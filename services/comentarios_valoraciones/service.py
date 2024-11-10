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
    try:
        idUsuario = request.args.get("idUsuarioRedactor")
        idEntrada = request.args.get("idEntrada")
        contenido = request.args.get("contenido")
        editado = request.args.get("editado")
        query = {}
    except Exception as e:
        return jsonify({"error": "Error al leer parámetros de consulta"}), 400

    if idUsuario:
        query["idUsuarioRedactor"] = ObjectId(idUsuario)
    if idEntrada:
        query["idEntrada"] = ObjectId(idEntrada)
    if contenido:
        query["contenido"] = {"$regex": contenido, "$options": "i"}
    if editado is not None:
        query["editado"] = editado.lower() == "true"

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
        return jsonify({"error": f"Error al convertir los datos del comentario: {str(e) }"}), 400
    try:
        comentarios.insert_one(datos)
    except Exception as e:
        return jsonify({"error": f"Error al convertir los datos del comentario: {e}"}), 400
    return jsonify({"message": f"Comentario creado correctamente"})


# DELETE /comentarios
@comentario_bp.route("/<id>", methods = ['DELETE'])
def delete_comments(id):
    try:
        filtro = {"_id": ObjectId(id)}
    except Exception as e:
        return jsonify({"error": f"Id no valida:{e}"}),400
    comentario = comentarios.find_one(filtro)
    if comentario:
        comentarios.delete_one(filtro)
        return jsonify({"message": f"Comentario con ID {id} eliminado correctamente"}), 200
    else:
        return jsonify({"error": "Comentario no encontrado"}), 404

@comentario_bp.route("/", methods = ['DELETE'])
def delete_comments_byIdEntrada():
    try:
        data = request.json
        idEntrada = data["idEntrada"]
        filtro = {"idEntrada": ObjectId(idEntrada)}
        comentarios.delete_many(filtro)
        return jsonify({"message": f"Comentarios de la entrada con ID {idEntrada} eliminados correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al eliminar los comentarios de la entrada: {e}"}), 400

# actualiza un comentario de una entrada
@comentario_bp.route("/<id>", methods = ['PUT'])
def update_comments(id):
    datos = request.json
    if not datos:
        return jsonify({"error": "Datos no válidos"}), 400
    try:
        filtro = {"_id": ObjectId(id)}
    except Exception as e:
        return jsonify({"error": f"Id invalido:{e}"}),400

    newData = {}
    print(datos)
    try:
        if datos.get("contenido"):
            newData["contenido"] = datos["contenido"]
        if datos.get("idUsuarioRedactor"):
            newData["idUsuarioRedactor"] = ObjectId(datos["idUsuarioRedactor"])
        if datos.get("idEntrada"):
            newData["idEntrada"] = ObjectId(datos["idEntrada"])
        if datos.get("editado"):
            newData["editado"] = datos["editado"]
    except Exception as e:
        return jsonify({"error": f"Error al convertir los ID: {str(e) }"}), 400
    try:
        comentarios.find_one_and_update(filtro, {"$set": newData})
    except Exception as e:
        return jsonify({"error": f"No se ha podido modificar el comentario: {e}"}), 400
    return jsonify({"message": f"Comentario con ID {id} actualizado correctamente"}), 200



   