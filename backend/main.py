from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.configuracion import config
from app.routes import auth, buscador, perfil, reglas, alertas, itinerarios
from app.routes import equipaje#, vuelos , auth

tags_metadata = [
    {
        "name": "Autenticación y Usuarios",
        "description": "Gestión de acceso, credenciales JWT y roles de sistema."
    },
    {
        "name": "Buscador y Orquestación",
        "description": "Orquestación asíncrona de GDS, stopovers y validación de equipaje."
    },
    {
        "name": "Perfil de Usuario y Preferencias",
        "description": "Gestión de datos del viajero y medidas frecuentes de equipaje."
    },
    {
        "name": "Gestión de Reglas IATA",
        "description": "Panel administrativo para el control de restricciones aeroportuarias."
    },
    {
        "name": "Alertas y Suscripciones Premium",
        "description": "Gestión de conversiones y disparadores de notificaciones preventivas."
    },
    {
        "name": "Gestión y Exportación de Itinerarios",
        "description": "Almacenamiento de rutas offline y exportación nativa a calendarios (.ics)."
    }
]

app = FastAPI(
    title=config.NOMBRE_PROYECTO,
    description="Plataforma de Optimización de Itinerarios Multidestino y Prevención de Riesgos de Equipaje",
    version=config.VERSION,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(buscador.router)
app.include_router(perfil.router)
app.include_router(reglas.router)
app.include_router(alertas.router)
app.include_router(itinerarios.router)

@app.get("/", tags=["Estado del Sistema"])
async def raiz():
    return {
        "estado": "operativo", 
        "proyecto": config.NOMBRE_PROYECTO
}
