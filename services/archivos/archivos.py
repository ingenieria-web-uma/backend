import os

import pymongo
from dotenv import load_dotenv
from fastapi import (APIRouter, File, HTTPException, Response, UploadFile,
                     status)

from models.archivo import ArchivoNew

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

archivos_bp = APIRouter(
    prefix="/v2/archivos",
    tags=['archivos']
    )


# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
archivos = db.archivos

# MicroServicio de ARCHIVOS

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# Configuration       
cloudinary.config( 
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# Subir un archivo (POST)

@archivos_bp.post("/subir")
async def subir_archivo(file: UploadFile = File(...)):
    # Obtener el archivo
    try:
        archivo = await file.read()

        # Subir el archivo a Cloudinary
        upload_result = cloudinary.uploader.upload(archivo, resource_type="auto")
        # Guardar la URL en la base de datos
        nombre = file.filename
        url = upload_result.get("secure_url")
        archivo = {
            "nombre": nombre,
            "url": url
        }
        archivos.insert_one(ArchivoNew(**archivo))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al subir el archivo")
    return ({"mensaje": f"Archivo con nombre { nombre } subido exitosamente"}), 201
