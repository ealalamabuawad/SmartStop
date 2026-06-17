from pydantic import BaseModel, Field
from typing import List, Optional

class SolicitudBusqueda(BaseModel):
    origen: str = Field(min_length=3, max_length=3)
    destino: str = Field(min_length=3, max_length=3)
    fecha_salida: str
    fecha_retorno: Optional[str] = None

class TramoVuelo(BaseModel):
    codigo_vuelo: str
    aerolinea_id: str
    origen: str
    destino: str
    salida: str
    llegada: str

class ItinerarioStopover(BaseModel):
    id_ruta: str
    vuelos: List[TramoVuelo]
    horas_stopover: float = Field(ge=24, le=72)
    costo_vuelo_clp: float