import json
import os

import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Blueprint, current_app, jsonify, request
from datetime import datetime

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

versiones_bp = Blueprint('versiones_bp', __name__)

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWiki
versiones = db.versiones

# GET /versiones
@versiones_bp.route("/", methods=['GET'])
def get_versions():
    data = request.args
    query = {}

    try:
        if data:
            if data.get("idEntrada"):
                query["idEntrada"] = ObjectId(data.get("idEntrada"))
            if data.get("idWiki"):
                query["idWiki"] = ObjectId(data.get("idWiki"))
            if data.get("idUsuario"):
                query["idUsuario"] = ObjectId(data.get("idUsuario"))
            if data.get("contenido"):
                query["contenido"] = {"$regex": data.get("contenido"), "$options": "i"}
            if data.get("fechaEdicion"):
                query["fechaEdicion"] = {"$regex": data.get("fechaEdicion"), "$options": "i"}
    except Exception as e:
        return jsonify({"error": f"Datos no válidos. {e}"}), 400

    versiones_data = versiones.find(query)
    versiones_json = json.loads(json_util.dumps(versiones_data))
    return jsonify(versiones_json), 200

# GET /versiones/<id>
@versiones_bp.route("/<id>", methods=['GET'])
def get_versions_byId(id):
    query = {}

    try:
        query["_id"] = ObjectId(id)
    except Exception as e:
        return jsonify({"error": "Id de version no valido"}), 400

    versiones_data = versiones.find_one(query)
    if versiones_data:
        versiones_json = json.loads(json_util.dumps(versiones_data))
        return jsonify(versiones_json), 200
    else:
        return jsonify({"error": f"Version con id {id} no encontrada"}), 404

# POST /versiones
@versiones_bp.route("/", methods=['POST'])
def create_version():
    datos = request.json
    try:
        datos["idUsuario"] = ObjectId(datos["idUsuario"])
        datos["idEntrada"] = ObjectId(datos["idEntrada"])
        datos["contenido"] = datos["contenido"]
        datos["fechaEdicion"] = datetime.now()
    except Exception as e:
        return jsonify({"error": f"Datos no válidos. {e}"}), 400
    
    try:
        response = versiones.insert_one(datos)
        if response:
            return jsonify({"message": "Version creada correctamente"}), 201
    except Exception as e:
        return jsonify({"error": f"Error al insertar la version: {e}"}), 500


    return jsonify({"message": "Version creada correctamente"}), 201

@versiones_bp.route("/<id>", methods=['PUT'])
def update_version(id):
    datos = request.json
    if not datos:
        return jsonify({"error": "Datos no válidos"}), 400
    
    newValues = {}

    try:
        if datos.get("idWiki"):
            newValues["idWiki"] = ObjectId(datos["idWiki"])
        if datos.get("idUsuario"):
            newValues["idUsuario"] = ObjectId(datos["idUsuario"])
        if datos.get("idEntrada"):
            newValues["idEntrada"] = ObjectId(datos["idEntrada"])
        if datos.get("contenido"):
            newValues["contenido"] = datos["contenido"]
    except Exception as e:
        return jsonify({"error": f"Datos no válidos. {e}"}), 400
    if newValues:
        newValues["fechaEdicion"] = datetime.now()
    try:
        query = {"_id": ObjectId(id)}
    except Exception as e:
        return jsonify({"error": f"Id no valido. {e}"}), 400
    try:
        versiones.update_one(query, {"$set": newValues})
        return jsonify({"message": f"Version con id {id} actualizada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al actualizar la version: {e}"}), 500

@versiones_bp.route("/<id>", methods=['DELETE'])
def delete_version(id):
    try:
        query = {"_id": ObjectId(id)}
    except Exception as e:
        return jsonify({"error": f"Id invalida: {e}"})
    try:
        currentEntrada = versiones.find_one(query)
        idEntrada = currentEntrada["idEntrada"]
        if current_app.debug:
            requests.delete(f"http://localhost:{os.getenv("SERVICE_COMENTARIOS_PORT")}/comentarios/{idEntrada}")
        else:
            requests.delete(f"http://{os.getenv("ENDPOINT_COMENTARIOS")}:{os.getenv('SERVICE_COMENTARIOS_PORT')}/comentarios/{idEntrada}")
        versiones.find_one_and_delete(query)
        return jsonify({"message": f"Version con id {id} eliminada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al eliminar la version: {e}"}), 500

@versiones_bp.route("/", methods=['DELETE'])
def delete_versions_byEntradaId():
    body = request.json
    if not body:
        return jsonify({"error": "Datos no válidos"}), 400
    try:
        idEntrada = ObjectId(body["idEntrada"])
    except Exception as e:
        return jsonify({"error": f"Id de entrada no válido. {e}"}), 400

    query = {"idEntrada": idEntrada}

    try:
        versiones.delete_many(query)
        return jsonify({"message": f"Versiones de la entrada con id {idEntrada} eliminadas correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al eliminar las versiones: {e}"}), 500