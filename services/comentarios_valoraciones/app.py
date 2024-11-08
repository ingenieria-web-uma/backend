from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
import os
from dotenv import load_dotenv

from service import comentario_bp

load_dotenv()

app = Flask(__name__)

SWAGGER_URL = '/docs'
API_URL = '/static/swagger.yaml'

swaggerui_bp = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config = {
        'app_name': "laWiki",
        'layout': "BaseLayout"
    }
)

# Registrar los microservicios como Blueprints
app.register_blueprint(swaggerui_bp)
app.register_blueprint(comentario_bp, url_prefix="/comentarios")

@app.route("/")
def main_route():
    return "<a href='http://127.0.0.1:5002/comentarios'>CLICK AQUI PARA IR AL APARTADO DE LAS COMENTARIOS</a>"

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=os.getenv("SERVICE_COMENTARIOS_PORT"))
