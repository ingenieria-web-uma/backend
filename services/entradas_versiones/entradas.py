import os

import httpx
import pymongo
import requests
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Response, status

from models.comentario import ComentarioList
from models.entrada import (Entrada, EntradaFiltro, EntradaId, EntradaList,
                            EntradaNew, EntradaUpdate)
from models.version import Version
from models.wiki import Wiki

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

entradas_router = APIRouter(prefix="/v2/entradas", tags=["entradas"])

# Configuración de MongoDB
db = pymongo.MongoClient(MONGO_URL).laWikiv2
entradas = db.entradas
versiones = db.versiones

SERVICE_NOTIFICACIONES_PORT = os.getenv("SERVICE_NOTIFICACIONES_PORT")
ENDPOINT_NOTIFICACIONES = os.getenv("ENDPOINT_NOTIFICACIONES")

if os.getenv("DOCKER"):
    NOTIFICACIONES_SERVICE_URL = "http://gateway:8000/notificaciones"
else:
    NOTIFICACIONES_SERVICE_URL = f"http://localhost:{SERVICE_NOTIFICACIONES_PORT}/{ENDPOINT_NOTIFICACIONES}"


# GET /entradas
@entradas_router.get("/")
def get_entries(filtro: EntradaFiltro = Depends()):
    try:
        entradas_data = entradas.find(filtro.to_mongo_dict(exclude_none=True))
        return EntradaList(entradas=[entrada for entrada in entradas_data]).model_dump(
            exclude_none=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar las entradas: {str(e)}"
        )


# GET /entradas/<id>
@entradas_router.get("/{id}")
def get_entry_by_id(id: str):
    try:
        entrada = entradas.find_one({"_id": ObjectId(id)})
        if entrada:
            return Entrada(**entrada).model_dump()
        else:
            raise HTTPException(status_code=404, detail="Entrada no encontrada")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar la entrada: {str(e)}"
        )


# POST /entradas
@entradas_router.post("/", response_model=EntradaId, status_code=201)
def create_entry(entrada: EntradaNew):
    try:
        entrada_dump = entrada.to_mongo_dict(exclude_none=True)
        entrada_id = entradas.insert_one(entrada_dump).inserted_id
        return EntradaId(idEntrada=str(entrada_id))
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al crear la entrada: {str(e)}"
        )


# PUT /entradas/<id>
@entradas_router.put("/{id}", response_model=Entrada)
def update_entry(id: str, entrada: EntradaUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID {id} no tiene formato valido")

    if entrada.nombre and entradas.find_one({"nombre": entrada.nombre}):
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una entrada con el nombre {entrada.nombre}",
        )
    ##enviar notificacion de que se ha actualizado una entrada
    entrada = entradas.find_one({"_id": ObjectId(id)})
    entrada = Entrada(**entrada)
    entradaJson = entrada.model_dump()
    user_id = entradaJson["idUsuario"]
    message = f"Se ha actualizado la entrada: {entrada.nombre}"
    response =  send_notification(user_id, message, id)
    update_result = entradas.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": entrada.to_mongo_dict(exclude_none=True)},
        return_document=pymongo.ReturnDocument.AFTER,
    )
    if update_result is not None:
        return update_result
    else:
        raise HTTPException(
            status_code=404, detail=f"Entrada con ID {id} no encontrada"
        )


# DELETE /entradas/<id>
@entradas_router.delete("/{id}")
async def delete_entry(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID {id} no tiene formato valido")

    try:
        #enviar notificacion de que se ha eliminado una entrada
        entrada = entradas.find_one({"_id": ObjectId(id)})
        entradaModel = Entrada(**entrada).model_dump()
        user_id = entradaModel["idUsuario"]
        message = f"Se ha eliminado la entrada: {entradaModel['nombre']}"
        response =  send_notification(user_id, message, id)
        delete_result = entradas.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al eliminar la entrada: {str(e)}"
        )

    if delete_result.deleted_count == 1:
        raise HTTPException(status_code=204, detail="Entrada eliminada correctamente")

    raise HTTPException(status_code=404, detail=f"Entrada con ID {id} no encontrada")


