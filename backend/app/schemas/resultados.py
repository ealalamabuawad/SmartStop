from typing import List, Optional
from pydantic import BaseModel

class TrayectoVista(BaseModel):
    aerolinea: str
    aerolinea_nombre: str
    origen: str
    destino: str
    fecha_salida: str
    hora_salida: str
    fecha_llegada: str
    hora_llegada: str
    duracion_formato: str
    es_directo: bool
    info_escalas: str
    tipo_avion: str

class ItinerarioOptimizadoResponse(BaseModel):
    codigo_ruta: str
    offer_id: str
    aerolinea_owner: str
    precio_vuelo_clp: int
    cumple_equipaje: bool
    multa_estimada_clp: int
    duracion_total_formato: str
    es_stopover: bool = False
    stopover_city: Optional[str] = None
    stopover_hours: int = 0
    trayectos: List[TrayectoVista]