from typing import List
from fastapi import APIRouter, HTTPException
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import random

from app.core.database import tabla_smartstop
from app.services.api_viajes import ApiViajesService

from app.schemas.buscador import BusquedaItinerarioRequest
from app.schemas.resultados import ItinerarioOptimizadoResponse, TrayectoVista

router = APIRouter(prefix="/vuelos", tags=["Buscador y Orquestación"])

@router.get("/aeropuertos", response_model=List[dict], tags=["Buscador y Orquestación"])
def listar_aeropuertos():
    """
    Retorna dinámicamente todos los destinos, escalas y stopovers disponibles 
    en la base de datos sin dejar códigos huérfanos como GRU.
    """
    try:
        respuesta = tabla_smartstop.scan()
        items = respuesta.get('Items', [])
        destinos_unicos = set()
        resultados = []
        
        mapeo_geo = {
            "SCL": {"nombre": "Comodoro Arturo Merino Benítez", "ciudad": "Santiago", "pais": "Chile"},
            "ZCO": {"nombre": "La Araucanía", "ciudad": "Temuco", "pais": "Chile"},
            "PMC": {"nombre": "El Tepual", "ciudad": "Puerto Montt", "pais": "Chile"},
            "CDG": {"nombre": "Charles de Gaulle", "ciudad": "París", "pais": "Francia"},
            "MAD": {"nombre": "Adolfo Suárez Madrid-Barajas", "ciudad": "Madrid", "pais": "España"},
            "BCN": {"nombre": "El Prat", "ciudad": "Barcelona", "pais": "España"},
            "LHR": {"nombre": "Heathrow", "ciudad": "Londres", "pais": "Inglaterra"},
            "GIG": {"nombre": "Galeão", "ciudad": "Río de Janeiro", "pais": "Brasil"},
            "GRU": {"nombre": "Guarulhos", "ciudad": "São Paulo", "pais": "Brasil"},
            "LIM": {"nombre": "Jorge Chávez", "ciudad": "Lima", "pais": "Perú"},
            "BOG": {"nombre": "El Dorado", "ciudad": "Bogotá", "pais": "Colombia"},
            "AEP": {"nombre": "Jorge Newbery", "ciudad": "Buenos Aires", "pais": "Argentina"}
        }
        
        for item in items:
            pk = item.get('PK', '')
            if not pk: 
                continue
            
            if pk.startswith("RUTA#"):
                raw_ruta = pk.split('#')[1]
                codigos_pk = raw_ruta.replace('_', '-').split('-')
                for code in codigos_pk:
                    if code: 
                        destinos_unicos.add(code.strip().upper())
            
            datos_vuelo = item.get('EntidadDatos_JSON', {})
            if datos_vuelo:
                escalas = datos_vuelo.get('escalas', [])
                for esc in escalas:
                    aeropuerto_escala = esc.get('aeropuerto')
                    if aeropuerto_escala:
                        destinos_unicos.add(aeropuerto_escala.strip().upper())
                        
                tramos = datos_vuelo.get('tramos', [])
                for tramo in tramos:
                    ori = tramo.get('origen')
                    des = tramo.get('destino')
                    if ori: destinos_unicos.add(ori.strip().upper())
                    if des: destinos_unicos.add(des.strip().upper())

        for codigo_climpio in sorted(destinos_unicos):
            info_geo = mapeo_geo.get(codigo_climpio, {
                "nombre": f"Aeropuerto {codigo_climpio}", 
                "ciudad": codigo_climpio, 
                "pais": "Internacional"
            })
            
            ubicacion_completa = f"{info_geo['ciudad']}, {info_geo['pais']}"
            
            resultados.append({
                "codigo_iata": codigo_climpio,
                "nombre": info_geo["nombre"],
                "pais": ubicacion_completa,
                "moneda_itinerarios": 'CLP' if info_geo["pais"] == "Chile" else 'EUR'
            })
            
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def validar_equipaje_motor(aerolinea_iata: str, req: BusquedaItinerarioRequest) -> dict:
    pk_aerolinea = f"AEROLINEA#{aerolinea_iata}"
    respuesta = tabla_smartstop.get_item(Key={'PK': pk_aerolinea, 'CO': 'REGLAS_EQUIPAJE'})
    if 'Item' not in respuesta: return {"cumple": True, "multa": 0}
    limite_peso = respuesta['Item']['EntidadDatos_JSON'].get('bodega_kg', 23)
    if req.equipaje_peso > limite_peso: return {"cumple": False, "multa": 45000}
    return {"cumple": True, "multa": 0}

