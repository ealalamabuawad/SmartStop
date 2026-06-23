import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from boto3.dynamodb.conditions import Key

from app.core.configuracion import config
from app.core.database import tabla_smartstop
from app.schemas.resultados import ItinerarioOptimizadoResponse

import jwt
from jwt.exceptions import PyJWKError

router = APIRouter(prefix="/itinerarios", tags=["Gestión y Exportación de Itinerarios"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# DEPENDENCIA: VALIDACIÓN DE TOKEN
def obtener_pk_usuario_actual(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, config.CLAVE_SECRETA_JWT, algorithms=[config.ALGORITMO_JWT])
        pk_usuario = payload.get("sub")
        if not pk_usuario:
            raise HTTPException(status_code=401, detail="Token inválido")
        return pk_usuario
    except PyJWKError:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")

class GuardarItinerarioRequest(BaseModel):
    itinerario: ItinerarioOptimizadoResponse

# GUARDAR ITINERARIO FAVORITO
@router.post("/guardar", status_code=status.HTTP_201_CREATED)
def guardar_itinerario(req: GuardarItinerarioRequest, pk_usuario: str = Depends(obtener_pk_usuario_actual)):
    """
    Guarda una ruta optimizada en el perfil del usuario para acceso offline o revisión futura.
    Utiliza el diseño de Tabla Única anidando bajo el PK del usuario.
    """
    try:
        id_itinerario = str(uuid.uuid4())[:8]
        fecha_guardado = datetime.utcnow().isoformat()
        co_itinerario = f"ITINERARIO#{req.itinerario.codigo_ruta}#{id_itinerario}"

        nuevo_item = {
            'PK': pk_usuario,
            'CO': co_itinerario,
            'FechaGuardado': fecha_guardado,
            'EntidadDatos_JSON': req.itinerario.model_dump()
        }

        tabla_smartstop.put_item(Item=nuevo_item)
        
        return {
            "mensaje": "Itinerario guardado exitosamente",
            "id_itinerario": id_itinerario
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el itinerario: {str(e)}")

# LISTAR ITINERARIOS GUARDADOS
@router.get("/", response_model=List[dict])
def listar_mis_itinerarios(pk_usuario: str = Depends(obtener_pk_usuario_actual)):
    """
    Recupera todos los viajes guardados por el usuario mediante una consulta (Query) eficiente.
    """
    try:
        respuesta = tabla_smartstop.query(
            KeyConditionExpression=Key('PK').eq(pk_usuario) & Key('CO').begins_with('ITINERARIO#')
        )
        
        resultados = []
        for item in respuesta.get('Items', []):
            resultados.append({
                "id_itinerario": item['CO'].split('#')[2],
                "codigo_ruta": item['CO'].split('#')[1],
                "fecha_guardado": item.get('FechaGuardado'),
                "detalle": item.get('EntidadDatos_JSON')
            })
            
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# EXPORTAR A CALENDARIO 
@router.get("/{id_itinerario}/exportar/calendario")
def exportar_calendario(id_itinerario: str, pk_usuario: str = Depends(obtener_pk_usuario_actual)):
    """
    Genera un archivo .ics al vuelo para integrar los tramos de vuelo con 
    Google Calendar, Apple Calendar o Outlook (Cumplimiento HU08).
    """
    try:
        respuesta = tabla_smartstop.query(
            KeyConditionExpression=Key('PK').eq(pk_usuario) & Key('CO').begins_with('ITINERARIO#')
        )
        
        itinerario_db = next((item for item in respuesta.get('Items', []) if id_itinerario in item['CO']), None)
        
        if not itinerario_db:
            raise HTTPException(status_code=404, detail="Itinerario no encontrado")

        datos = itinerario_db['EntidadDatos_JSON']
        tramos = datos.get('tramos', [])
        
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//SmartStop//TravelTech API//ES",
            "CALSCALE:GREGORIAN"
        ]
        
        for tramo in tramos:
            dt_start = tramo['fecha_salida'].replace("-", "").replace(":", "").split(".")[0] + "Z"
            dt_end = tramo['fecha_llegada'].replace("-", "").replace(":", "").split(".")[0] + "Z"
            
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"DTSTART:{dt_start}",
                f"DTEND:{dt_end}",
                f"SUMMARY:Vuelo {tramo['aerolinea']} {tramo['numero_vuelo']} ({tramo['origen']} - {tramo['destino']})",
                f"DESCRIPTION:Reserva gestionada via SmartStop. Revisa las reglas de equipaje en la app.",
                f"LOCATION:Aeropuerto {tramo['origen']}",
                "END:VEVENT"
            ])
            
        ics_lines.append("END:VCALENDAR")
        ics_content = "\n".join(ics_lines)
        
        # Retornar como archivo descargable
        return Response(
            content=ics_content,
            media_type="text/calendar",
            headers={"Content-Disposition": f"attachment; filename=itinerario_{id_itinerario}.ics"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ELIMINAR ITINERARIO
@router.delete("/{id_itinerario}")
def eliminar_itinerario(id_itinerario: str, pk_usuario: str = Depends(obtener_pk_usuario_actual)):
    """
    Permite al usuario limpiar su historial de viajes guardados.
    """
    try:
        respuesta = tabla_smartstop.query(
            KeyConditionExpression=Key('PK').eq(pk_usuario) & Key('CO').begins_with('ITINERARIO#')
        )
        
        itinerario_db = next((item for item in respuesta.get('Items', []) if id_itinerario in item['CO']), None)
        
        if not itinerario_db:
            raise HTTPException(status_code=404, detail="Itinerario no encontrado")
            
        tabla_smartstop.delete_item(
            Key={
                'PK': pk_usuario,
                'CO': itinerario_db['CO']
            }
        )
        return {"mensaje": "Itinerario eliminado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))