import os

import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException

from models.comentario import (Comentario, ComentarioFilter, ComentarioList,
                               ComentarioNew, ComentarioUpdate)
from models.entrada import EntradaId

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

comentarios_bp = APIRouter(prefix="/v2/comentarios", tags=["comentarios"])


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
        res = comentarios.insert_one(nuevoComentario.to_mongo_dict(exclude_none=True))
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
