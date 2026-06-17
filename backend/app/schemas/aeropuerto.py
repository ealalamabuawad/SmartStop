from pydantic import BaseModel

class AeropuertoBase(BaseModel):
    codigo_iata: str
    nombre: str
    pais: str
    tasas_embarque_clp: float

class AeropuertoRespuesta(AeropuertoBase):
    class Config:
        from_attributes = True