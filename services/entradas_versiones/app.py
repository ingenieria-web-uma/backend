import os
from fastapi import FastAPI
from dotenv import load_dotenv
from flask import Flask
from entradas import entradas_router
#from versiones import versiones_router

load_dotenv()

app = FastAPI()

# Registrar los microservicios como Blueprints
app.include_router(entradas_router)
#app.include_router(versiones_router)

@app.get("/")
def main_route():
    return f"<a href='http://127.0.0.1:{os.getenv("SERVICE_ENTRADAS_PORT")}/entradas'>CLICK AQUI PARA IR AL APARTADO DE LAS ENTRADAS</a>"

# Ejecutar la aplicación Flask
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=os.getenv("SERVICE_ENTRADAS_PORT"))
    
#export PYTHONPATH=$(pwd); fastapi dev services/entradas_versiones/app.py