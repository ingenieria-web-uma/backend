import json
import os

import pymongo
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

comentario_bp = Blueprint('comentario_bp', __name__)

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWiki
coleccion = db.entradas
comentarios = db.comentarios

# MicroServicio de COMENTARIOS

# obtener todos los comentarios de un slug específico
@comentario_bp.route("/<slug>/comments", methods = ['GET'])
def view_comments(slug):
    nombre = slug
    entrada = coleccion.find_one({"slug": nombre})
    if not entrada:
        return jsonify({"error": "Entrada no encontrada"}), 400 #cambiar cuando sepamos el formato que vamos a usar
    idEntrada = entrada["_id"]
    comentarios_slug = comentarios.find({"idEntrada" : idEntrada})
    comentarios_json = json.loads(json_util.dumps(comentarios_slug))
    return jsonify(comentarios_json)

# insertar un comentario a una entrada especifica
@comentario_bp.route("/<slug>/comments", methods = ['POST'])
def create_comments(slug):
    nombre = slug
    entrada = coleccion.find_one({"slug": nombre})
    if not entrada:
        return jsonify({"error": "Entrada no encontrada"}), 404
    
    idEntrada = entrada["_id"]
    datos = request.json

    if datos:
        datos["idEntrada"] = idEntrada
        comentarios.insert_one(datos)
        return f"<p>El comentario ha sido publicado correctamente</p>"
    else:
        return jsonify({"error": "Datos no validos"}), 400

# borrar un comentario de una entrada buscando por id del comentario.
@comentario_bp.route("/<slug>/comments", methods = ['DELETE'])
def delete_comments(slug):
    datos = request.json
    if datos:
       result = comentarios.find_one_and_delete({"_id":ObjectId(datos["id"])})
       if result:
        return f"Comentario {datos["id"]} borrado con exito"
       else:
           return jsonify({"error": "Comentario no encontrado"}), 400
    else:
        return f"Comentario {datos["id"]} no encontrado. No se ha podido borrar."

# actualiza un comentario de una entrada
@comentario_bp.route("/<slug>/comments", methods = ['PUT'])
def update_comments(slug):
    idFiltro = request.json["id"]
    if not idFiltro:
        return jsonify({"error", "ID de comentario no proporcionado"}), 400
    datos = request.json
    del datos["id"]
    actualizado = {"$set": datos}
    if datos:
        comentarios.find_one_and_update({"_id":ObjectId(idFiltro)}, actualizado)
        return f"Comentario {idFiltro} actualizado con exito"
    else:
        return f"Comentario {idFiltro} no encontrado. No se ha podido actualizar"