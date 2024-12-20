import os

from dotenv import load_dotenv
from flask import Flask
from comentarios import comentarios_bp
from valoraciones import valoraciones_bp

load_dotenv()

app = Flask(__name__)

# Registrar los microservicios como Blueprints
app.register_blueprint(comentarios_bp, url_prefix="/comentarios")
app.register_blueprint(valoraciones_bp, url_prefix="/v2/valoraciones")

@app.route("/")
def main_route():
    return f"<a href='http://127.0.0.1:{os.getenv("SERVICE_COMENTARIOS_PORT")}/comentarios'>CLICK AQUI PARA IR AL APARTADO DE LAS COMENTARIOS</a>"

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("SERVICE_COMENTARIOS_PORT"))
