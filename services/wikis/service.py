import json
import os

import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, UploadFile
from models.wiki import WikiNew, WikiUpdate, WikiList, Wiki
from typing import Optional


load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

wikis_bp = APIRouter(
    prefix="/wikis",
    tags=['wikis']
)

client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
wikis = db.wikis

#GET /wikis/

@wikis_bp.get("/", response_model=WikiList)
def get_wikis(nombre: Optional[str] = None):
    query = {}
    if nombre:
        query["nombre"] = {"$regex": nombre, "$options": "i"}
    try:
        resultado = wikis.find(query)
        return WikiList(wikis=resultado)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al buscar las wikis: {str(e)}")

#GET /wikis/<id>

@wikis_bp.get("/{id}")
def get_wikis_byId(id: str):
    try:
        resultado = wikis.find_one({"_id":ObjectId(id)})
        if resultado:
            resultado["_id"] = str(resultado["_id"])
            return resultado
        else:
            raise HTTPException(status_code=404, detail="Wiki no encontrada")
    except Exception as e:
        raise HTTPException(status_code=400, detail="ID inválido")
    
#POST /wikis/

@wikis_bp.post("/", response_model=Wiki)
def create_wiki(wiki: WikiNew):
    try:
        wiki_dump = wiki.model_dump()
        wiki_id = wikis.insert_one(wiki_dump).inserted_id
        return wikis.find_one({"_id": wiki_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear la wiki: {str(e)}")

#PUT /wikis/<id>

@wikis_bp.put("/{id}")
def update_wiki(id: str, wiki: WikiUpdate):
    wiki_dump = wiki.model_dump(exclude_unset=True)
    wiki_dump = {k: v for k, v in wiki_dump.items() if v is not None}
    if not wiki_dump:
        raise HTTPException(status_code=400, detail="No se han recibido datos para actualizar")
    result = wikis.update_one({"_id": ObjectId(id)}, {"$set": wiki_dump})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Wiki no encontrada")
    wiki = wikis.find_one({"_id": ObjectId(id)})
    if wiki:
        wiki["_id"] = str(wiki["_id"])
        return wiki
    else:
        raise HTTPException(status_code=404, detail="Wiki no encontrada")

#DELETE /wikis/<id>

@wikis_bp.delete("/{id}")
def delete_wiki(id: str):
    try:
        borrado = wikis.delete_one({"_id":ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al borrar la wiki: {str(e)}")
    if borrado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Wiki no encontrada")
    return "Wiki borrada con éxito"

#GET /wikis/<id>/entradas

@wikis_bp.get("/{id}/entradas")
def get_entradas_byWiki(id: str):
    nombreServicio= os.getenv("ENDPOINT_ENTRADAS")
    puertoServicio= os.getenv("SERVICE_ENTRADAS_PORT")
    #Obtenemos del microservicio de entradas las entradas de la wiki
    try:
        #Hay que cambiar la URL por la del microservicio de entradas
        response = requests.get(f"http://127.0.0.1:{puertoServicio}/entradas?wiki={id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al buscar las entradas: {str(e)}")