import uuid
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from boto3.dynamodb.conditions import Key

from app.core.configuracion import config
from app.core.database import tabla_smartstop
from app.core.seguridad import obtener_hash_contrasena, verificar_contrasena, crear_token_acceso
from app.schemas.usuario import UsuarioCrear, UsuarioRespuesta, UsuarioLogin, Token

router = APIRouter()

def enviar_correo_smtp(destinatario: str, asunto: str, cuerpo: str):
    mensaje = MIMEMultipart()
    mensaje["From"] = config.SMTP_USER
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "plain"))
    
    try:
        servidor = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT)
        servidor.starttls()
        servidor.login(config.SMTP_USER, config.SMTP_PASSWORD)
        servidor.send_message(mensaje)
        servidor.quit()
    except Exception as e:
        print(f"Error SMTP: {e}")

def buscar_usuario_por_correo(correo: str):
    respuesta = tabla_smartstop.query(
        IndexName='GSI1-Correo-Index',
        KeyConditionExpression=Key('GSI1_Correo').eq(correo)
    )
    items = respuesta.get('Items', [])
    return items[0] if items else None

@router.post("/registro", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: UsuarioCrear, background_tasks: BackgroundTasks):
    if buscar_usuario_por_correo(usuario.correo):
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    id_usuario = str(uuid.uuid4())
    fecha_actual = datetime.utcnow().isoformat()
    
    nuevo_usuario = {
        'PK': f'USUARIO#{id_usuario}',
        'CO': 'PERFIL',
        'GSI1_Correo': usuario.correo,
        'RolSistema': 'Viajero_Comun',
        'EntidadDatos_JSON': {
            'nombre': usuario.nombre,
            'telefono': usuario.telefono,
            'pais': usuario.pais,
            'region': usuario.region,
            'hash': obtener_hash_contrasena(usuario.contrasena)
        },
        'Auditoria_JSON': [
            {'accion': 'Registro', 'fecha': fecha_actual}
        ]
    }
    
    tabla_smartstop.put_item(Item=nuevo_usuario)
    
    cuerpo_correo = f"Hola {usuario.nombre}, bienvenido a SmartStop. Tu cuenta ha sido creada con éxito."
    background_tasks.add_task(enviar_correo_smtp, usuario.correo, "Bienvenido a SmartStop", cuerpo_correo)
    
    return UsuarioRespuesta(
        nombre=usuario.nombre,
        correo=usuario.correo,
        telefono=usuario.telefono,
        pais=usuario.pais,
        region=usuario.region,
        rol='Viajero_Comun',
        estado='Activo'
    )

@router.post("/login", response_model=Token)
async def login(credenciales: UsuarioLogin):
    usuario_db = buscar_usuario_por_correo(credenciales.correo)
    
    if not usuario_db:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
    hash_guardado = usuario_db.get('EntidadDatos_JSON', {}).get('hash', '') # type: ignore
    
    if not verificar_contrasena(credenciales.contrasena, hash_guardado):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
    token = crear_token_acceso(
        datos={"sub": credenciales.correo, "rol": usuario_db.get('RolSistema')}
    )
    
    return {"access_token": token, "token_type": "bearer"}

@router.post("/recuperar-contrasena")
async def reestablecer_contrasena(correo: str, background_tasks: BackgroundTasks):
    usuario_db = buscar_usuario_por_correo(correo)
    
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    nueva_contrasena = str(uuid.uuid4())[:8]
    nuevo_hash = obtener_hash_contrasena(nueva_contrasena)
    
    entidad_datos = usuario_db.get('EntidadDatos_JSON', {})  
    entidad_datos['hash'] = nuevo_hash # type: ignore
    
    tabla_smartstop.update_item(
        Key={
            'PK': usuario_db['PK'],
            'CO': usuario_db['CO']
        },
        UpdateExpression="SET EntidadDatos_JSON = :ed, Auditoria_JSON = list_append(Auditoria_JSON, :aud)",
        ExpressionAttributeValues={
            ':ed': entidad_datos,
            ':aud': [{'accion': 'Recuperacion_Contrasena', 'fecha': datetime.utcnow().isoformat()}]
        }
    )
    
    cuerpo_correo = f"Tu nueva contraseña temporal es: {nueva_contrasena}\nPor favor, inicia sesión y cámbiala lo antes posible."
    background_tasks.add_task(enviar_correo_smtp, correo, "Recuperación de Contraseña", cuerpo_correo)
    
    return {"mensaje": "Se enviaron las instrucciones a tu correo electrónico"}