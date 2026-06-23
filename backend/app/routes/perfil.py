from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from app.core.configuracion import config
from app.core.database import tabla_smartstop

import jwt
from jwt.exceptions import PyJWTError

router = APIRouter(prefix="/perfil", tags=["Perfil de Usuario y Preferencias"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# DEPENDENCIA: VALIDACIÓN DE TOKEN
def obtener_pk_usuario_actual(token: str = Depends(oauth2_scheme)) -> str:
    """
    Desencripta el token JWT enviado por el frontend.
    Retorna el PK del usuario (ej: USUARIO#1234) si el token es válido.
    """
    try:
        payload = jwt.decode(token, config.CLAVE_SECRETA_JWT, algorithms=[config.ALGORITMO_JWT])
        pk_usuario = payload.get("sub")
        if pk_usuario is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o corrupto")
        return pk_usuario
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token expirado o inválido, inicie sesión nuevamente"
        )

# SCHEMAS DE REQUEST / RESPONSE
class EquipajeFrecuenteRequest(BaseModel):
    alto: float = Field(..., description="Alto en centímetros", gt=0)
    ancho: float = Field(..., description="Ancho en centímetros", gt=0)
    largo: float = Field(..., description="Largo en centímetros", gt=0)
    peso: float = Field(..., description="Peso en kilogramos", gt=0)

# OBTENER DATOS DEL PERFIL
@router.get("/me")
def obtener_mi_perfil(pk_usuario: str = Depends(obtener_pk_usuario_actual)):
    """
    Retorna la información completa del usuario autenticado, 
    incluyendo sus medidas de equipaje guardadas.
    """
    try:
        respuesta = tabla_smartstop.get_item(
            Key={
                'PK': pk_usuario,
                'CO': 'PERFIL'
            }
        )
        
        if 'Item' not in respuesta:
            raise HTTPException(status_code=404, detail="Perfil no encontrado en la base de datos")
            
        usuario = respuesta['Item']
        datos_entidad = usuario.get('EntidadDatos_JSON', {})
        
        # Eliminamos el hash por seguridad antes de enviar al frontend
        if 'hash' in datos_entidad:
            del datos_entidad['hash']
            
        return {
            "id_usuario": pk_usuario.split('#')[1],
            "correo": usuario.get('GSI1_Correo'),
            "rol": usuario.get('RolSistema'),
            "datos_personales": datos_entidad,
            "equipaje_frecuente": usuario.get('Equipaje_JSON', None),
            "suscripcion": usuario.get('Suscripcion_JSON', None)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el perfil: {str(e)}")

# GUARDAR EQUIPAJE FRECUENTE
@router.put("/equipaje-frecuente")
def guardar_equipaje_frecuente(
    equipaje: EquipajeFrecuenteRequest, 
    pk_usuario: str = Depends(obtener_pk_usuario_actual)
):
    """
    Permite al viajero guardar o actualizar las dimensiones de su maleta 
    para autocompletar futuras búsquedas de stopover.
    """
    try:
        nuevo_equipaje = {
            "alto": equipaje.alto,
            "ancho": equipaje.ancho,
            "largo": equipaje.largo,
            "peso": equipaje.peso
        }
        
        tabla_smartstop.update_item(
            Key={
                'PK': pk_usuario,
                'CO': 'PERFIL'
            },
            UpdateExpression="SET Equipaje_JSON = :equipaje",
            ExpressionAttributeValues={
                ':equipaje': nuevo_equipaje
            }
        )
        
        return {
            "mensaje": "Dimensiones de equipaje guardadas correctamente",
            "equipaje_actual": nuevo_equipaje
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar equipaje: {str(e)}")

# ACTUALIZAR DATOS PERSONALES
@router.put("/datos")
def actualizar_datos_personales(
    telefono: str,
    pais: str,
    region: str,
    pk_usuario: str = Depends(obtener_pk_usuario_actual)
):
    """
    Actualiza la información de contacto y ubicación del viajero.
    """
    try:
        # Primero necesitamos obtener los datos actuales para no sobreescribir el hash ni el nombre
        respuesta = tabla_smartstop.get_item(Key={'PK': pk_usuario, 'CO': 'PERFIL'})
        if 'Item' not in respuesta:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        datos_actuales = respuesta['Item'].get('EntidadDatos_JSON', {})
        
        # Modificamos solo los campos permitidos
        datos_actuales['telefono'] = telefono
        datos_actuales['pais'] = pais
        datos_actuales['region'] = region
        
        # Guardamos en la base de datos
        tabla_smartstop.update_item(
            Key={'PK': pk_usuario, 'CO': 'PERFIL'},
            UpdateExpression="SET EntidadDatos_JSON = :datos",
            ExpressionAttributeValues={
                ':datos': datos_actuales
            }
        )
        
        # Limpiamos hash para la respuesta
        if 'hash' in datos_actuales:
            del datos_actuales['hash']
            
        return {
            "mensaje": "Datos actualizados exitosamente",
            "datos_actuales": datos_actuales
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))