@router.post("/buscar", response_model=List[ItinerarioOptimizadoResponse], tags=["Buscador y Orquestación"])
def buscar_itinerarios(req: BusquedaItinerarioRequest):
    try:
        pk_busqueda = f"RUTA#{req.origen_iata}_{req.destino_iata}"
        respuesta = tabla_smartstop.query(
            KeyConditionExpression=Key('PK').eq(pk_busqueda) & Key('CO').begins_with('OFFER#')
        )
        
        ofertas_db = respuesta.get('Items', [])
        itinerarios_finales = []
        
        for item in ofertas_db:
            datos_vuelo = item.get('EntidadDatos_JSON', {})
            if datos_vuelo.get('fecha_vuelo') != req.fecha_salida: continue
                
            vuelos_detalle = datos_vuelo.get('vuelos', [])
            if not vuelos_detalle: continue
                
            aerolinea_principal = datos_vuelo.get('aerolinea_owner', 'Desconocida')
            codigo_linea = vuelos_detalle[0][:2] if len(vuelos_detalle[0]) >= 2 else "YY"
            
            validacion = {"cumple": True, "multa": 0}
            if 'validar_equipaje_motor' in globals():
                validacion = validar_equipaje_motor(codigo_linea, req)
                
            offer_id = item['CO'].split('#')[1]
            es_directo_original = datos_vuelo.get('es_directo', True)
            
            trayectos_obj = []
            dur_ida = "13h 40m" if es_directo_original else "18h 15m"
            avion_ida = "Boeing 787-9 Dreamliner" if es_directo_original else "Airbus A320neo"
            
            es_stopover_flag = False
            stopover_city_final = None
            stopover_hours_final = 0

            # --- LÓGICA DE ORQUESTACIÓN AUTOMÁTICA ---
            if req.trip_type == "ida":
                trayectos_obj.append(TrayectoVista(
                    aerolinea=codigo_linea, aerolinea_nombre=aerolinea_principal,
                    origen=req.origen_iata, destino=req.destino_iata,
                    fecha_salida=req.fecha_salida, hora_salida="10:30",
                    fecha_llegada=req.fecha_salida, hora_llegada="16:45",
                    duracion_formato=dur_ida, es_directo=es_directo_original,
                    info_escalas="Directo" if es_directo_original else "1 escala",
                    tipo_avion=avion_ida
                ))
                
            elif req.trip_type == "ida-vuelta":
                trayectos_obj.append(TrayectoVista(
                    aerolinea=codigo_linea, aerolinea_nombre=aerolinea_principal,
                    origen=req.origen_iata, destino=req.destino_iata,
                    fecha_salida=req.fecha_salida, hora_salida="12:35",
                    fecha_llegada=req.fecha_salida, hora_llegada="23:30",
                    duracion_formato=dur_ida, es_directo=es_directo_original,
                    info_escalas="Directo" if es_directo_original else "1 escala",
                    tipo_avion=avion_ida
                ))
                trayectos_obj.append(TrayectoVista(
                    aerolinea=codigo_linea, aerolinea_nombre=aerolinea_principal,
                    origen=req.destino_iata, destino=req.origen_iata,
                    fecha_salida=req.fecha_regreso or req.fecha_salida, hora_salida="20:25",
                    fecha_llegada=req.fecha_regreso or req.fecha_salida, hora_llegada="17:30",
                    duracion_formato=dur_ida, es_directo=es_directo_original,
                    info_escalas="Directo" if es_directo_original else "1 escala",
                    tipo_avion="Boeing 787-9"
                ))
                
            elif req.trip_type == "multidestino":
                # La App detecta los hubs posibles para generar un Stopover Automático
                hubs = ["GIG", "GRU", "BOG", "LIM"]
                stopover_city_final = random.choice(hubs)
                stopover_hours_final = random.choice([24, 48, 72])
                es_stopover_flag = True

                # Trayecto 1: Hacia el Hub (Stopover)
                trayectos_obj.append(TrayectoVista(
                    aerolinea=codigo_linea, aerolinea_nombre=aerolinea_principal,
                    origen=req.origen_iata, destino=stopover_city_final,
                    fecha_salida=req.fecha_salida, hora_salida="08:15",
                    fecha_llegada=req.fecha_salida, hora_llegada="12:00",
                    duracion_formato="3h 45m", es_directo=True,
                    info_escalas="Stopover (Ida)", tipo_avion="Airbus A320"
                ))
                # Trayecto 2: Desde el Hub hacia Destino Final
                trayectos_obj.append(TrayectoVista(
                    aerolinea=codigo_linea, aerolinea_nombre=aerolinea_principal,
                    origen=stopover_city_final, destino=req.destino_iata,
                    fecha_salida=req.fecha_salida, hora_salida="15:30",
                    fecha_llegada=req.fecha_salida, hora_llegada="23:45",
                    duracion_formato="9h 15m", es_directo=True,
                    info_escalas=f"Vuelo tras {stopover_hours_final}h", tipo_avion="Boeing 787-9"
                ))

            precio_final = Decimal(str(datos_vuelo.get('costo_clp', 0)))
            if req.trip_type == "ida-vuelta": precio_final *= Decimal('1.8')
            if req.trip_type == "multidestino": precio_final *= Decimal('1.5')

            itinerarios_finales.append(
                ItinerarioOptimizadoResponse(
                    codigo_ruta=pk_busqueda.split('#')[1],
                    offer_id=offer_id,
                    aerolinea_owner=aerolinea_principal,
                    precio_vuelo_clp=int(precio_final),
                    cumple_equipaje=validacion.get('cumple', True),
                    multa_estimada_clp=validacion.get('multa', 0),
                    duracion_total_formato=dur_ida,
                    es_stopover=es_stopover_flag,
                    stopover_city=stopover_city_final,
                    stopover_hours=stopover_hours_final,
                    trayectos=trayectos_obj
                )
            )
            
        return itinerarios_finales
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/admin/sincronizar-manual", tags=["Buscador y Orquestación"])
async def sincronizacion_manual(origen: str, destino: str, fecha_salida: str):
    try:
        servicio = ApiViajesService()
        resultado = await servicio.sincronizar_itinerarios(origen, destino, fecha_salida)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/sincronizar-masiva", tags=["Buscador y Orquestación"])
async def sincronizacion_masiva():
    try:
        servicio = ApiViajesService()
        resultados = await servicio.sincronizar_todo()
        return {
            "estado": "finalizado", 
            "total_peticiones": len(resultados),
            "detalles": resultados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))