import json
import os

import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query

from models.comentario import (ComentarioFilter, ComentarioList, ComentarioNew,
                               ComentarioUpdate)
from models.entrada import EntradaId

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

comentarios_bp = APIRouter(
    prefix="/v2/comentarios",
    tags=['comentarios']
)


# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
comentarios = db.comentarios

# MicroServicio de COMENTARIOS

# GET /comentarios
@comentarios_bp.get("/")
def view_comments(filtro: ComentarioFilter = Depends()):
    print(filtro.model_dump())
    comentarios_data = comentarios.find(filtro.model_dump(exclude_none=True))
    return ComentarioList(comentarios=[comentario for comentario in comentarios_data]).model_dump(exclude_none=True)

# POST /comentarios
@comentarios_bp.post("/")
def create_comments(nuevoComentario: ComentarioNew):
    try:
        comentarios.insert_one(nuevoComentario.model_dump(exclude_none=True))
    except Exception as e:
        return {"error": f"Error al convertir los datos del comentario: {e}"}, 400
    return {"message": "Comentario creado correctamente"}, 201
#
#
# # DELETE /comentarios
@comentarios_bp.delete("/{id}")
def delete_comments(id):
    try:
        filtro = {"_id": ObjectId(id)}
    except Exception as e:
        return {"error": f"Id invalido:{e}"}, 400
    comentario = comentarios.find_one(filtro)
    if comentario:
        comentarios.delete_one(filtro)
        return {"message": f"Comentario con ID {id} eliminado correctamente"}, 200
    else:
        return {"error": "Comentario no encontrado"}, 404
#
@comentarios_bp.delete("/")
def delete_comments_byIdEntrada(idEntrada: EntradaId):
    try:
        comentarios.delete_many(idEntrada.model_dump(exclude_none=True))
        return {"message": f"Comentarios de la entrada con ID {idEntrada.idEntrada} eliminados correctamente"}, 200
    except Exception as e:
        return {"error": f"Error al eliminar los comentarios de la entrada: {e}"}, 400
#
# actualiza un comentario de una entrada
@comentarios_bp.put("/{id}")
def update_comments(id, newEntrada:ComentarioUpdate):
    try:
        filtro = {"_id": ObjectId(id)}
    except Exception as e:
        return {"error": f"Id invalido:{e}"}, 400

    try:
        newData = newEntrada.model_dump(exclude_none=True)
        res = comentarios.find_one_and_update(filtro, {"$set": newData})

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al actualizar el comentario: {e}")

    if res is None:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    raise HTTPException(status_code=200, detail="Comentario actualizado correctamente")
