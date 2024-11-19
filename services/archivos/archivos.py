import json
import os

import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
# from flask import Blueprint, jsonify, request
from fastapi import (APIRouter, File, HTTPException, Response, UploadFile,
                     status)

from models.archivo import ArchivoNew

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

# archivos_bp = Blueprint('archivos_bp', __name__)
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

async def subir_archivo(file: UploadFile):
    # Obtener el archivo
    archivo = file
    print(archivo.filename)

    # Subir el archivo a Cloudinary
    upload_result = cloudinary.uploader.upload(archivo)
    # Guardar la URL en la base de datos
    nombre = archivo.filename
    url = upload_result["secure_url"]
    archivo = {
        "nombre": nombre,
        "url": url
    }
    archivos.insert_one(ArchivoNew(**archivo))
    return ({"mensaje": f"Archivo con nombre { nombre } subido exitosamente"}), 201
