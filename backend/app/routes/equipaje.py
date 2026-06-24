from fastapi import APIRouter, HTTPException
from app.core.database import tabla_smartstop
from app.schemas.equipaje import ValidacionEquipajeRequest

router = APIRouter(prefix="/equipaje", tags=["Validación de Equipaje"])

@router.post("/validar")
def validar_maleta(req: ValidacionEquipajeRequest):
    pk_aerolinea = f"AEROLINEA#{req.codigo_aerolinea.upper()}"
    
    try:
        respuesta = tabla_smartstop.get_item(Key={'PK': pk_aerolinea, 'CO': 'REGLAS_EQUIPAJE'})
        if 'Item' not in respuesta:
            raise HTTPException(status_code=404, detail="Reglas de aerolínea no encontradas para validar")
        
        datos_regla = respuesta['Item']['EntidadDatos_JSON']
        dimensiones_mano_str = datos_regla['mano'] 
        limite_peso_mano = datos_regla.get('mano_kg', 10) 
        limite_peso_bodega = datos_regla['bodega_kg']
        
        limites_dim = sorted([float(x) for x in dimensiones_mano_str.split('x')], reverse=True)
        maleta_usuario = sorted([req.alto, req.ancho, req.largo], reverse=True)
        
        cumple_dimensiones_mano = all(u <= l for u, l in zip(maleta_usuario, limites_dim))
        cumple_peso_mano = req.peso <= limite_peso_mano
        cumple_peso_bodega = req.peso <= limite_peso_bodega
        
        es_valida_cabina = cumple_dimensiones_mano and cumple_peso_mano
        requiere_bodega = not es_valida_cabina and cumple_peso_bodega
        
        if es_valida_cabina:
            estado = "APROBADO_MANO"
            mensaje = "Tu maleta cumple con las medidas y el peso para ir en cabina sin costo extra."
        elif requiere_bodega:
            estado = "REQUIERE_BODEGA"
            if not cumple_dimensiones_mano:
                mensaje = "Tu maleta excede las dimensiones de mano, pero cumple para ir en bodega. Revisa los costos."
            else:
                mensaje = f"Tu maleta cumple las medidas, pero excede el peso de cabina ({limite_peso_mano}kg). Tendrá que ir en bodega."
        else:
            estado = "RECHAZADO_EXCESO"
            mensaje = "Tu maleta excede tanto las dimensiones de mano como el peso máximo de bodega permitido."

        return {
            "aerolinea": req.codigo_aerolinea.upper(),
            "estado_validacion": estado,
            "mensaje": mensaje,
            "detalles": {
                "tus_medidas": f"{req.alto}x{req.ancho}x{req.largo} con {req.peso}kg",
                "limite_mano_aerolinea": f"{dimensiones_mano_str} hasta {limite_peso_mano}kg",
                "limite_peso_bodega": f"{limite_peso_bodega}kg"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))