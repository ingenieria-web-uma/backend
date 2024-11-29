import httpx
import os
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from cachetools import TTLCache

from models.mapa import MapInfo, MapListResponse

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

mapas_bp = APIRouter(
    prefix="/v2/mapas",
    tags=['mapas']
)

db = pymongo.MongoClient(MONGO_URL).laWikiv2
mapas = db.mapas

cache = TTLCache(maxsize=100, ttl=3600)

@mapas_bp.get("")
def get_mapas_por_query_o_coords(q: str = None, lat: float = None, lon: float = None):
    if q:
        if q in cache:
            return {"source": "cache", "data": cache[q]}

        with httpx.Client() as client:
            params = {
                "q": q,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 1
            }
            response = client.get("https://nominatim.openstreetmap.org/search", params=params)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error al consultar Nominatim")

            data = response.json()
            if not data:
                raise HTTPException(status_code=404, detail="No se encontraron resultados")

            cache[q] = data[0]
            return {"source": "nominatim", "data": data[0]}

    elif lat is not None and lon is not None:
        cache_key = f"{lat},{lon}"
        if cache_key in cache:
            return {"source": "cache", "data": cache[cache_key]}

        with httpx.Client() as client:
            params = {
                "lat": lat,
                "lon": lon,
                "format": "jsonv2",
                "addressdetails": 1
            }
            response = client.get("https://nominatim.openstreetmap.org/reverse", params=params)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error al consultar Nominatim")

            data = response.json()
            if "error" in data:
                raise HTTPException(status_code=404, detail="No se encontraron resultados")

            cache[cache_key] = data
            return {"source": "nominatim", "data": data}

    else:
        raise HTTPException(status_code=400, detail="Debe proporcionar 'q' para búsqueda o 'lat' y 'lon' para búsqueda inversa")


@mapas_bp.get("/entrada/{idEntrada}", response_model=MapListResponse)
def get_mapas_por_entrada(idEntrada: str):
    mapas_cursor = mapas.find({"idEntrada": ObjectId(idEntrada)})
    mapas_entrada = [MapInfo(**m) for m in mapas_cursor]
    return MapListResponse(mapas=mapas_entrada)


@mapas_bp.get("/{idMapa}/entrada/{idEntrada}", response_model=MapInfo)
def get_mapa_por_id(idMapa: str, idEntrada: str):
    mapa = mapas.find_one({"_id": ObjectId(idMapa), "idEntrada": ObjectId(idEntrada)})
    if not mapa:
        raise HTTPException(status_code=404, detail="Mapa no encontrado")
    return MapInfo(**mapa)


@mapas_bp.post("/entrada/{idEntrada}", response_model=MapInfo)
def add_mapa_a_entrada(idEntrada: str, mapa: MapInfo):
    mapa_data = mapa.model_dump(exclude_unset=True, by_alias=True)
    mapa_data["idEntrada"] = ObjectId(idEntrada)
    result = mapas.insert_one(mapa_data)
    mapa_data["_id"] = result.inserted_id
    return MapInfo(**mapa_data)


@mapas_bp.put("/{idMapa}/entrada/{idEntrada}", response_model=MapInfo)
def update_mapa(idMapa: str, idEntrada: str, mapa: MapInfo):
    existing_mapa = mapas.find_one({"_id": ObjectId(idMapa), "idEntrada": ObjectId(idEntrada)})
    if not existing_mapa:
        raise HTTPException(status_code=404, detail="Mapa no encontrado")

    mapa_data = mapa.model_dump(exclude_unset=True, by_alias=True)
    result = mapas.update_one(
        {"_id": ObjectId(idMapa), "idEntrada": ObjectId(idEntrada)},
        {"$set": mapa_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="No se pudo actualizar el mapa")

    updated_mapa = mapas.find_one({"_id": ObjectId(idMapa), "idEntrada": ObjectId(idEntrada)})
    return MapInfo(**updated_mapa)


@mapas_bp.delete("/{idMapa}/entrada/{idEntrada}", response_model=dict)
def delete_mapa(idMapa: str, idEntrada: str):
    result = mapas.delete_one({"_id": ObjectId(idMapa), "idEntrada": ObjectId(idEntrada)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Mapa no encontrado")
    return {"message": f"Mapa con ID {idMapa} eliminado de la entrada {idEntrada}"}