import os

from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

swaggerui_bp = get_swaggerui_blueprint(
    '/docs',
    '/static/swagger.yaml',
    config = {
        'app_name': "laWiki",
        'layout': "BaseLayout"
    }
)

app.register_blueprint(swaggerui_bp)

@app.route("/")
def main_route():
    return "<a href='http://127.0.0.1/docs'>CLICK AQUI PARA IR A LA ESPECIFICACIÓN</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=os.getenv("SERVICE_GATEWAY_PORT"))