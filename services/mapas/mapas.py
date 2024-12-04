import httpx
import os
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from cachetools import TTLCache

from models.mapa import Mapa, MapaNew, MapaUpdate

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

mapas_bp = APIRouter(prefix="/v2/mapas", tags=["mapas"])

db = pymongo.MongoClient(MONGO_URL).laWikiv2
mapas = db.mapas

cache = TTLCache(maxsize=100, ttl=3600)


@mapas_bp.get("")
def get_mapas_por_query_o_coords(q: str = None, lat: float = None, lon: float = None):
    if q:
        if q in cache:
            return {"source": "cache", "data": cache[q]}

        with httpx.Client() as client:
            params = {"q": q, "format": "jsonv2", "addressdetails": 1, "limit": 1}
            response = client.get(
                "https://nominatim.openstreetmap.org/search", params=params
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error al consultar Nominatim",
                )

            data = response.json()
            if not data:
                raise HTTPException(
                    status_code=404, detail="No se encontraron resultados"
                )

            cache[q] = data[0]
            return {"source": "nominatim", "data": data[0]}

    elif lat is not None and lon is not None:
        cache_key = f"{lat},{lon}"
        if cache_key in cache:
            return {"source": "cache", "data": cache[cache_key]}

        with httpx.Client() as client:
            params = {"lat": lat, "lon": lon, "format": "jsonv2", "addressdetails": 1}
            response = client.get(
                "https://nominatim.openstreetmap.org/reverse", params=params
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error al consultar Nominatim",
                )

            data = response.json()
            if "error" in data:
                raise HTTPException(
                    status_code=404, detail="No se encontraron resultados"
                )

            cache[cache_key] = data
            return {"source": "nominatim", "data": data}

    else:
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar 'q' para búsqueda o 'lat' y 'lon' para búsqueda inversa",
        )


@mapas_bp.get("/{id}", response_model=Mapa)
def get_mapa_por_id(id):
    try:
        mapa = mapas.find_one({"_id": ObjectId(id)})
        if not mapa:
            raise HTTPException(status_code=404, detail="Mapa no encontrado")

        return mapa
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar el mapa: {str(e)}"
        )


@mapas_bp.get("/{idEntrada}", response_model=Mapa)
def get_mapa_por_entrada(idEntrada):
    try:
        mapa = mapas.find_one({"idEntrada": ObjectId(idEntrada)})
        if not mapa:
            raise HTTPException(status_code=404, detail="Mapa no encontrado")

        return mapa
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar el mapa: {str(e)}"
        )


@mapas_bp.post("/")
def create_mapa(mapa: MapaNew):
    try:
        mapa_data = mapa.to_mongo_dict(exclude_none=True)
        mapas.insert_one(mapa_data)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al crerar el mapa: {str(e)}"
        )


@mapas_bp.put("/{id}")
def update_mapa(id, mapa: MapaUpdate):
    try:
        filter = {"_id": ObjectId(id)}
        mapa_existente = mapas.find_one(filter)
        if not mapa_existente:
            raise HTTPException(status_code=404, detail="Mapa no encontrado")

        res = mapas.update_one(filter, {"$set": mapa.to_mongo_dict(exclude_none=True)})

        if res.modified_count == 0:
            raise HTTPException(status_code=404, detail="No se pudo actualizar el mapa")

        return {"message": "Mapa actualizado correctamente"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al actualizar el mapa: {str(e)}"
        )


@mapas_bp.delete("/{id}")
def delete_mapa(id):
    try:
        res = mapas.delete_one({"_id": ObjectId(id)})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Mapa no encontrado")

        return {"message": f"Mapa con ID {id} eliminado"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al eliminar el mapa: {str(e)}"
        )
