import json
import os

import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Response, status
import httpx

from models.entrada import Entrada, EntradaList, EntradaNew, EntradaUpdate

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

entradas_router = APIRouter(
    prefix="/entradas",
    tags=['entradas']
)

# Configuración de MongoDB
db = pymongo.MongoClient(MONGO_URL).laWikiv2
entradas = db.entradas

# GET /entradas
@entradas_router.get("/", response_model=EntradaList)
def get_entries(nombre: str = None, idWiki: str = None):
    query = {}
    if nombre:
        query["nombre"] = {"$regex": nombre, "$options": "i"}
    if idWiki:
        query["idWiki"] = idWiki
    try:
        entradas_data = entradas.find(query).to_list(1000)
        return EntradaList(entradas = entradas_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al buscar las entradas: {str(e)}")

# GET /entradas/<id>
@entradas_router.get("/{id}", response_model=Entrada)
def get_entry_by_id(id: str):
    try:
        entrada = entradas.find_one({"_id": ObjectId(id)})
        if entrada:
            return entrada
        else:
            raise HTTPException(status_code=404, detail= "Entrada no encontrada")
    except Exception as e:
        raise HTTPException(status_code=400, detail= f"Error al buscar la entrada: {str(e)}")

# # POST /entradas
@entradas_router.post("/", response_model=Entrada, status_code=status.HTTP_201_CREATED)
def create_entry(entrada: EntradaNew):
    if not ObjectId.is_valid(entrada.idWiki):
        raise HTTPException(status_code=400, detail=f"ID de wiki {entrada.idWiki} no tiene formato valido")
    if not ObjectId.is_valid(entrada.idVersionActual):
        raise HTTPException(status_code=400, detail=f"ID de version actual {entrada.idVersionActual} no tiene formato valido")
    entrada.idVersionActual = ObjectId(entrada.idVersionActual)
    entrada.idWiki = ObjectId(entrada.idWiki)
    try:
        if entrada.nombre and entradas.find_one({"nombre": entrada.nombre}):
            raise HTTPException(status_code=400, detail= f"Ya existe una entrada con el nombre {entrada.nombre}")
        result = entradas.insert_one(entrada.model_dump(by_alias=True))
        return entradas.find_one({"_id": result.inserted_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail= f"Error al buscar la entrada: {str(e)}")
    
# PUT /entradas/<id>
@entradas_router.put("/{id}", response_model=Entrada)
def update_entry(id: str, entrada: EntradaUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID {id} no tiene formato valido")
    
    print(entrada)
    
    if entrada.nombre and entradas.find_one({"nombre": entrada.nombre}):
        raise HTTPException(status_code=400, detail= f"Ya existe una entrada con el nombre {entrada.nombre}")
    
    update_result = entradas.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": entrada.model_dump(by_alias=True, exclude_none=True)},
        return_document=pymongo.ReturnDocument.AFTER,
    )
    if update_result is not None:
        return update_result
    else:
        raise HTTPException(status_code=404, detail=f"Entrada con ID {id} no encontrada")

# DELETE /entradas/<id>
@entradas_router.delete("/{id}")
def delete_entry(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID {id} no tiene formato valido")
    
    delete_result = entradas.delete_one({"_id": ObjectId(id)})
    
    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    raise HTTPException(status_code=404, detail=f"Entrada con ID {id} no encontrada")

# DELETE /entradas/ : JSON {idWiki:"xxxxxxxxx"} Borra las entradas asociadas a una wiki
@entradas_router.delete("/wikis/{id}")
def delete_entries_byWiki(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID {id} no tiene formato valido")
    
    with httpx.Client() as client:
        try:
            for entrada in entradas.find({"idWiki": id}):
                # eliminamos las versiones de la entrada
                # client.delete(f"http://localhost:{os.getenv("SERVICE_ENTRADAS_PORT")}/versiones", json={"idEntrada": entrada.id})
                # eliminamos la entrada
                entrada = entrada["_id"]
                print(f"http://localhost:{os.getenv('SERVICE_ENTRADAS_PORT')}/entradas/{entrada}")
                client.delete(f"http://localhost:{os.getenv('SERVICE_ENTRADAS_PORT')}/entradas/{entrada}")
        except Exception as e:
            raise HTTPException(status_code=400, detail= f"Error al buscar las entradas: {str(e)}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# # GET /entradas/<id>/wikis
# @entradas_router.route("/<id>/wiki", methods=['GET'])
# def get_wikis_for_entry(id):
#     try:
#         entrada = entradas.find_one({"_id": ObjectId(id)})
#     except Exception as e:
#         raise HTTPException(status_code=400, detail= f"Error al buscar la entrada: {str(e)}"}), 400
#     if entrada:
#         wiki_id = entrada["idWiki"]
#         wikiServiceName = os.getenv("ENDPOINT_WIKIS")
#         wikiServicePort = os.getenv("SERVICE_WIKIS_PORT")
#         if current_app.debug:
#             wiki_raw = requests.get(f"http://localhost:{wikiServicePort}/wikis/{wiki_id}") # solo dev
#         else:
#             wiki_raw = requests.get(f"http://{wikiServiceName}:{wikiServicePort}/wikis/{wiki_id}")

#         if wiki_raw.status_code == 200:
#             return jsonify(wiki_raw.json()), 200
#         else:
#             raise HTTPException(status_code=400, detail="Error al obtener la wiki de la entrada"}), 400
#     else:
#         raise HTTPException(status_code=400, detail= "Entrada no encontrada"}), 404

# # GET /entradas/<id>/comentarios
# @entradas_router.route("/<id>/comentarios", methods=['GET'])
# def get_comentarios_for_entry(id):
#     try:
#         entrada = entradas.find_one({"_id": ObjectId(id)})
#         if entrada:
#             slug = entrada["slug"]
#             # buscar todos los comentarios de la entrada
#             comentariosServiceName = os.getenv("ENDPOINT_COMENTARIOS")
#             comentariosPort = os.getenv("SERVICE_COMENTARIOS_PORT")

#             if current_app.debug:
#                 url = f"http://localhost:{comentariosPort}/comentarios?idEntrada={id}"
#             else:
#                 url = f"http://{comentariosServiceName}:{comentariosPort}/comentarios?idEntrada={id}"

#             comentarios_raw = requests.get(url)
#             if comentarios_raw.status_code == 200:
#                 return jsonify(comentarios_raw.json()), 200
#             else:
#                 raise HTTPException(status_code=400, detail="Error al obtener los comentarios de la entrada"}), 400
#         else:
#             raise HTTPException(status_code=400, detail= "Entrada no encontrada"}), 404
#     except Exception as e:
#         raise HTTPException(status_code=400, detail= f"Error al buscar la entrada: {str(e)}"}), 400
