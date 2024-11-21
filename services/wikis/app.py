import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from service import wikis_bp

load_dotenv()

app = FastAPI()

# Registrar los microservicios como Blueprints
app.include_router(wikis_bp)

@app.get("/")
def main_route():
    return "<h1>laWiki</h1>"

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    puerto = os.getenv("SERVICE_WIKIS_PORT")
    if puerto:
        puerto = int(puerto)
        uvicorn.run("services.wikis.app:app", host="0.0.0.0", port=puerto, reload=True)
