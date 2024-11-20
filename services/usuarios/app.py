import os

from dotenv import load_dotenv
from fastapi import FastAPI
from .usuarios import usuarios_router

load_dotenv()

app = FastAPI()

# Registrar los microservicios como Blueprints
app.include_router(usuarios_router)

@app.get("/")
def main_route():
    return f"<a href='http://localhost:{os.getenv('SERVICE_USUARIOS_PORT')}/usuarios'>CLICK AQUI PARA IR AL APARTADO DE LOS USUARIOS</a>"