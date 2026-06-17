from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.configuracion import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def obtener_hash_contrasena(contrasena: str) -> str:
    return pwd_context.hash(contrasena)

def verificar_contrasena(contrasena_plana: str, contrasena_hash: str) -> bool:
    return pwd_context.verify(contrasena_plana, contrasena_hash)

def crear_token_acceso(datos: dict, expira_delta: Optional[timedelta] = None) -> str:
    datos_codificar = datos.copy()
    
    if expira_delta:
        expira = datetime.utcnow() + expira_delta
    else:
        expira = datetime.utcnow() + timedelta(minutes=config.EXPIRACION_TOKEN_MINUTOS)
        
    datos_codificar.update({"exp": expira})
    
    token_jwt = jwt.encode(
        datos_codificar, 
        config.CLAVE_SECRETA_JWT, 
        algorithm=config.ALGORITMO_JWT
    )
    
    return token_jwt