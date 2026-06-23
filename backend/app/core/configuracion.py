from pydantic_settings import BaseSettings

class Configuracion(BaseSettings):
    NOMBRE_PROYECTO: str = "SmartStop Core API"
    VERSION: str = "1.0.0"
    
    CLAVE_SECRETA_JWT: str = "CLAVE_DESAROLLO_123456"
    ALGORITMO_JWT: str = "HS256"
    EXPIRACION_TOKEN_MINUTOS: int = 120
    
    AWS_ACCESS_KEY_ID: str = "dummy"
    AWS_SECRET_ACCESS_KEY: str = "dummy"
    AWS_REGION: str = "us-east-1"
    DYNAMODB_ENDPOINT: str = "http://127.0.0.1:8000"
    DYNAMODB_TABLA: str = "SmartStopTable"
    
    DUFFEL_API_KEY: str = ""
    DUFFEL_API_URL: str = "https://api.duffel.com/air"
    
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

config = Configuracion()