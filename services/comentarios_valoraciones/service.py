import json
import os

import pymongo
import requests
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
comentarios = db.comentarios

# MicroServicio de COMENTARIOS

# GET /comentarios
@comentario_bp.route("/", methods = ['GET'])
def view_comments():
    idUsuario = request.args.get("idUsuarioRedactor")
    idEntrada = request.args.get("idEntrada")
    contenido = request.args.get("contenido")
    query = {}

    if idUsuario:
        query["idUsuarioRedactor"] = {"$regex": idUsuario, "$options": "i"}
    if idEntrada:
        query["idEntrada"] = ObjectId(idEntrada)
    if contenido:
        query["contenido"] = ObjectId(contenido)

    comentarios_data = comentarios.find(query)
    comentarios_json = json.loads(json_util.dumps(comentarios_data))
    return jsonify(comentarios_json)

# POST /comentarios
@comentario_bp.route("/", methods = ['POST'])
def create_comments():
    datos = request.json
    if not datos:
        return jsonify({"error": "Datos no válidos"}), 400
    try:
        datos["idUsuarioRedactor"] = ObjectId(datos["idUsuarioRedactor"])
        datos["idEntrada"] = ObjectId(datos["idEntrada"])
    except Exception as e:
        return jsonify({"error": f"Error al convertir los ID: {str(e) }"}), 400
    
    comentarios.insert_one(datos)
    return jsonify({"message": f"Comentario creado correctamente"})


# DELETE /comentarios
@comentario_bp.route("/", methods = ['DELETE'])
def delete_comments(id):
    filtro = {"_id": ObjectId(id)}
    comentario = comentario.find_one(filtro)
    if comentario:
        comentario.delete_one(filtro)
        return jsonify({"message": f"Comentario con ID {id} eliminado correctamente"}), 200
    else:
        return jsonify({"error": "Comentario no encontrado"}), 404

# actualiza un comentario de una entrada
@comentario_bp.route("/", methods = ['PUT'])
def update_comments(id):
    datos = request.json
    if not datos:
        return jsonify({"error": "Datos no válidos"}), 400
    filtro = {"_id": ObjectId(id)}
    entrada_existente = comentarios.find_one(filtro)
    if not entrada_existente:
        return jsonify({"error": "Entrada no encontrada"}), 404
    
    comentarios.update_one(filtro, {"$set": datos})
    return jsonify({"message": f"Comentario con ID {id} actualizado correctamente"}), 200



   