from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    telefono: Optional[str] = None
    pais: Optional[str] = None
    region: Optional[str] = None

class UsuarioCrear(UsuarioBase):
    contrasena: str

class UsuarioRespuesta(UsuarioBase):
    rol: str
    estado: str

    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    correo: EmailStr
    contrasena: str

class Token(BaseModel):
    access_token: str
    token_type: str