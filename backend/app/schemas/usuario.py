from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from enum import Enum

class RolSistema(str, Enum):
    VIAJERO_COMUN = "Viajero_Comun"
    VIAJERO_PREMIUM = "Viajero_Premium"
    ADMINISTRADOR = "Administrador"

class EventoAuditoria(BaseModel):
    accion: str
    fecha: str
    ip: Optional[str] = None

class DatosUsuario(BaseModel):
    nombre: str
    telefono: str
    pais: str
    region: str
    hash: str

class SuscripcionInfo(BaseModel):
    estado: str
    renovacion: str
    metodo: str

class UsuarioDB(BaseModel):
    PK: str = Field(..., examples=["USUARIO#101"])
    CO: str = Field("PERFIL")
    GSI1_Correo: EmailStr
    RolSistema: RolSistema
    EntidadDatos_JSON: DatosUsuario
    Suscripcion_JSON: Optional[SuscripcionInfo] = None
    Auditoria_JSON: List[EventoAuditoria] = []
    TTL: Optional[int] = None