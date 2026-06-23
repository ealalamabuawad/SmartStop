import httpx
import asyncio
from datetime import datetime, timedelta
from app.core.configuracion import config
from app.core.database import tabla_smartstop

class ApiViajesService:
    def __init__(self):
        base_url = config.DUFFEL_API_URL.replace("/air", "").rstrip("/")
        self.search_url = f"{base_url}/air/offer_requests"
        
        self.headers = {
            "Authorization": f"Bearer {config.DUFFEL_API_KEY}",
            "Duffel-Version": "v2",
            "Content-Type": "application/json"
        }

    async def sincronizar_itinerarios(self, origen: str, destino: str, fecha_salida: str):
        """
        Consulta vuelos reales a Duffel y almacena TODOS los itinerarios disponibles
        (directos, con escala, solo ida) en DynamoDB local.
        """
        payload = {
            "data": {
                "passengers": [{"type": "adult"}],
                "slices": [
                    {
                        "origin": origen,
                        "destination": destino,
                        "departure_date": fecha_salida
                    }
                ],
                "cabin_class": "economy"
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self.search_url, json=payload, headers=self.headers)
                
                if response.status_code != 201:
                    return {"status": "error_api", "status_code": response.status_code}
                    
                data = response.json()
                offers = data.get("data", {}).get("offers", [])
                items_guardados = 0
                
                for offer in offers:
                    offer_id = offer.get("id")
                    slices = offer.get("slices", [])
                    if not slices: continue
                    
                    segments = slices[0].get("segments", [])
                    if not segments: continue
                    
                    # Estructuramos la metadata de los segmentos para guardarla en nuestra BD
                    itinerario_vuelos = []
                    detalles_escalas = []
                    
                    for i, seg in enumerate(segments):
                        codigo_vuelo = f"{seg['marketing_carrier']['iata_code']}{seg['marketing_carrier_flight_number']}"
                        itinerario_vuelos.append(codigo_vuelo)
                        
                        # Si hay un segmento siguiente, calculamos el tiempo de esa escala
                        if i < len(segments) - 1:
                            llegada_ant = datetime.fromisoformat(seg["arriving_at"])
                            salida_sig = datetime.fromisoformat(segments[i+1]["departing_at"])
                            horas_escala = int((salida_sig - llegada_ant).total_seconds() / 3600)
                            detalles_escalas.append({
                                "aeropuerto": seg["destination"]["iata_code"],
                                "duracion_horas": horas_escala
                            })

                    pk_ruta = f"RUTA#{origen}_{destino}"
                    co_oferta = f"OFFER#{offer_id}"
                    
                    costo_total = int(float(offer.get("total_amount", 0)))
                    ts_futuro = int(datetime.utcnow().timestamp()) + (3 * 24 * 60 * 60)
                    
                    # Estructura limpia
                    item_nosql = {
                        'PK': pk_ruta,
                        'CO': co_oferta,
                        'EntidadDatos_JSON': {
                            'aerolinea_owner': offer.get("owner", {}).get("name", "Desconocida"),
                            'fecha_vuelo': fecha_salida,
                            'vuelos': list(itinerario_vuelos),
                            'es_directo': len(segments) == 1,
                            'escalas': detalles_escalas,
                            'costo_clp': costo_total,
                            'moneda_original': offer.get("total_currency", "EUR")
                        },
                        'TTL': ts_futuro
                    }
                    
                    tabla_smartstop.put_item(Item=item_nosql)
                    items_guardados += 1
                        
                return {"status": "success", "itinerarios_guardados": items_guardados}
            except Exception as e:
                return {"status": "error_codigo", "detail": str(e)}

    async def sincronizar_todo(self):
        """
        Barrido masivo sin filtros enfocado en los hubs internacionales principales.
        """
        # Filtramos los nacionales para maximizar la cuota de la API en rutas de alta densidad
        destinos = ["CDG", "MAD", "BCN", "LHR", "GIG", "LIM", "BOG"]
        origen = "SCL"
        
        fecha_inicio = datetime(2026, 6, 22)
        fecha_fin = datetime(2026, 7, 10)
        
        fechas_a_consultar = []
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            fechas_a_consultar.append(fecha_actual.strftime("%Y-%m-%d"))
            fecha_actual += timedelta(days=1)
            
        resultados_totales = []
        
        for destino in destinos:
            for fecha in fechas_a_consultar:
                resultado = await self.sincronizar_itinerarios(origen, destino, fecha)
                resultados_totales.append({
                    "ruta": f"{origen}-{destino}", 
                    "fecha": fecha, 
                    "resultado": resultado
                })
                await asyncio.sleep(1.2)
                
        return resultados_totales