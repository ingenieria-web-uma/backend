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
        return jsonify({"error": f"Error al insertar la version: {e}"}), 400

    return jsonify({"message": "Version creada correctamente"}), 201

# PUT /versiones/<id>
@versiones_bp.route("/<id>", methods=['PUT'])
def update_version(id):
    datos = request.json
    if not datos:
        return jsonify({"error": "Datos no válidos"}), 400

    try:
        filtro = {"_id": ObjectId(id)}
        versiones.find_one(filtro)
    except Exception as e:
        return jsonify({"error": f"Version no encontrada"}), 404

    try:
        if datos.get("idUsuario"):
            datos["idUsuario"] = ObjectId(datos["idUsuario"])
        if datos.get("idEntrada"):
            datos["idEntrada"] = ObjectId(datos["idEntrada"])
        if datos.get("contenido"):
            datos["contenido"] = datos["contenido"]
    except Exception as e:
        return jsonify({"error": f"Datos no válidos. {e}"}), 400

    if datos:
        datos["fechaEdicion"] = datetime.now()

    try:
        versiones.update_one(filtro, {"$set": datos})
        return jsonify({"message": f"Version con id {id} actualizada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al actualizar la version: {e}"}), 400

# DELETE /versiones/<id>
@versiones_bp.route("/<id>", methods=['DELETE'])
def delete_version(id):
    try:
        filtro = {"_id": ObjectId(id)}
        version = versiones.find_one(filtro)
        if version:
            versiones.delete_one(filtro)
            return jsonify({"message": f"Versión con ID {id} eliminada correctamente"}), 200
        else:
            return jsonify({"error": "Versión no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": f"Error al eliminar la versión: {str(e)}"}), 400

# DELETE /versiones/
@versiones_bp.route("/", methods=['DELETE'])
def delete_versions_byEntradaId():
    body = request.json
    if not body:
        return jsonify({"error": "Datos no válidos"}), 400

    try:
        idEntrada = body["idEntrada"]
    except Exception as e:
        return jsonify({"error": f"Id de entrada no válido. {e}"}), 400

    idVersionesABorrar = []
    try:
        for versionByEntrada in versiones.find({"idEntrada": ObjectId(idEntrada)}):
            idV = json.loads(json_util.dumps(versionByEntrada))["_id"]["$oid"]
            idVersionesABorrar.append(idV)
        print(idVersionesABorrar)

        if len(idVersionesABorrar) > 0:
            with current_app.test_client() as client:
                for idVersion in idVersionesABorrar:
                    if current_app.debug:
                        requests.delete(f"http://localhost:{os.getenv("SERVICE_ENTRADAS_PORT")}/entradas", json={"idVersion": idVersion})
                    else:
                        requests.delete(f"http://{os.getenv("ENDPOINT_ENTRADAS")}:{os.getenv("SERVICE_ENTRADAS_PORT")}/entradas", json={"idVersion": idVersion})
                    client.delete(f"/versiones/{idVersion}")
    except Exception as e:
        return jsonify({"error": f"Error al buscar las versiones: {str(e)}"}), 400

    return jsonify({"message": f"Se han eliminado las versiones asociadas a la entrada con ID {idEntrada}"}), 200