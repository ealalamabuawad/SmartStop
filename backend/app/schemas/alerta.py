from pydantic import BaseModel, Field
from typing import Optional

class SuscripcionInfo(BaseModel):
    estado: str
    renovacion: str
    metodo: str

class AlertaPremiumBase(BaseModel):
    id_usuario: str
    mensaje: str
    fecha_envio: str
    tipo_notificacion: str  # push, email