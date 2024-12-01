import os

import pymongo
import requests
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException

from models.wiki import Wiki, WikiFilter, WikiList, WikiNew, WikiUpdate

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

wikis_bp = APIRouter(prefix="/v2/wikis", tags=["wikis"])

client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
wikis = db.wikis

# GET /wikis/


@wikis_bp.get("/")
def get_wikis(filtro: WikiFilter = Depends()):
    try:
        wikisRes = wikis.find(filtro.model_dump(exclude_none=True))
        return WikiList(wikis=[wiki for wiki in wikisRes]).model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener las wikis, {e}")


# GET /wikis/<id>


@wikis_bp.get("/{id}", response_model=Wiki)
def get_wikis_byId(id: str):
    try:
        resultado = wikis.find_one({"_id": ObjectId(id)})
        if resultado:
            resultado["_id"] = str(resultado["_id"])
            return resultado
        else:
            raise HTTPException(status_code=404, detail="Wiki no encontrada")
    except Exception as e:
        raise HTTPException(status_code=400, detail="ID inválido")


# POST /wikis/


@wikis_bp.post("/", response_model=Wiki)
def create_wiki(wiki: WikiNew):
    try:
        wiki_dump = wiki.model_dump()
        wiki_id = wikis.insert_one(wiki_dump).inserted_id
        return wikis.find_one({"_id": wiki_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear la wiki: {str(e)}")


# PUT /wikis/<id>


@wikis_bp.put("/{id}")
def update_wiki(id: str, wikiUpdate: WikiUpdate):
    try:
        dataFormateada = {"$set": wikiUpdate.to_mongo_dict(exclude_none=True)}
        respuesta = wikis.find_one_and_update(
            {"_id": ObjectId(id)},
            dataFormateada,
            return_document=pymongo.ReturnDocument.AFTER,
        )
        if respuesta is None:
            raise HTTPException(status_code=404, detail="Wiki no encontrada")
        return Wiki(**respuesta).model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al actualizar la wiki: {str(e)}"
        )


# DELETE /wikis/<id>


@wikis_bp.delete("/{id}")
def delete_wiki(id: str):
    try:
        borrado = wikis.delete_one({"_id": ObjectId(id)})
        if borrado.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Wiki no encontrada")
        raise HTTPException(status_code=200, detail="Wiki borrada")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al borrar la wiki: {str(e)}"
        )


# GET /wikis/<id>/entradas


@wikis_bp.get("/{id}/entradas")
def get_entradas_byWiki(id: str):
    nombreServicio = os.getenv("ENDPOINT_ENTRADAS")
    puertoServicio = os.getenv("SERVICE_ENTRADAS_PORT")
    # Obtenemos del microservicio de entradas las entradas de la wiki
    try:
        # Hay que cambiar la URL por la del microservicio de entradas
        if (os.getenv("DOCKER")):
            response = requests.get(f"http://gateway:8000/entradas?wiki={id}")
        else:
            response = requests.get(f"http://127.0.0.1:{puertoServicio}/v2/entradas?wiki={id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar las entradas: {str(e)}"
        )
