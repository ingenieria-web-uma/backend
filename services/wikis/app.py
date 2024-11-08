import os

from dotenv import load_dotenv
from flask import Flask
from service import wikis_bp

load_dotenv()

app = Flask(__name__)

# Registrar los microservicios como Blueprints
app.register_blueprint(wikis_bp, url_prefix="/wikis")

@app.route("/")
def main_route():
    return "<h1>laWiki</h1>"

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("SERVICE_WIKIS_PORT"))
