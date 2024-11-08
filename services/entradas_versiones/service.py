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

version_bp = Blueprint('version_bp', __name__)

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWiki
entradas = db.entradas
wikis = db.wikis

# GET /entradas
@version_bp.route("/", methods=['GET'])
def get_entries():
    nombre = request.args.get("nombre")
    idWiki = request.args.get("idWiki")
    query = {}

    if nombre:
        query["nombre"] = {"$regex": nombre, "$options": "i"}
    if idWiki:
        query["idWiki"] = ObjectId(idWiki)

    entradas_data = entradas.find(query)
    entradas_json = json.loads(json_util.dumps(entradas_data))
    return jsonify(entradas_json)

# GET /entradas/<id>
@version_bp.route("/<id>", methods=['GET'])
def get_entry_by_id(id):
    entrada = entradas.find_one({"_id": ObjectId(id)})
    if entrada:
        return jsonify(json.loads(json_util.dumps(entrada)))
    else:
        return jsonify({"error": "Entrada no encontrada"}), 404

# POST /entradas
@version_bp.route("/", methods=['POST'])
def create_entry():
    datos = request.json
    if not datos:
        return jsonify({"error": "Datos no válidos"}), 400

    nombre = datos.get("nombre")
    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400

    try:
        datos["idVersionActual"] = ObjectId(datos["idVersionActual"])
        datos["idWiki"] = ObjectId(datos["idWiki"])
    except Exception as e:
        return jsonify({"error": f"Error al convertir los ID: {str(e)}"}), 400

    datos["slug"] = nombre.lower().replace(" ", "-")

    if entradas.find_one({"nombre": nombre}):
        return jsonify({"error": f"Ya existe una entrada con el nombre {nombre}"}), 400

    entradas.insert_one(datos)
    return jsonify({"message": f"Entrada '{nombre}' creada correctamente"}), 201

# PUT /entradas/<id>
@version_bp.route("/<id>", methods=['PUT'])
def update_entry(id):
    datos = request.json
    if not datos:
        return jsonify({"error": "Datos no válidos"}), 400

    filtro = {"_id": ObjectId(id)}
    entrada_existente = entradas.find_one(filtro)
    if not entrada_existente:
        return jsonify({"error": "Entrada no encontrada"}), 404

    entradas.update_one(filtro, {"$set": datos})
    return jsonify({"message": f"Entrada con ID {id} actualizada correctamente"}), 200

# DELETE /entradas/<id>
@version_bp.route("/<id>", methods=['DELETE'])
def delete_entry(id):
    filtro = {"_id": ObjectId(id)}
    entrada = entradas.find_one(filtro)
    if entrada:
        entradas.delete_one(filtro)
        return jsonify({"message": f"Entrada con ID {id} eliminada correctamente"}), 200
    else:
        return jsonify({"error": "Entrada no encontrada"}), 404

# DELETE /entradas/ : JSON {idWiki:"xxxxxxxxx"} Borra las entradas asociadas a una wiki
@version_bp.route("/", methods=['DELETE'])
def delete_entries_byWikiId():
    body = request.json
    if not body:
        return {"error": "Datos no válidos"}, 400

    if "idWiki" not in body:
        return {"error": "El campo idWiki es obligatorio"}, 400

    if not ObjectId.is_valid(body["idWiki"]):
        return {"error": "El campo idWiki no es un ObjectId válido"}, 400
    
    idWiki = body["idWiki"]

    result = entradas.delete_many({"idWiki":ObjectId(idWiki)})
    if result.deleted_count == 0:
        return {"message": "No se encontraron entradas asociadas a la wiki"}, 200
    else:
        return {"message": f"Se han eliminado {result.deleted_count} entradas asociadas a la wiki con ID {idWiki}"}, 200


# GET /entradas?nombre&idWiki
@version_bp.route("/", methods=['GET'])
def get_entries_by_name_and_idwiki():
    nombre = request.args.get("nombre")
    idWiki = request.args.get("idWiki")
    query = {}

    if nombre:
        query["nombre"] = {"$regex": nombre, "$options": "i"}
    if idWiki:
        query["idWiki"] = ObjectId(idWiki)

    entradas_data = entradas.find(query)
    entradas_json = json.loads(json_util.dumps(entradas_data))
    return jsonify(entradas_json)

# GET /entradas/<id>/wikis
@version_bp.route("/<id>/wikis", methods=['GET'])
def get_wikis_for_entry(id):
    entrada = entradas.find_one({"_id": ObjectId(id)})
    if entrada:
        wiki_id = entrada["idWiki"]
        wikiServiceName = os.getenv("ENDPOINT_WIKIS")
        wikiServicePort = os.getenv("SERVICE_WIKIS_PORT")
        if current_app.debug:
            wiki_raw = requests.get(f"http://localhost:{wikiServicePort}/wikis/{wiki_id}") # solo dev
        else:
            wiki_raw = requests.get(f"http://{wikiServiceName}:{wikiServicePort}/wikis/{wiki_id}")

        if wiki_raw.status_code == 200:
            return jsonify(wiki_raw.json()),200
        else:
            return {"error":"Error al obtener la wiki de la entrada", "status_code":400}
    else:
        return jsonify({"error": "Entrada no encontrada"}), 404
