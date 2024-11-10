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

entradas_bp = Blueprint('entradas_bp', __name__)

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWiki
entradas = db.entradas

# GET /entradas
@entradas_bp.route("/", methods=['GET'])
def get_entries():
    try:
        nombre = request.args.get("nombre")
        idWiki = request.args.get("idWiki")
        query = {}
    except Exception as e:
        return jsonify({"error": "Error al leer parámetros de consulta"}), 400

    try:
        if nombre:
            query["nombre"] = {"$regex": nombre, "$options": "i"}
        if idWiki:
            query["idWiki"] = ObjectId(idWiki)
    except Exception as e:
        return jsonify({"error": f"Error al convertir los ID: {str(e)}"}), 400

    try:
        entradas_data = entradas.find(query)
        entradas_json = json.loads(json_util.dumps(entradas_data))
        return jsonify(entradas_json), 200
    except Exception as e:
        return jsonify({"error": f"Error al buscar las entradas: {str(e)}"}), 400

# GET /entradas/<id>
@entradas_bp.route("/<id>", methods=['GET'])
def get_entry_by_id(id):
    try:
        entrada = entradas.find_one({"_id": ObjectId(id)})
        if entrada:
            return jsonify(json.loads(json_util.dumps(entrada))), 200
        else:
            return jsonify({"error": "Entrada no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": f"Error al buscar la entrada: {str(e)}"}), 400

# POST /entradas
@entradas_bp.route("/", methods=['POST'])
def create_entry():
    try:
        datos = request.json
    except Exception as e:
        return jsonify({"error": "Error al leer los datos"}), 400
    if not datos:
        return jsonify({"error": "Datos no válidos"}), 400

    try:
        datos["idVersionActual"] = ObjectId(datos["idVersionActual"])
        datos["idWiki"] = ObjectId(datos["idWiki"])
        nombre = datos.get("nombre")
        if not nombre:
            return jsonify({"error": "El nombre es obligatorio"}), 400

        datos["slug"] = nombre.lower().replace(" ", "-")
    except Exception as e:
        return jsonify({"error": f"Error al convertir los ID: {str(e)}"}), 400

    try:
        if entradas.find_one({"nombre": nombre}):
            return jsonify({"error": f"Ya existe una entrada con el nombre {nombre}"}), 400
        entradas.insert_one(datos)
        return jsonify({"message": f"Entrada '{nombre}' creada correctamente"}), 201
    except Exception as e:
        return jsonify({"error": f"Error al buscar la entrada: {str(e)}"}), 400

# PUT /entradas/<id>
@entradas_bp.route("/<id>", methods=['PUT'])
def update_entry(id):
    try:
        datos = request.json
        if not datos:
            return jsonify({"error": "Datos no válidos"}), 400

        filtro = {"_id": ObjectId(id)}
        entrada_existente = entradas.find_one(filtro)
        if not entrada_existente:
            return jsonify({"error": "Entrada no encontrada"}), 404
        if datos.get("nombre"):
            datos["slug"] = datos["nombre"].lower().replace(" ", "-")

        entradas.update_one(filtro, {"$set": datos})
        return jsonify({"message": f"Entrada con ID {id} actualizada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al actualizar la entrada: {str(e)}"}), 400

# DELETE /entradas/<id>
@entradas_bp.route("/<id>", methods=['DELETE'])
def delete_entry(id):
    try:
        filtro = {"_id": ObjectId(id)}
        entrada = entradas.find_one(filtro)
        if entrada:
            entradas.delete_one(filtro)
            return jsonify({"message": f"Entrada con ID {id} eliminada correctamente"}), 200
        else:
            return jsonify({"error": "Entrada no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": f"Error al eliminar la entrada: {str(e)}"}), 400

# DELETE /entradas/ : JSON {idWiki:"xxxxxxxxx"} Borra las entradas asociadas a una wiki
@entradas_bp.route("/", methods=['DELETE'])
def delete_entries_byWikiId():
    body = request.json
    if not body:
        return jsonify({"error": "Datos no válidos"}), 400

    try:
        idWiki = body["idWiki"]
    except Exception as e:
        return jsonify({"error": f"Error al convertir el ID: {str(e)}"}), 400

    idEntradasABorrar = []
    try:
        for entradaByWiki in entradas.find({"idWiki": ObjectId(idWiki)}):
            idE = json.loads(json_util.dumps(entradaByWiki))["_id"]["$oid"]
            idEntradasABorrar.append(idE)
        print(idEntradasABorrar)

        if len(idEntradasABorrar) > 0:
            with current_app.test_client() as client:
                for idEntrada in idEntradasABorrar:
                    # client.delete("/versiones", json={"idEntrada": idEntrada})
                    if current_app.debug:
                        requests.delete(f"http://localhost:{os.getenv("SERVICE_ENTRADAS_PORT")}/versiones",json={"idEntrada": idEntrada})
                    else:
                        requests.delete(f"http://{os.getenv("ENDPOINT_ENTRADAS")}:{os.getenv("SERVICE_ENTRADAS_PORT")}/versiones",json={"idEntrada": idEntrada})
                    client.delete(f"/entradas/{idEntrada}")
    except Exception as e:
        return jsonify({"error": f"Error al buscar las entradas: {str(e)}"}), 400

    return jsonify({"message": f"Se han eliminado las entradas y versiones asociadas a la wiki con ID {idWiki}"}), 200


# GET /entradas/<id>/wikis
@entradas_bp.route("/<id>/wiki", methods=['GET'])
def get_wikis_for_entry(id):
    try:
        entrada = entradas.find_one({"_id": ObjectId(id)})
    except Exception as e:
        return jsonify({"error": f"Error al buscar la entrada: {str(e)}"}), 400
    if entrada:
        wiki_id = entrada["idWiki"]
        wikiServiceName = os.getenv("ENDPOINT_WIKIS")
        wikiServicePort = os.getenv("SERVICE_WIKIS_PORT")
        if current_app.debug:
            wiki_raw = requests.get(f"http://localhost:{wikiServicePort}/wikis/{wiki_id}") # solo dev
        else:
            wiki_raw = requests.get(f"http://{wikiServiceName}:{wikiServicePort}/wikis/{wiki_id}")

        if wiki_raw.status_code == 200:
            return jsonify(wiki_raw.json()), 200
        else:
            return jsonify({"error":"Error al obtener la wiki de la entrada"}), 400
    else:
        return jsonify({"error": "Entrada no encontrada"}), 404

# GET /entradas/<id>/comentarios
@entradas_bp.route("/<id>/comentarios", methods=['GET'])
def get_comentarios_for_entry(id):
    try:
        entrada = entradas.find_one({"_id": ObjectId(id)})
        if entrada:
            slug = entrada["slug"]
            # buscar todos los comentarios de la entrada
            comentariosServiceName = os.getenv("ENDPOINT_COMENTARIOS")
            comentariosPort = os.getenv("SERVICE_COMENTARIOS_PORT")

            if current_app.debug:
                url = f"http://localhost:{comentariosPort}/comentarios?idEntrada={id}"
            else:
                url = f"http://{comentariosServiceName}:{comentariosPort}/comentarios?idEntrada={id}"

            comentarios_raw = requests.get(url)
            if comentarios_raw.status_code == 200:
                return jsonify(comentarios_raw.json()), 200
            else:
                return jsonify({"error":"Error al obtener los comentarios de la entrada"}), 400
        else:
            return jsonify({"error": "Entrada no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": f"Error al buscar la entrada: {str(e)}"}), 400
