import os
from fastapi import FastAPI
from dotenv import load_dotenv
from flask import Flask
from notificaciones import notificaciones_router
#from versiones import versiones_router

load_dotenv()

app = FastAPI()

# Registrar los microservicios como Blueprints
app.include_router(notificaciones_router) 


@app.get("/")
def main_route():
    return f"<a href='http://127.0.0.1:{os.getenv("SERVICE_NOTIFICACIONES_PORT")}/notificaciones'>CLICK AQUI PARA IR AL APARTADO DE LAS NOTIFICACIONES</a>"
