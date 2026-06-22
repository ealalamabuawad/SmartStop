from fastapi import APIRouter, HTTPException
import httpx
import asyncio
from app.schemas.vuelos_equipaje import BusquedaVueloInput

router = APIRouter(prefix="/vuelos", tags=["Buscador y Stopovers"])

@router.post("/buscar")
async def buscar_itinerarios(datos: BusquedaVueloInput):
    AMADEUS_API_KEY = "tu_api_key_amadeus"
    KIWI_API_KEY = "tu_api_key_kiwi"

    async with httpx.AsyncClient() as client:
        try:
            peticion_amadeus = client.get(
                f"https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode={datos.origen}&destinationLocationCode={datos.destino}&departureDate={datos.fecha_salida}&adults=1",
                headers={"Authorization": f"Bearer {AMADEUS_API_KEY}"}
            )
            peticion_kiwi = client.get(
                f"https://api.tequila.kiwi.com/v2/search?fly_from={datos.origen}&fly_to={datos.destino}&date_from={datos.fecha_salida}",
                headers={"apikey": KIWI_API_KEY}
            )

            # Orquestación paralela
            respuesta_amadeus, respuesta_kiwi = await asyncio.gather(peticion_amadeus, peticion_kiwi, return_exceptions=True)

            return {"estado": "en_construccion", "mensaje": "Endpoints listos para recibir credenciales"}

        except Exception as e:
            raise HTTPException(status_code=500, detail="Error en la orquestación de APIs externas")