import os

import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from notificaciones import notificaciones_bp

load_dotenv()

app = FastAPI()

# Registrar los microservicios como Blueprints
app.include_router(notificaciones_bp) 


# Ejecutar la aplicación FastAPI
if __name__ == "__main__":
    puerto = os.getenv("SERVICE_NOTIFICACIONES_PORT")
    if puerto:
        puerto = int(puerto)
        uvicorn.run("services.notificaciones.app:app", host="0.0.0.0", port=puerto, reload=True)
