from flask import Blueprint, jsonify, request
import pymongo
from bson import ObjectId  

entrada_bp = Blueprint('entrada_bp', __name__)

#Cuando entramos a /entradas accederemos aqui

@entrada_bp.route("/")
def hello_world():
    return "<a href='http://127.0.0.1:5000/entradas/g'>CLICK AQUI PARA VER TODOS LAS ENTRADAS</a>"

# entradas/s?t=x&d=y con x = titulo e y = descripcion para subir entradas

@entrada_bp.route("/s", methods = ['GET'])
def upload_entry():
    t = request.args.get('t')
    d = request.args.get('d')
    
    entrada = db.entradas.find_one({"titulo": t})
    if entrada: 
        return "<p>La entrada con titulo " + t + " ya existe, si quieres actualizarla utiliza /u"
 
    db.entradas.insert_one({"titulo" : t, "descripcion" : d})

    return "<p>En esta pagina se cargaran los usuarios a la db " + t + " con descripcion " + d + " </p>"

# entradas/u?t=x&d=y con x = titulo e y = descripcion para actualizar entradas

@entrada_bp.route("/u", methods = ['GET'])
def update_entry():
    t = request.args.get('t')
    d = request.args.get('d')
    
    entrada = db.entradas.find_one({"titulo": t})
    if not entrada: #Si la entrada ya esta, es candidata a actualizar, en caso contrario avisaremos que hay que crearla
        return "<p>La entrada con titulo " + t + " no existe, si quieres crearla utiliza /s"

    db.entradas.update_one({"titulo" : t}, {"descripcion" : d})

    return "<p>La entrada con titulo " + t + " se ha actualizado correctamente"

# entradas/g para obtener todas las entradas
# entradas/g?t=x con x = titulo para obtener todas una entrada en especifica

@entrada_bp.route("/g")
def get_entry():
    
    t = request.args.get('t')

    if t: #Si existe una entrada con titulo => t buscamos parametrizadamente, si es null devolvemos todos y si no existe pues error
        entrada = db.entradas.find_one({"titulo": t})

        if entrada:
            resultado = {
                "titulo": entrada["titulo"],
                "descripcion": entrada["descripcion"]
            }
            return jsonify(resultado)
        
        else:
            return "<p>Entrada no encontrada</p>"
        
    else: #Si t no existe pues devolvemos todos
        entradas = db.entradas.find()
        resultado = [{"id": str(entrada["_id"]), "titulo": entrada["titulo"], "descripcion": entrada["descripcion"]} for entrada in entradas]
        return jsonify(resultado)
    
# Configuración de MongoDB
client = pymongo.MongoClient('mongodb+srv://admin:adminadmin@cluster0.gdoyn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.laWiki

