import json
import os

import pymongo
from bson import json_util
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

version_bp = Blueprint('version_bp', __name__)

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWiki
coleccion = db.entradas
comentarios = db.comentarios

#Cuando entramos a /entradas accederemos aqui

# MicroServicio de VERSIONES

# get entradas. ?titulo=<entrada> para filtrar por similitud en nombre (cRud)
@version_bp.route("/", methods = ['GET'])
def get_entry():
    titulo = request.args.get("titulo")
    print(titulo)

    if titulo:
        print("busqueda parametrizada")
        entradas = coleccion.find({"nombreEntrada":{"$regex": titulo}})
    else:
        print("busqueda normal")
        entradas = coleccion.find()

    entradas_json = json.loads(json_util.dumps(entradas))
    return jsonify(entradas_json)

# actualiza entradas buscando coincidencias por nombreEntrada (crUd)
@version_bp.route("/<nombreEntrada>", methods = ['PUT'])
def update_entry(nombreEntrada):
    datos = request.json # recoge los datos del body

    filtro = {"nombreEntrada": nombreEntrada}
    actualizacion = {"$set": datos}
    coleccion.update_one(filtro, actualizacion)

    return f"<p>La entrada con nombreEntrada {nombreEntrada} se ha actualizado correctamente</p>"

# DELETE, es decir (cruD), se usa con el envio de un json y busca en la base de datos de entradas para borrarlo, en caso de existir lo borra, en su defecto devuelve un error
@version_bp.route("/", methods = ['DELETE'])
def delete_entry():
    datos = request.json
    resultado = coleccion.find_one_and_delete(datos)
    if resultado:
        return f"<p>La entrada con nombreEntrada {datos['nombreEntrada']} se ha eliminado correctamente</p>"
    else:
        return f"<p>La entrada con nombreEntrada {datos['nombreEntrada']} no se ha encontrado</p>"

# POST, es decir (Crud), se usa con el envio de un json y controla que no sea nulo o vacio y
@version_bp.route("/", methods = ['POST'])
def create_entry():
    datos = request.json
    if not datos:
        return "<p>Error al insertar una nueva entrada. Los valores no son válidos</p>"

    nombre = datos["nombre"]
    datos["slug"] = nombre.lower().replace(" ", "-")

    #Manejo de nulos
    if nombre == None:
        return f"<p>La entrada no es valida</p>"

    if nombre: #Si existe una entrada con nombreEntrada => t buscamos parametrizadamente, si es null devolvemos todos y si no existe pues error
        entrada = coleccion.find_one({"nombre": nombre})

        if not entrada:
            coleccion.insert_one(datos)
            return f"<p>La entrada con nombreEntrada {datos['nombreEntrada']} se ha creado correctamente</p>"
        else:
            return f"<p>La entrada con nombreEntrada {datos['nombreEntrada']} ya existe</p>"
