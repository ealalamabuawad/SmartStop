from pydantic import BaseModel, Field
from typing import Optional

class DatosAeropuerto(BaseModel):
    nombre: str
    pais: str
    tasas_embarque_clp: int

class AeropuertoDB(BaseModel):
    PK: str = Field(..., examples=["AEROPUERTO#SCL"])
    CO: str = Field("METADATOS")
    EntidadDatos_JSON: DatosAeropuerto
    TTL: Optional[int] = None