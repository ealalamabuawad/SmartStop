from pydantic import BaseModel, Field
from typing import List, Optional

class DatosRuta(BaseModel):
    vuelos: List[str] = Field(..., examples=[["LA704", "IB3402"]])
    costo_clp: int

class RutaDB(BaseModel):
    PK: str = Field(..., examples=["RUTA#SCL_MAD_CDG"])
    CO: str = Field(..., examples=["STOPOVER#48H"])
    EntidadDatos_JSON: DatosRuta
    TTL: int