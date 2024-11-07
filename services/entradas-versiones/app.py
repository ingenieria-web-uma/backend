from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

from version_service import version_bp

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
app.register_blueprint(version_bp, url_prefix="/entradas")

@app.route("/")
def main_route():
    return "<a href='http://127.0.0.1:5000/entradas'>CLICK AQUI PARA IR AL APARTADO DE LAS ENTRADAS</a>"

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
