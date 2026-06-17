from pydantic import BaseModel, Field

class Dimensiones(BaseModel):
    alto_cm: float = Field(gt=0)
    ancho_cm: float = Field(gt=0)
    largo_cm: float = Field(gt=0)

class EquipajeValidar(BaseModel):
    dimensiones: Dimensiones
    peso_kg: float = Field(gt=0)
    aerolinea_id: str

class ReglaAerolinea(BaseModel):
    aerolinea_id: str
    dimensiones_mano_maximas: str
    peso_bodega_maximo_kg: float