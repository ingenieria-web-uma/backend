import os
from models.traduccion import TraduccionRequest
import pymongo
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
import httpx
from typing import Dict

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
GTRANSLATE_API_KEY = os.getenv("GTRANSLATE_API_KEY")

traducciones_bp = APIRouter(prefix="/v3/traducciones", tags=["traducciones"])

db = pymongo.MongoClient(MONGO_URL).laWikiv3
traducciones = db.traducciones


async def traducir_google(textos: Dict[str, str], target_lang: str):
    values = list(textos.values())
    url = f"https://translation.googleapis.com/language/translate/v2?key={GTRANSLATE_API_KEY}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            data={
                "q": values,
                "target": target_lang,
                "format": "text",
            },
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Error en la traducción"
        )

    translated_data = response.json()
    translated_values = [
        t["translatedText"] for t in translated_data["data"]["translations"]
    ]

    translated_texts = {
        key: translated_values[i] for i, key in enumerate(textos.keys())
    }
    return translated_texts


@traducciones_bp.post("/traducir")
async def traducir_texto(request: TraduccionRequest):
    try:
        traducciones = await traducir_google(request.textos, request.target_lang)
        return {"translations": traducciones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la traducción: {str(e)}")


@traducciones_bp.get("/idiomas")
async def get_idiomas():
    try:
        url = f"https://translation.googleapis.com/language/translate/v2/languages?key={GTRANSLATE_API_KEY}&target=es"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="Error al obtener idiomas"
            )

        languages_data = response.json()
        return {"languages": languages_data["data"]["languages"]}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener idiomas: {str(e)}"
        )