# DELETE /entradas/ : JSON {idWiki:"xxxxxxxxx"} Borra las entradas asociadas a una wiki
@entradas_router.delete("/")
def delete_entries_by_wiki(idWiki: str):
    if not ObjectId.is_valid(idWiki):
        raise HTTPException(
            status_code=400, detail=f"ID {idWiki} no tiene formato valido"
        )

    entradasServiceName = os.getenv("ENDPOINT_ENTRADAS")
    entradasServicePort = os.getenv("SERVICE_ENTRADAS_PORT")

    if os.getenv("DOCKER"):
        url_base = "https://gateway:8000"
    else:
        url_base = f"http://{entradasServiceName}:{entradasServicePort}/v2"

    try:
        for entrada in entradas.find({"idWiki": idWiki}):
            id = entrada["_id"]
            # eliminamos las versiones de la entrada
            requests.delete(f"{url_base}/versiones?idEntrada={id}")
            # eliminamos la entrada
            requests.delete(f"{url_base}/entradas/{id}")
            ##enviar notificacion de que se ha eliminado una entrada
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar las entradas: {str(e)}"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# GET /entradas/<id>/wikis
@entradas_router.get("/{id}/wiki", response_model=Wiki)
def get_wiki_of_entry(id: str):
    try:
        entrada = entradas.find_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar la entrada: {str(e)}"
        )
    if not entrada:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")

    idWiki = entrada["idWiki"]
    wikiServiceName = os.getenv("ENDPOINT_WIKIS")
    wikiServicePort = os.getenv("SERVICE_WIKIS_PORT")
    if os.getenv("DOCKER"):
        url_base = "https://gateway:8000"
    else:
        url_base = f"http://{wikiServiceName}:{wikiServicePort}/v2"

    try:
        wiki = requests.get(f"{url_base}/wikis/{idWiki}").json()
        return wiki
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar la wiki: {str(e)}"
        )


# GET /entradas/<id>/comentarios
@entradas_router.get("/{id}/comentarios", response_model=ComentarioList)
def get_comentarios_for_entry(id: str):
    try:
        entrada = entradas.find_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar la entrada: {str(e)}"
        )
    if not entrada:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")

    comentariosServiceName = os.getenv("ENDPOINT_COMENTARIOS")
    comentariosPort = os.getenv("SERVICE_COMENTARIOS_PORT")
    if os.getenv("DOCKER"):
        url_base = "https://gateway:8000"
    else:
        url_base = f"http://{comentariosServiceName}:{comentariosPort}/v2"

    try:
        comentarios = requests.get(f"{url_base}/comentarios?idEntrada={id}").json()
        return comentarios
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar los comentarios: {str(e)}"
        )


# GET ultima version de una entrada
@entradas_router.get("/{id}/last-version")
def get_last_version_of_entry(id: str):
    try:
        version = versiones.find_one({"idEntrada": ObjectId(id)}, sort=[("fechaEdicion", pymongo.DESCENDING)])
        if version:
            return Version(**version).model_dump()
        else:
            raise HTTPException(status_code=404, detail="Version no encontrada")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar la version: {str(e)}"
        )

#Enviar notificacion

def send_notification(user_id: str, message: str, entrada_id: str):
    try:
        response = requests.post(
            f"{NOTIFICACIONES_SERVICE_URL}",
            json={"user_id": user_id, "message": message, "entrada_id": entrada_id},
            timeout=10  # Configura un timeout razonable
        )
        response.raise_for_status()  # Lanza excepción si hay error HTTP
        print("Notificación enviada:", response.status_code)
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error al enviar la notificación: {str(e)}"
        )
