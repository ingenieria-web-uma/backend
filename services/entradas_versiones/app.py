import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from entradas import entradas_router
#from versiones import versiones_router

load_dotenv()

app = FastAPI()

# Registrar las rutas
app.include_router(entradas_router)
#app.include_router(versiones_router)

@app.get("/")
def main_route():
    return f"<a href='http://127.0.0.1:{os.getenv('SERVICE_ENTRADAS_PORT')}/entradas'>CLICK AQUI PARA IR AL APARTADO DE LAS ENTRADAS</a>"
    
if __name__ == "__main__":
        puerto = os.getenv("SERVICE_ENTRADAS_PORT")
        if puerto:
            puerto = int(puerto)
            uvicorn.run("services.entradas_versiones.app:app", host="0.0.0.0", port=puerto, reload=True)

# export PYTHONPATH=$(pwd); python services/entradas_versiones/app.py