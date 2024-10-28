from flask import Flask, jsonify
import pymongo

app = Flask(__name__)

# Conexión a MongoDB
client = pymongo.MongoClient('mongodb+srv://admin:adminadmin@cluster0.gdoyn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.laWiki

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/upload_users")
def hello_blose():
    users = ["pedro", "blose", "migue", "pablo", "oscar", "inbal"]
    for i in users:
        db.entradas.insert_many(
            [
                {"user":i}
            ]
        )
    return "<p>En esta pagina se cargaran los usuarios a la db</p>"

@app.route("/get_users")
def get_users():
    entradas = db.entradas.find()
    resultado = [{"id": str(entrada["_id"]), "user": entrada["user"]} for entrada in entradas]
    return jsonify(resultado)


# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(debug=True)