from dotenv import load_dotenv
import pymongo
from bson import json_util
from bson.objectid import ObjectId
import os
from flask import Blueprint, jsonify, request
import json

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
wikis_bp = Blueprint("wikis_bp", __name__)

client = pymongo.MongoClient(MONGO_URL)
db = client.laWiki
wikis = db.wikis

#GET /wikis/

@wikis_bp.route("/", methods = ['GET'])
def get_wikis():
    nombre = request.args.get("nombre")

    if nombre: #Si tenemos idWiki buscamos parametrizadamente
        print("Busqueda parametrizada con idWiki")
        wiki = wikis.find({"nombre":{"$regex": nombre}})
    else:
        print("Busqueda general")
        wiki = wikis.find()

    wiki_json = json.loads(json_util.dumps(wiki))

    return jsonify(wiki_json)

#GET /wikis/<id>

@wikis_bp.route("/<id>", methods = ["GET"])
def get_wikis_byId(id):
    resultado = wikis.find_one({"_id":ObjectId(id)})  
    if resultado:
        print("Busqueda de wiki por id")
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    else:
        print(f"Error al obtener la wiki con id {id}")
        return {"error":"Wiki con id especificado no encontrada", "status_code":404}
        
#POST /wikis/

@wikis_bp.route("/", methods = ['POST'])
def create_wiki():
    datos = request.json
    
    if not datos or not datos["nombre"]:
        print("Error: Parametros de entrada inválidos")

    nombre = datos["nombre"]
    wiki_existente = wikis.find_one({"nombre":{"$regex": nombre}})

    if wiki_existente:
        return {"error": f"Wiki con nombre {nombre} ya existe", "status_code": 404}
    else:
        wikis.insert_one(datos)
        return f"<p>La wiki con el nombre {nombre} ha sido creada correctamente </p>"

#PUT /wikis/<id>       

@wikis_bp.route("/<id>", methods=["PUT"])
def update_wiki(id):
    data = request.json
    dataFormateada = {"$set":data}
    respuesta = wikis.find_one_and_update({"_id":ObjectId(id)},dataFormateada, return_document=True)
    print(respuesta)

    if respuesta is None:
        return {"error":f"Error al actualizar la wiki {id}", "status_code":404}
    else:
        return {"response":f"Wiki {respuesta["nombre"]} modificada correctamente", "status_code":200}
    
#DELETE /wikis/<id>

@wikis_bp.route("/<id>", methods=['DELETE'])
def delete_wiki(id):

    wiki = wikis.find_one({"_id":ObjectId(id)})
    nombre = wiki["nombre"]

    if not wiki:
        return f"La wiki con nombre {nombre} no existe, por lo tanto no se puede borrar"
    else:
        borrado = wikis.delete_one(wiki)
        if borrado == None:
            return "Borrado fallido"
        else:
            return "Borrado exitoso"

    
#GET /wikis/<id>/entradas

@wikis_bp.route("/<id>/entradas", methods=['GET'])
def get_entradas_byWiki(id):
    resultado = wikis.find_one({"_id":ObjectId(id)})
    if resultado:
        print("Busqueda de wiki por entradas")
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    else:
        print(f"Error al obtener las entradas de la wiki con id {id}")
        return {"error": "Entradas con id de la wiki especificado no encontrada", "status_code":404}
