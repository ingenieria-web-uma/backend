from flask import Flask, jsonify, request
import pymongo

app = Flask(__name__)

# Conexión a MongoDB
client = pymongo.MongoClient('mongodb+srv://admin:adminadmin@cluster0.gdoyn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.laWiki

@app.route("/")
def hello_world():
    return "<a href='http://127.0.0.1:5000/g'>CLICK AQUI PARA VER TODOS LAS ENTRADAS</a>"

@app.route("/s", methods = ['GET'])
def upload_entry():
    t = request.args.get('t')
    d = request.args.get('d')
    
    db.entradas.insert_one({"titulo" : t, "descripcion" : d})

    return "<p>En esta pagina se cargaran los usuarios a la db " + t + " con descripcion " + d + " </p>"

@app.route("/g")
def get_users():
    entradas = db.entradas.find()
    resultado = [{"id": str(entrada["_id"]), "titulo": entrada["titulo"], "descripcion": entrada["descripcion"]} for entrada in entradas]
    return jsonify(resultado)


# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(debug=True)