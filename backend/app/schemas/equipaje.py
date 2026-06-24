from pydantic import BaseModel, Field
from typing import Optional

class DatosAerolinea(BaseModel):
    mano: str = Field(..., examples=["55x35x25"])
    mano_kg: int = Field(..., examples=[10]) # <- Agregamos el límite de peso en cabina
    bodega_kg: int

class AerolineaDB(BaseModel):
    PK: str = Field(..., examples=["AEROLINEA#LATAM"])
    CO: str = Field("REGLAS_EQUIPAJE")
    EntidadDatos_JSON: DatosAerolinea
    TTL: Optional[int] = None

class ValidacionEquipajeRequest(BaseModel):
    alto: float
    ancho: float
    largo: float
    peso: float
    codigo_aerolinea: str