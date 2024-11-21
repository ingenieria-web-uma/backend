import json
import os

import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, Query

from models.comentario import ComentarioFilter, ComentarioList, ComentarioNew

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
        comentarios.insert_one(nuevoComentario.model_dump())
    except Exception as e:
        return {"error": f"Error al convertir los datos del comentario: {e}"}, 400
    return {"message": "Comentario creado correctamente"}, 201
#
#
# # DELETE /comentarios
# @comentarios_bp.route("/<id>", methods = ['DELETE'])
# def delete_comments(id):
#     try:
#         filtro = {"_id": ObjectId(id)}
#     except Exception as e:
#         return jsonify({"error": f"Id no valida:{e}"}),400
#     comentario = comentarios.find_one(filtro)
#     if comentario:
#         comentarios.delete_one(filtro)
#         return jsonify({"message": f"Comentario con ID {id} eliminado correctamente"}), 200
#     else:
#         return jsonify({"error": "Comentario no encontrado"}), 404
#
# @comentarios_bp.route("/", methods = ['DELETE'])
# def delete_comments_byIdEntrada():
#     try:
#         data = request.json
#         idEntrada = data["idEntrada"]
#         filtro = {"idEntrada": ObjectId(idEntrada)}
#         comentarios.delete_many(filtro)
#         return jsonify({"message": f"Comentarios de la entrada con ID {idEntrada} eliminados correctamente"}), 200
#     except Exception as e:
#         return jsonify({"error": f"Error al eliminar los comentarios de la entrada: {e}"}), 400
#
# # actualiza un comentario de una entrada
# @comentarios_bp.route("/<id>", methods = ['PUT'])
# def update_comments(id):
#     datos = request.json
#     if not datos:
#         return jsonify({"error": "Datos no válidos"}), 400
#     try:
#         filtro = {"_id": ObjectId(id)}
#     except Exception as e:
#         return jsonify({"error": f"Id invalido:{e}"}),400
#
#     newData = {}
#     print(datos)
#     try:
#         if datos.get("contenido"):
#             newData["contenido"] = datos["contenido"]
#         if datos.get("idUsuarioRedactor"):
#             newData["idUsuarioRedactor"] = ObjectId(datos["idUsuarioRedactor"])
#         if datos.get("idEntrada"):
#             newData["idEntrada"] = ObjectId(datos["idEntrada"])
#         if datos.get("editado"):
#             newData["editado"] = datos["editado"]
#     except Exception as e:
#         return jsonify({"error": f"Error al convertir los ID: {str(e) }"}), 400
#     try:
#         comentarios.find_one_and_update(filtro, {"$set": newData})
#     except Exception as e:
#         return jsonify({"error": f"No se ha podido modificar el comentario: {e}"}), 400
#     return jsonify({"message": f"Comentario con ID {id} actualizado correctamente"}), 200
