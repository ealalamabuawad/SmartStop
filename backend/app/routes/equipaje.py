from fastapi import APIRouter, HTTPException
from app.schemas.vuelos_equipaje import EquipajeInput
# importaremos la conexión a dynamo cuando la configuremos bien
# from app.core.database import tabla_smartstop 

router = APIRouter(prefix="/equipaje", tags=["Validador de Equipaje"])

@router.post("/validar")
async def validar_equipaje(datos: EquipajeInput):
    try:
        # LÓGICA TEMPORAL PARA CONECTAR CON VUE AHORA:
        if datos.peso > 10:
            return {
                "estado": "error",
                "mensaje": "Las dimensiones o el peso superan el contrato de transporte de la aerolínea seleccionada.",
                "multaEstimada": 45000
            }
        return {
            "estado": "exito",
            "mensaje": "Tu maleta cumple con las resoluciones de la IATA. Viajas sin sorpresas."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))