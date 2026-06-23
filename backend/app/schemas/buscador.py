from typing import Optional
from pydantic import BaseModel

class BusquedaItinerarioRequest(BaseModel):
    trip_type: str
    origen_iata: str
    destino_iata: str
    fecha_salida: str
    fecha_regreso: Optional[str] = None
    passengers: int
    cabin_class: str
    cabin_bag: int = 0
    checked_bag: int = 0
    equipaje_alto: int = 0
    equipaje_ancho: int = 0
    equipaje_largo: int = 0
    equipaje_peso: int = 0