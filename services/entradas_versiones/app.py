import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from entradas import entradas_router
from versiones import versiones_router

load_dotenv()

app = FastAPI()

# Registrar las rutas
app.include_router(entradas_router)
app.include_router(versiones_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    puerto = os.getenv("SERVICE_ENTRADAS_PORT")
    if puerto:
        puerto = int(puerto)
        uvicorn.run(
            "services.entradas_versiones.app:app",
            host="0.0.0.0",
            port=puerto,
            reload=True,
        )

# export PYTHONPATH=$(pwd); python services/entradas_versiones/app.py
