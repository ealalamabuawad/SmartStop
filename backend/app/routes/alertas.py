from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr

import jwt
from jwt.exceptions import PyJWTError

from app.core.configuracion import config
from app.core.database import tabla_smartstop
from app.schemas.usuario import RolSistema

router = APIRouter(prefix="/alertas", tags=["Alertas y Suscripciones Premium"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def obtener_pk_usuario_actual(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, config.CLAVE_SECRETA_JWT, algorithms=[config.ALGORITMO_JWT])
        sub = payload.get("sub")
        if not isinstance(sub, str):
            raise HTTPException(status_code=401, detail="Token inválido: sujeto no válido")
        return sub
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

def verificar_admin(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, config.CLAVE_SECRETA_JWT, algorithms=[config.ALGORITMO_JWT])
        if payload.get("rol") != "Administrador":
            raise HTTPException(status_code=403, detail="Acceso denegado: Se requieren privilegios de Administrador")
        sub = payload.get("sub")
        if not isinstance(sub, str):
            raise HTTPException(status_code=401, detail="Token inválido: sujeto no válido")
        return sub
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


class SuscripcionRequest(BaseModel):
    metodo_pago: str = Field(..., examples=["TC_Terminada_4498"])

class NotificacionReglaRequest(BaseModel):
    codigo_aerolinea: str = Field(..., examples=["LATAM"])
    cambio_detalle: str = Field(..., examples=["Reducción de equipaje de mano a 40x30x20 cm"])

# ACTIVAR SUSCRIPCIÓN PREMIUM (Usuario Final)
@router.post("/suscribir")
def activar_premium(req: SuscripcionRequest, pk_usuario: str = Depends(obtener_pk_usuario_actual)):
    """
    Actualiza el perfil del viajero al rol Premium y activa su suscripción 
    para recibir notificaciones de equipaje en tiempo real.
    """
    try:
        # Calcular fecha de renovación (30 días)
        fecha_renovacion = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        suscripcion_info = {
            "estado": "Activa",
            "renovacion": fecha_renovacion,
            "metodo": req.metodo_pago
        }

        tabla_smartstop.update_item(
            Key={'PK': pk_usuario, 'CO': 'PERFIL'},
            UpdateExpression="SET RolSistema = :rol, Suscripcion_JSON = :suscripcion",
            ExpressionAttributeValues={
                ':rol': RolSistema.VIAJERO_PREMIUM.value,
                ':suscripcion': suscripcion_info
            }
        )
        return {
            "mensaje": "Suscripción Premium activada exitosamente", 
            "detalles": suscripcion_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar suscripción: {str(e)}")

# DISPARADOR DE ALERTAS AUTOMATIZADO (ADMIN)
@router.post("/admin/notificar-cambios")
def disparar_alertas_premium(req: NotificacionReglaRequest, admin_id: str = Depends(verificar_admin)):
    """
    Webhook interno para el Administrador. 
    Escanea la base de datos en busca de usuarios Premium y despacha correos/push 
    cuando una aerolínea cambia sus reglas (HU06).
    """
    try:
        respuesta = tabla_smartstop.scan(
            FilterExpression=Attr('RolSistema').eq(RolSistema.VIAJERO_PREMIUM.value) & Key('CO').eq('PERFIL')
        )
        
        usuarios_premium = respuesta.get('Items', [])
        correos_notificados = []

        for usuario in usuarios_premium:
            correo = usuario.get('GSI1_Correo')
            
            print(f"\n--- ENVIANDO ALERTA PUSH/EMAIL A: {correo} ---")
            print(f"¡Atención! La aerolínea {req.codigo_aerolinea} ha actualizado sus reglas contractuales:")
            print(f"Detalle: {req.cambio_detalle}")
            print("Verifica tu itinerario en SmartStop para evitar sobrecostos en el aeropuerto.")
            print("------------------------------------------------\n")
            
            correos_notificados.append(correo)

        return {
            "mensaje": "Alertas despachadas exitosamente a la base Premium",
            "total_notificados": len(correos_notificados),
            "usuarios_contactados": correos_notificados
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al despachar alertas: {str(e)}")