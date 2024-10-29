from flask import Flask

from version_service import version_bp

app = Flask(__name__)

# Registrar los microservicios como Blueprints
app.register_blueprint(version_bp, url_prefix="/entradas")

@app.route("/")
def main_route():
    return "<a href='http://127.0.0.1:5000/entradas'>CLICK AQUI PARA IR AL APARTADO DE LAS ENTRADAS</a>"

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(debug=True)
