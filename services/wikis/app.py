import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from wikis import wikis_bp

load_dotenv()

app = FastAPI()

# Registrar los microservicios como Blueprints
app.include_router(wikis_bp)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ejecutar la aplicación FASTAPI
if __name__ == "__main__":
    puerto = os.getenv("SERVICE_WIKIS_PORT")
    if puerto:
        puerto = int(puerto)
        uvicorn.run("app:app", host="0.0.0.0", port=puerto, reload=True)
