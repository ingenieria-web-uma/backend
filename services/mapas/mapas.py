from fastapi import APIRouter, HTTPException
import httpx
from cachetools import TTLCache

mapas_bp = APIRouter(
    prefix="/v2/mapas",
    tags=['mapas']
    )

cache = TTLCache(maxsize=100, ttl=3600)

@mapas_bp.get("")
async def mapas(q: str = None, lat: float = None, lon: float = None):
    if q:
        if q in cache:
            return {"source": "cache", "data": cache[q]}

        async with httpx.AsyncClient() as client:
            params = {
                "q": q,
                "format": "json",
                "addressdetails": 1,
                "limit": 1
            }
            response = await client.get("https://nominatim.openstreetmap.org/search", params=params)

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

        async with httpx.AsyncClient() as client:
            params = {
                "lat": lat,
                "lon": lon,
                "format": "json",
                "addressdetails": 1
            }
            response = await client.get("https://nominatim.openstreetmap.org/reverse", params=params)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error al consultar Nominatim")

            data = response.json()
            if "error" in data:
                raise HTTPException(status_code=404, detail="No se encontraron resultados")

            cache[cache_key] = data
            return {"source": "nominatim", "data": data}

    else:
        raise HTTPException(status_code=400, detail="Debe proporcionar 'q' para búsqueda o 'lat' y 'lon' para búsqueda inversa")