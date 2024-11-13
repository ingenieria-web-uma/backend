import json
import os

import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Blueprint, current_app, jsonify, request

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

valoraciones_bp = Blueprint('valoraciones_bp', __name__)

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
valoraciones = db.valoraciones

# GET /valoraciones
@valoraciones_bp.route("/", methods=['GET'])
def get_evaluations():
    try:
        idUsuarioRedactor = request.args.get("idUsuarioRedactor")
        idUsuarioValorado = request.args.get("idUsuarioValorado")
        nota = request.args.get("nota")
        query = {}

        if idUsuarioRedactor:
            query["idUsuarioRedactor"] = ObjectId(idUsuarioRedactor)
        if idUsuarioValorado:
            query["idUsuarioValorado"] = ObjectId(idUsuarioValorado)
        if nota:
            query["nota"] = int(nota)

        valoraciones_data = valoraciones.find(query)
        valoraciones_json = json.loads(json_util.dumps(valoraciones_data))
        return jsonify(valoraciones_json), 200
    except Exception as e:
        return jsonify({"error": f"Error al buscar las valoraciones: {str(e)}"}), 400

# GET /valoraciones/<id>
@valoraciones_bp.route("/<id>", methods=['GET'])
def get_evaluation_by_id(id):
    try:
        valoracion = valoraciones.find_one({"_id": ObjectId(id)})
        if valoracion:
            return jsonify(json.loads(json_util.dumps(valoracion))), 200
        else:
            return jsonify({"error": "Valoración no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": f"Error al buscar la valoración: {str(e)}"}), 400

# POST /valoraciones
@valoraciones_bp.route("/", methods=['POST'])
def create_evaluation():
    try:
        datos = request.json
        if not datos:
            return jsonify({"error": "Datos no válidos"}), 400

        datos["idUsuarioRedactor"] = ObjectId(datos["idUsuarioRedactor"])
        datos["idUsuarioValorado"] = ObjectId(datos["idUsuarioValorado"])
        nota = datos.get("nota")

        if not nota:
            return jsonify({"error": "La nota es obligatoria"}), 400

        valoracion_existente = valoraciones.find_one({
            "idUsuarioRedactor": datos["idUsuarioRedactor"],
            "idUsuarioValorado": datos["idUsuarioValorado"]
        })

        if valoracion_existente:
            return jsonify({"error": "Ya existe una valoración para este usuario"}), 400

        valoraciones.insert_one(datos)

        return jsonify({"message": f"Valoración creada correctamente"}), 201
    except Exception as e:
        return jsonify({"error": f"Error al crear la valoración: {str(e)}"}), 400

# PUT /valoraciones/<id>
@valoraciones_bp.route("/<id>", methods=['PUT'])
def update_evaluation(id):
    try:
        datos = request.json
        if not datos:
            return jsonify({"error": "Datos no válidos"}), 400

        filtro = {"_id": ObjectId(id)}
        valoracion_existente = valoraciones.find_one(filtro)
        if not valoracion_existente:
            return jsonify({"error": "Valoración no encontrada"}), 404

        valoraciones.update_one(filtro, {"$set": datos})
        return jsonify({"message": f"Valoración con ID {id} actualizada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al actualizar la valoracion: {str(e)}"}), 400

# DELETE /valoraciones/<id>
@valoraciones_bp.route("/<id>", methods=['DELETE'])
def delete_evaluation(id):
    try:
        filtro = {"_id": ObjectId(id)}
        valoracion = valoraciones.find_one(filtro)
        if valoracion:
            valoraciones.delete_one(filtro)
            return jsonify({"message": f"Valoración con ID {id} eliminada correctamente"}), 200
        else:
            return jsonify({"error": "Valoración no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": f"Error al eliminar la valoración: {str(e)}"}), 400