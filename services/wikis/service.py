import json
import os

import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException

from models.wiki import Wiki, WikiFilter, WikiList, WikiNew, WikiUpdate

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

wikis_bp = APIRouter(
    prefix="/v2/wikis",
    tags=["wikis"]
)

client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
wikis = db.wikis

#GET /wikis/

@wikis_bp.get("/")
def get_wikis(filtro: WikiFilter = Depends()):
    try:
        wikisRes = wikis.find(filtro.model_dump(exclude_none=True))
        return WikiList(wikis=[wiki for wiki in wikisRes]).model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener las wikis, {e}")

#GET /wikis/<id>

@wikis_bp.get("/{id}")
def get_wikis_byId(id):
    try:
        resultado = wikis.find_one({"_id":ObjectId(id)})
        if resultado:
            return Wiki(**resultado).model_dump()
        else:
            raise HTTPException(status_code=404, detail=f"Wiki {id} no encontrada")
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener la wiki {id}, {e}")
#
# #POST /wikis/
#
@wikis_bp.post("/")
def create_wiki(newWiki: WikiNew):
    try:
        wiki_existente = wikis.find_one({"nombre": newWiki.nombre})

        if wiki_existente:
            raise HTTPException(status_code=400, detail="Ya existe una wiki con ese nombre")
        else:
            wikis.insert_one(newWiki.to_mongo_dict(exclude_none=True))
            raise HTTPException(status_code=201, detail="Wiki creada correctamente")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear la wiki, {e}")
#
# #PUT /wikis/<id>
#
@wikis_bp.put("/{id}")
def update_wiki(id, wikiUpdate: WikiUpdate):
    try:
        dataFormateada = {"$set": wikiUpdate.to_mongo_dict(exclude_none=True)}
        respuesta = wikis.find_one_and_update({"_id":ObjectId(id)}, dataFormateada, return_document=True)

        if respuesta is None:
            raise HTTPException(status_code=404, detail=f"Wiki {id} no encontrada")
        else:
            raise HTTPException(status_code=200, detail="Wiki actualizada correctamente")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al actualizar la wiki {id}, {e}")
#
# #DELETE /wikis/<id>
#
# @wikis_bp.delete("/{id}")
# def delete_wiki(id):
#
#     try:
#         wiki = wikis.find_one({"_id":ObjectId(id)})
#     except Exception as e:
#         return f"La wiki {id} no existe, por lo tanto no se puede borrar", 404
#         #borrar entradas de la wiki
#     headers = {"Content-Type":"application/json"}
#     if current_app.debug:
#         response = requests.delete(f"http://localhost:{os.getenv("SERVICE_ENTRADAS_PORT")}/entradas",headers=headers, json={"idWiki":id})
#     else:
#         response = requests.delete(f"http://{os.getenv("ENDPOINT_ENTRADAS")}:{os.getenv("SERVICE_ENTRADAS_PORT")}/entradas", headers=headers,json={"idWiki":id})
#
#
#     if response.status_code != 200:
#         return "Error al eliminar las entradas relacionadas a la wiki", 400
#
#     try:
#         borrado = wikis.delete_one({"_id":ObjectId(id)})
#     except Exception as e:
#         return f"Error al borrar la wiki {id}", 400
#     if borrado.deleted_count == 0:
#         return f"La wiki {id} no existe, por lo tanto no se puede borrar", 200
#
#     return "La wiki ha sido borrada con éxito", 200
#
#
# #GET /wikis/<id>/entradas
#
# @wikis_bp.route("/<id>/entradas", methods=['GET'])
# def get_entradas_byWiki(id):
#     nombreServicio= os.getenv("ENDPOINT_ENTRADAS")
#     puertoServicio= os.getenv("SERVICE_ENTRADAS_PORT")
#     if current_app.debug:
#         url = f"http://localhost:{puertoServicio}/entradas/?idWiki={id}"
#     else:
#         url = f"http://{nombreServicio}:{puertoServicio}/entradas/?idWiki={id}"
#     resultado = requests.get(url)
#     if resultado.status_code != 200:
#         return jsonify({"error":"No se ha podido solicitar las entradas de la wiki"}), 404
#     else:
#         return jsonify(resultado.json())
