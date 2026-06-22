from pydantic import BaseModel

class Dimensiones(BaseModel):
    alto: float
    ancho: float
    largo: float

class EquipajeInput(BaseModel):
    aerolinea: str
    dimensiones: Dimensiones
    peso: float

class BusquedaVueloInput(BaseModel):
    origen: str
    destino: str
    fecha_salida: str