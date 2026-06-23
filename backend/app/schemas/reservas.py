from pydantic import BaseModel, Field
from typing import Optional

class ReservaBase(BaseModel):
    codigo_reserva: str
    id_usuario: str
    codigo_ruta: str
    fecha_reserva: str
    estado_pago: str