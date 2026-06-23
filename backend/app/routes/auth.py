import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from boto3.dynamodb.conditions import Key
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

import jwt
from jwt.exceptions import PyJWTError

from app.core.configuracion import config
from app.core.database import tabla_smartstop
from app.schemas.usuario import RolSistema, UsuarioDB, DatosUsuario, EventoAuditoria

router = APIRouter(prefix="/auth", tags=["Autenticación y Usuarios"])

# --- CONFIGURACIÓN DE SEGURIDAD
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verificar_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def obtener_password_hash(password):
    return pwd_context.hash(password)

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=config.EXPIRACION_TOKEN_MINUTOS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.CLAVE_SECRETA_JWT, algorithm=config.ALGORITMO_JWT)

class RegistroRequest(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    telefono: str
    pais: str
    region: str

class RecuperarPasswordRequest(BaseModel):
    correo: EmailStr

class ResetPasswordRequest(BaseModel):
    correo: EmailStr
    token_recuperacion: str
    nueva_password: str

class EdicionAdminRequest(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    rol: Optional[RolSistema] = None

# 1. REGISTRO DE USUARIO 
@router.post("/registro", response_model=dict, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: RegistroRequest):
    # Verificar si el correo ya existe usando el GSI
    respuesta_gsi = tabla_smartstop.query(
        IndexName='GSI1-Correo-Index',
        KeyConditionExpression=Key('GSI1_Correo').eq(usuario.correo)
    )
    if respuesta_gsi.get('Items'):
        raise HTTPException(status_code=400, detail="El correo ya está registrado en SmartStop.")

    # Generar ID y Hash
    id_usuario = str(uuid.uuid4())
    pk_usuario = f"USUARIO#{id_usuario}"
    hashed_pwd = obtener_password_hash(usuario.password)
    fecha_actual = datetime.utcnow().isoformat()

    # Construir el Item
    nuevo_usuario = {
        'PK': pk_usuario,
        'CO': 'PERFIL',
        'GSI1_Correo': usuario.correo,
        'RolSistema': RolSistema.VIAJERO_COMUN.value,
        'EntidadDatos_JSON': {
            'nombre': usuario.nombre,
            'telefono': usuario.telefono,
            'pais': usuario.pais,
            'region': usuario.region,
            'hash': hashed_pwd
        },
        'Auditoria_JSON': [
            {'accion': 'Registro Web', 'fecha': fecha_actual, 'ip': '127.0.0.1'}
        ]
    }

    # Insertar en DynamoDB
    tabla_smartstop.put_item(Item=nuevo_usuario)
    return {"mensaje": "Usuario registrado exitosamente", "id_usuario": id_usuario}


# 2. LOGIN
@router.post("/login")
def login_usuario(form_data: OAuth2PasswordRequestForm = Depends()):
    # Buscar usuario por correo en el GSI
    respuesta = tabla_smartstop.query(
        IndexName='GSI1-Correo-Index',
        KeyConditionExpression=Key('GSI1_Correo').eq(form_data.username)
    )
    items = respuesta.get('Items', [])
    if not items:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    
    usuario_db = items[0]
    hash_guardado = usuario_db['EntidadDatos_JSON']['hash']

    # Verificar contraseña
    if not verificar_password(form_data.password, hash_guardado):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    # Generar JWT
    token = crear_token_acceso(data={
        "sub": usuario_db['PK'], 
        "rol": usuario_db['RolSistema'],
        "correo": usuario_db['GSI1_Correo']
    })

    # Generar Log
    auditoria = usuario_db.get('Auditoria_JSON', [])
    auditoria.append({'accion': 'Login Exitoso', 'fecha': datetime.utcnow().isoformat()})
    tabla_smartstop.update_item(
        Key={'PK': usuario_db['PK'], 'CO': 'PERFIL'},
        UpdateExpression="SET Auditoria_JSON = :aud",
        ExpressionAttributeValues={':aud': auditoria}
    )

    return {"access_token": token, "token_type": "bearer", "rol": usuario_db['RolSistema']}


# 3. RESTABLECER CONTRASEÑA
@router.post("/recuperar-password")
def solicitar_recuperacion(req: RecuperarPasswordRequest):
    respuesta = tabla_smartstop.query(
        IndexName='GSI1-Correo-Index',
        KeyConditionExpression=Key('GSI1_Correo').eq(req.correo)
    )
    if not respuesta.get('Items'):
        return {"mensaje": "Si el correo existe, se han enviado las instrucciones."}
    
    token_temporal = crear_token_acceso(data={"sub": req.correo}, expires_delta=timedelta(minutes=15))
    print(f"--- SIMULACIÓN DE CORREO A {req.correo} ---")
    print(f"Tu token de recuperación es: {token_temporal}")
    print("------------------------------------------")

    return {"mensaje": "Si el correo existe, se han enviado las instrucciones (Revisa la consola del backend)."}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest):
    try:
        # Validar token
        payload = jwt.decode(req.token_recuperacion, config.CLAVE_SECRETA_JWT, algorithms=[config.ALGORITMO_JWT])
        correo_token = payload.get("sub")
        if correo_token != req.correo:
            raise HTTPException(status_code=400, detail="Token inválido para este correo")
    except PyJWTError:
        raise HTTPException(status_code=400, detail="Token expirado o inválido")

    # Buscar usuario
    respuesta = tabla_smartstop.query(
        IndexName='GSI1-Correo-Index',
        KeyConditionExpression=Key('GSI1_Correo').eq(req.correo)
    )
    if not respuesta.get('Items'):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_db = respuesta['Items'][0]
    
    # Actualizar Hash
    nuevo_hash = obtener_password_hash(req.nueva_password)
    usuario_db['EntidadDatos_JSON']['hash'] = nuevo_hash

    tabla_smartstop.update_item(
        Key={'PK': usuario_db['PK'], 'CO': 'PERFIL'},
        UpdateExpression="SET EntidadDatos_JSON = :datos",
        ExpressionAttributeValues={':datos': usuario_db['EntidadDatos_JSON']}
    )
    return {"mensaje": "Contraseña actualizada correctamente"}


# 4. ADMINISTRACIÓN (Ver, Editar, Eliminar)
@router.get("/admin/usuarios")
def admin_listar_usuarios(): 
    # filtramos solo los items que tengan CO = 'PERFIL'
    respuesta = tabla_smartstop.scan(
        FilterExpression=Key('CO').eq('PERFIL')
    )
    usuarios = respuesta.get('Items', [])
    # Limpiamos el hash antes de enviarlo al frontend
    for u in usuarios:
        if 'hash' in u.get('EntidadDatos_JSON', {}):
            del u['EntidadDatos_JSON']['hash']
    return {"total": len(usuarios), "usuarios": usuarios}

@router.put("/admin/usuarios/{id_usuario}")
def admin_editar_usuario(id_usuario: str, req: EdicionAdminRequest):
    pk = f"USUARIO#{id_usuario}"
    
    # Obtener usuario actual
    respuesta = tabla_smartstop.get_item(Key={'PK': pk, 'CO': 'PERFIL'})
    if 'Item' not in respuesta:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario = respuesta['Item']
    
    # Actualizar campos
    if req.nombre:
        usuario['EntidadDatos_JSON']['nombre'] = req.nombre
    if req.telefono:
        usuario['EntidadDatos_JSON']['telefono'] = req.telefono
    if req.rol:
        usuario['RolSistema'] = req.rol.value

    # Guardar cambios
    tabla_smartstop.put_item(Item=usuario)
    return {"mensaje": "Usuario actualizado", "datos": usuario['EntidadDatos_JSON']}

@router.delete("/admin/usuarios/{id_usuario}")
def admin_eliminar_usuario(id_usuario: str):
    pk = f"USUARIO#{id_usuario}"
    try:
        tabla_smartstop.delete_item(
            Key={
                'PK': pk,
                'CO': 'PERFIL'
            }
        )
        return {"mensaje": f"Usuario {id_usuario} eliminado permanentemente del sistema"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))