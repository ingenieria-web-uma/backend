import os

import cloudinary
import cloudinary.uploader
import pymongo
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from models.archivo import ArchivoNew

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

archivos_bp = APIRouter(prefix="/v2/archivos", tags=["archivos"])

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
archivos = db.archivos

# MicroServicio de ARCHIVOS

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

# Subir un archivo (POST)
@archivos_bp.post("/subir")
async def subir_archivo(archivo: UploadFile):
    try:
        # Subir el archivo a Cloudinary
        upload_result = cloudinary.uploader.upload(archivo.file, public_id=archivo.filename)

        # Guardar la URL en la base de datos
        nombre = archivo.filename
        url = upload_result["secure_url"]
        archivo_res = {"nombre": nombre, "url": url}
        
        # Insert into MongoDB
        archivos.insert_one(ArchivoNew(**archivo_res).model_dump())  # Assuming ArchivoNew is a Pydantic model
        
        return JSONResponse(content={"mensaje": f"Archivo subido exitosamente", "url":url}, status_code=201)
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error al subir el archivo, {e}")
