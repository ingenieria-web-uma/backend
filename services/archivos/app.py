import os

from dotenv import load_dotenv
from flask import Flask
from archivos import archivos_bp

load_dotenv()

app = Flask(__name__)

# Registrar los microservicios como Blueprints
app.register_blueprint(archivos_bp, url_prefix="/v2/archivos")

@app.route("/")
def main_route():
    return f"Servicio de archivos corriendo en el puerto {os.getenv('SERVICE_ARCHIVOS_PORT')}"

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("SERVICE_ARCHIVOS_PORT"))
