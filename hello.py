from flask import Flask
import pymongo

app = Flask(__name__)

# Conexión a MongoDB
client = pymongo.MongoClient('mongodb+srv://admin:adminadmin@cluster0.gdoyn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.laWiki

@app.route("/")
def hello_world():
    # Insertar datos en MongoDB
    result = db.entradas.insert_many(
        [
            {"x": 1, "tags": ["dog", "cat"]}
        ]
    )
    
    # Mostrar los IDs de los documentos insertados
    return f"Documentos insertados: {result.inserted_ids}"

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(debug=True)