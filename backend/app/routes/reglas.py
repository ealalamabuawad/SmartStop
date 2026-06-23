from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel, Field
from boto3.dynamodb.conditions import Key

from app.core.configuracion import config
from app.core.database import tabla_smartstop
from app.schemas.equipaje import DatosAerolinea

import jwt
from jwt.exceptions import PyJWTError

router = APIRouter(prefix="/admin/reglas", tags=["Gestión de Reglas IATA"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verificar_admin(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, config.CLAVE_SECRETA_JWT, algorithms=[config.ALGORITMO_JWT])
        rol = payload.get("rol")
        if rol != "Administrador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Acceso denegado: Se requieren privilegios de Administrador"
            )
        return payload.get("sub")
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token inválido o expirado"
        )

class ReglaAerolineaRequest(BaseModel):
    codigo_iata: str = Field(..., min_length=2, max_length=3)
    mano: str
    bodega_kg: int

@router.get("/", response_model=List[dict])
def listar_reglas(admin_id: str = Depends(verificar_admin)):
    try:
        respuesta = tabla_smartstop.scan(
            FilterExpression=Key('CO').eq('REGLAS_EQUIPAJE')
        )
        resultados = []
        for item in respuesta.get('Items', []):
            codigo = item['PK'].split('#')[1]
            datos = item.get('EntidadDatos_JSON', {})
            resultados.append({
                "codigo_iata": codigo,
                "mano": datos.get('mano'),
                "bodega_kg": datos.get('bodega_kg')
            })
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_regla(req: ReglaAerolineaRequest, admin_id: str = Depends(verificar_admin)):
    pk_aerolinea = f"AEROLINEA#{req.codigo_iata.upper()}"
    
    try:
        respuesta_existencia = tabla_smartstop.get_item(Key={'PK': pk_aerolinea, 'CO': 'REGLAS_EQUIPAJE'})
        if 'Item' in respuesta_existencia:
            raise HTTPException(status_code=400, detail="La aerolínea ya tiene reglas registradas")

        nueva_regla = {
            'PK': pk_aerolinea,
            'CO': 'REGLAS_EQUIPAJE',
            'EntidadDatos_JSON': {
                'mano': req.mano,
                'bodega_kg': req.bodega_kg
            }
        }
        
        tabla_smartstop.put_item(Item=nueva_regla)
        return {"mensaje": f"Reglas creadas exitosamente para {req.codigo_iata.upper()}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{codigo_iata}")
def actualizar_regla(codigo_iata: str, req: DatosAerolinea, admin_id: str = Depends(verificar_admin)):
    pk_aerolinea = f"AEROLINEA#{codigo_iata.upper()}"
    
    try:
        respuesta = tabla_smartstop.get_item(Key={'PK': pk_aerolinea, 'CO': 'REGLAS_EQUIPAJE'})
        if 'Item' not in respuesta:
            raise HTTPException(status_code=404, detail="Aerolínea no encontrada")

        tabla_smartstop.update_item(
            Key={'PK': pk_aerolinea, 'CO': 'REGLAS_EQUIPAJE'},
            UpdateExpression="SET EntidadDatos_JSON = :datos",
            ExpressionAttributeValues={
                ':datos': {
                    'mano': req.mano,
                    'bodega_kg': req.bodega_kg
                }
            }
        )
        return {"mensaje": f"Reglas actualizadas para {codigo_iata.upper()}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{codigo_iata}")
def eliminar_regla(codigo_iata: str, admin_id: str = Depends(verificar_admin)):
    pk_aerolinea = f"AEROLINEA#{codigo_iata.upper()}"
    
    try:
        tabla_smartstop.delete_item(
            Key={
                'PK': pk_aerolinea,
                'CO': 'REGLAS_EQUIPAJE'
            }
        )
        return {"mensaje": f"Reglas eliminadas para la aerolínea {codigo_iata.upper()}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))