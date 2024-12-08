import os

import pymongo
import requests
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException

from models.comentario import (Comentario, ComentarioFilter, ComentarioList,
                               ComentarioNew, ComentarioUpdate)
from models.entrada import EntradaId

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

comentarios_bp = APIRouter(prefix="/v2/comentarios", tags=["comentarios"])


SERVICE_NOTIFICACIONES_PORT = os.getenv("SERVICE_NOTIFICACIONES_PORT")
ENDPOINT_NOTIFICACIONES = os.getenv("ENDPOINT_NOTIFICACIONES")

if os.getenv("DOCKER"):
    NOTIFICACIONES_SERVICE_URL = "http://gateway:8000/notificaciones"
else:
    NOTIFICACIONES_SERVICE_URL = f"http://localhost:{SERVICE_NOTIFICACIONES_PORT}/{ENDPOINT_NOTIFICACIONES}"


# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
comentarios = db.comentarios

# MicroServicio de COMENTARIOS


# GET /comentarios
@comentarios_bp.get("/")
def view_comments(filtro: ComentarioFilter = Depends()):
    filter = filtro.to_mongo_dict(exclude_none=True)
    comentarios_data = comentarios.find(filter).sort("fechaCreacion", pymongo.DESCENDING)
    return ComentarioList(
        comentarios=[comentario for comentario in comentarios_data]
    ).model_dump(exclude_none=True)


# POST /comentarios
@comentarios_bp.post("/")
def create_comments(nuevoComentario: ComentarioNew):
    try:
        ## Enviar notificación
        comentarioModel = nuevoComentario.model_dump()
        user_id = comentarioModel["idUsuario"]
        message = f"Nuevo comentario: {comentarioModel['contenido']}"
        entrada_id = comentarioModel["idEntrada"]

        entrada = requests.get(f"http://gateway:8000/entradas/{entrada_id}")
        entrada = entrada.json()
        usuario = entrada["idUsuario"]
        if usuario != user_id:
            send_notification(user_id, message, entrada_id)
        
        res = comentarios.insert_one(nuevoComentario.to_mongo_dict(exclude_none=True))
        print(res.inserted_id)
        if res.inserted_id:
            return Comentario(_id=res.inserted_id, **nuevoComentario.model_dump()).model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al crear el comentario: {str(e)}"
        )

# DELETE /comentarios
@comentarios_bp.delete("/{id}")
def delete_comments(id):
    try:
        filtro = {"_id": ObjectId(id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Id invalido:{e}")
    comentario = comentarios.find_one(filtro)
    if comentario:
        comentarios.delete_one(filtro)
        raise HTTPException(
            status_code=200, detail="Comentario eliminado correctamente"
        )
    else:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")


# Elimina un comentario de una entrada
@comentarios_bp.delete("/")
def delete_comments_byIdEntrada(idEntrada: EntradaId):
    try:
        res = comentarios.delete_many(idEntrada.to_mongo_dict(exclude_none=True))
        raise HTTPException(
            status_code=200,
            detail=f"Borrados {res.deleted_count} comentarios de la entrada con ID {idEntrada.idEntrada}",
        )
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al eliminar los comentarios de la entrada: {str(e)}",
        )


# Actualiza un comentario de una entrada
@comentarios_bp.put("/{id}")
def update_comments(id, newEntrada: ComentarioUpdate):
    try:
        filtro = {"_id": ObjectId(id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Id invalido:{e}")

    try:
        newData = newEntrada.to_mongo_dict(exclude_none=True)
        res = comentarios.find_one_and_update(filtro, {"$set": newData})

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al actualizar el comentario: {e}"
        )

    if res is None:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    raise HTTPException(status_code=200, detail="Comentario actualizado correctamente")

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
