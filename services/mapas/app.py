import os

import uvicorn
from mapas import mapas_bp
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Registrar los microservicios como Blueprints
app.include_router(mapas_bp)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.route("/")
def main_route():
    return f"Servicio de mapas corriendo en el puerto {os.getenv('SERVICE_MAPAS_PORT')}"


# Ejecutar la aplicación FastAPI
if __name__ == "__main__":
    puerto = os.getenv("SERVICE_MAPAS_PORT")
    if puerto:
        puerto = int(puerto)
        uvicorn.run("services.mapas.app:app", host="0.0.0.0", port=puerto, reload=True)
