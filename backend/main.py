from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.configuracion import config

app = FastAPI(
    title=config.NOMBRE_PROYECTO,
    version=config.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def raiz():
    return {
        "estado": "operativo", 
        "proyecto": config.NOMBRE_PROYECTO
    }