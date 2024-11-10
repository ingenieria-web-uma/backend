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
wikis_bp = Blueprint("wikis_bp", __name__)

client = pymongo.MongoClient(MONGO_URL)
db = client.laWiki
wikis = db.wikis

#GET /wikis/

@wikis_bp.route("/", methods = ['GET'])
def get_wikis():
    try:
        nombre = request.args.get("nombre")
    except Exception as e:
        return jsonify({"error": "Error al leer parámetros de consulta"}), 400
    try:
        if nombre: #Si tenemos nombre buscamos parametrizadamente
            print("Busqueda parametrizada con nombre")
            wiki = wikis.find({"nombre":{"$regex": nombre}})
        else:
            print("Busqueda general")
            wiki = wikis.find()
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        wiki_json = json.loads(json_util.dumps(wiki))
        return jsonify(wiki_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400

#GET /wikis/<id>

@wikis_bp.route("/<id>", methods = ["GET"])
def get_wikis_byId(id):
    try:
        resultado = wikis.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return jsonify({"error": "ID inválido"}), 400
    if resultado:
        print("Busqueda de wiki por id")
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    else:
        print(f"Error al obtener la wiki con id {id}")
        return jsonify({"error":"Wiki con id especificado no encontrada"}), 404

#POST /wikis/

@wikis_bp.route("/", methods = ['POST'])
def create_wiki():
    datos = request.json

    if not datos or not datos["nombre"]:
        print("Error: Parametros de entrada inválidos")

    nombre = datos["nombre"]
    wiki_existente = wikis.find_one({"nombre":{"$regex": nombre}})

    if wiki_existente:
        return jsonify({"error": f"Wiki con nombre {nombre} ya existe"}), 404
    else:
        wikis.insert_one(datos)
        return jsonify({"response": f"Wiki {nombre} creada correctamente"}), 201

#PUT /wikis/<id>

@wikis_bp.route("/<id>", methods=["PUT"])
def update_wiki(id):
    data = request.json
    dataFormateada = {"$set":data}
    respuesta = wikis.find_one_and_update({"_id":ObjectId(id)}, dataFormateada, return_document=True)
    print(respuesta)

    if respuesta is None:
        return jsonify({"error":f"Error al actualizar la wiki {id}"}), 404
    else:
        return jsonify({"response":f"Wiki {respuesta["nombre"]} modificada correctamente"}), 200

#DELETE /wikis/<id>

@wikis_bp.route("/<id>", methods=['DELETE'])
def delete_wiki(id):

    try:
        wiki = wikis.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"La wiki {id} no existe, por lo tanto no se puede borrar", 404
        #borrar entradas de la wiki
    headers = {"Content-Type":"application/json"}
    if current_app.debug:
        response = requests.delete(f"http://localhost:{os.getenv("SERVICE_ENTRADAS_PORT")}/entradas",headers=headers, json={"idWiki":id})
    else:
        response = requests.delete(f"http://{os.getenv("ENDPOINT_ENTRADAS")}:{os.getenv("SERVICE_ENTRADAS_PORT")}/entradas", headers=headers,json={"idWiki":id})


    if response.status_code != 200:
        return "Error al eliminar las entradas relacionadas a la wiki", 400

    try:
        borrado = wikis.delete_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"Error al borrar la wiki {id}", 400
    if borrado.deleted_count == 0:
        return f"La wiki {id} no existe, por lo tanto no se puede borrar", 200

    return "La wiki ha sido borrada con éxito", 200


#GET /wikis/<id>/entradas

@wikis_bp.route("/<id>/entradas", methods=['GET'])
def get_entradas_byWiki(id):
    nombreServicio= os.getenv("ENDPOINT_ENTRADAS")
    puertoServicio= os.getenv("SERVICE_ENTRADAS_PORT")
    if current_app.debug:
        url = f"http://localhost:{puertoServicio}/entradas/?idWiki={id}"
    else:
        url = f"http://{nombreServicio}:{puertoServicio}/entradas/?idWiki={id}"
    resultado = requests.get(url)
    if resultado.status_code != 200:
        return jsonify({"error":"No se ha podido solicitar las entradas de la wiki"}), 404
    else:
        return jsonify(resultado.json())
