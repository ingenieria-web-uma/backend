import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from services.wikis.service import wikis_bp

load_dotenv()

app = FastAPI()

# Registrar los microservicios como Blueprints
app.include_router(wikis_bp)

@app.get("/")
def main_route():
    return f"Servicio de wikis corriendo en el puerto {os.getenv('SERVICE_WIKIS_PORT')}"

# Ejecutar la aplicación FASTAPI
if __name__ == "__main__":
    puerto = os.getenv("SERVICE_WIKIS_PORT")
    if puerto:
        puerto = int(puerto)
        uvicorn.run("services.wikis.app:app", host="0.0.0.0", port=puerto, reload=True)
