from pydantic import BaseModel
from typing import Optional

class AnalisisEquipaje(BaseModel):
    cumple_normativa: bool
    sobrepeso_kg: float = 0.0
    exceso_dimensiones: bool = False
    
class AlertaMulta(BaseModel):
    estatus: str
    mensaje_preventivo: str
    multa_estimada_clp: float
    analisis_tecnico: AnalisisEquipaje