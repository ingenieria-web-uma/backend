import os

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

services = {
    "wikis": f"http://{os.getenv('ENDPOINT_WIKIS')}:{os.getenv('SERVICE_WIKIS_PORT')}/v2/wikis",
    "entradas": f"http://{os.getenv('ENDPOINT_ENTRADAS')}:{os.getenv('SERVICE_ENTRADAS_PORT')}/v2/entradas",
    "versiones": f"http://{os.getenv('ENDPOINT_ENTRADAS')}:{os.getenv('SERVICE_ENTRADAS_PORT')}/v2/valoraciones",
    "comentarios": f"http://{os.getenv('ENDPOINT_COMENTARIOS')}:{os.getenv('SERVICE_COMENTARIOS_PORT')}/v2/comentarios",
    "valoraciones": f"http://{os.getenv('ENDPOINT_COMENTARIOS')}:{os.getenv('SERVICE_COMENTARIOS_PORT')}/v2/valoraciones",
    "usuarios": f"http://{os.getenv('ENDPOINT_USUARIOS')}:{os.getenv('SERVICE_USUARIOS_PORT')}/v2/usuarios",
    "archivos": f"http://{os.getenv('ENDPOINT_ARCHIVOS')}:{os.getenv('SERVICE_ARCHIVOS_PORT')}/v2/archivos",
    "notificaciones": f"http://{os.getenv('ENDPOINT_NOTIFICACIONES')}:{os.getenv('SERVICE_NOTIFICACIONES_PORT')}/v2/notificaciones",
    "mapas": f"http://{os.getenv('ENDPOINT_MAPAS')}:{os.getenv('SERVICE_MAPAS_PORT')}/v2/mapas",
}


async def forward_request(
    service_url: str, method: str, path: str, body=None, headers=None
):
    async with httpx.AsyncClient() as client:
        url = f"{service_url}{path}"
        response = await client.request(method, url, json=body, headers=headers)
        return response


@app.api_route(
    "/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
    include_in_schema=False,
)
async def gateway(service: str, path: str, request: Request):
    if service not in services:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    service_url = services[service]
    body = await request.json() if request.method in ["POST", "PUT"] else None
    headers = dict(request.headers)
    query_params = str(request.query_params)

    response = await forward_request(
        service_url, request.method, f"/{path}?{query_params}", body, headers
    )

    return JSONResponse(status_code=response.status_code, content=response.json())


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", reload=True)
