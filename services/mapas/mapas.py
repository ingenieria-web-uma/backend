from fastapi import FastAPI, HTTPException
import httpx
from cachetools import TTLCache

app = FastAPI()

cache = TTLCache(maxsize=100, ttl=3600)

@app.get("/v2/mapas")
async def mapas(q: str):
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
