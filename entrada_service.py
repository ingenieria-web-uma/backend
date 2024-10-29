from flask import Blueprint, jsonify, request
import pymongo

entrada_bp = Blueprint('entrada_bp', __name__)

@entrada_bp.route("/")
def hello_world():
    return "<a href='http://127.0.0.1:5000/entradas/g'>CLICK AQUI PARA VER TODOS LAS ENTRADAS</a>"

@entrada_bp.route("/s", methods = ['GET'])
def upload_entry():
    t = request.args.get('t')
    d = request.args.get('d')
    
    entrada = db.entradas.find_one({"titulo": t})
    if entrada: 
        return "<p>La entrada con titulo " + t + " ya existe, si quieres actualizarla utiliza /u"
 
    db.entradas.insert_one({"titulo" : t, "descripcion" : d})

    return "<p>En esta pagina se cargaran los usuarios a la db " + t + " con descripcion " + d + " </p>"

@entrada_bp.route("/u", methods = ['GET'])
def update_entry():
    t = request.args.get('t')
    d = request.args.get('d')
    
    entrada = db.entradas.find_one({"titulo": t})
    if not entrada: #Si la entrada ya esta, es candidata a actualizar, en caso contrario avisaremos que hay que crearla
        return "<p>La entrada con titulo " + t + " no existe, si quieres crearla utiliza /s"

    db.entradas.update_one({"titulo" : t}, {"descripcion" : d})

    return "<p>La entrada con titulo " + t + " se ha actualizado correctamente"

@entrada_bp.route("/g")
def get_users():
    entradas = db.entradas.find()
    resultado = [{"id": str(entrada["_id"]), "titulo": entrada["titulo"], "descripcion": entrada["descripcion"]} for entrada in entradas]
    return jsonify(resultado)



# Configuración de MongoDB
client = pymongo.MongoClient('mongodb+srv://admin:adminadmin@cluster0.gdoyn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.laWiki

