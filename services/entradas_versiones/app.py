import os

from dotenv import load_dotenv
from flask import Flask
from entradas import entradas_bp
from versiones import versiones_bp

load_dotenv()

app = Flask(__name__)

# Registrar los microservicios como Blueprints
app.register_blueprint(entradas_bp, url_prefix="/entradas")
app.register_blueprint(versiones_bp, url_prefix="/versiones")

@app.route("/")
def main_route():
    return f"<a href='http://127.0.0.1:{os.getenv("SERVICE_ENTRADAS_PORT")}/entradas'>CLICK AQUI PARA IR AL APARTADO DE LAS ENTRADAS</a>"

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("SERVICE_ENTRADAS_PORT"))
