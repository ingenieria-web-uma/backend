import os

import uvicorn
from comentarios import comentarios_bp
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from valoraciones import valoraciones_bp

load_dotenv()

app = FastAPI()
app.include_router(comentarios_bp)
app.include_router(valoraciones_bp)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ejecutar la aplicación FastAPI
if __name__ == "__main__":
    puerto = os.getenv("SERVICE_COMENTARIOS_PORT")
    if puerto:
        puerto = int(puerto)
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=puerto,
            reload=True,
        )
