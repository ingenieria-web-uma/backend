from flask import Flask
from dotenv import load_dotenv
import os

from service import version_bp

load_dotenv()

app = Flask(__name__)

# Registrar los microservicios como Blueprints
app.register_blueprint(version_bp, url_prefix="/entradas")

@app.route("/")
def main_route():
    return "<a href='http://127.0.0.1:5001/entradas'>CLICK AQUI PARA IR AL APARTADO DE LAS ENTRADAS</a>"

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=os.getenv("SERVICE_ENTRADAS_PORT"))