import json
import os

import pymongo
import requests
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Response, status
from datetime import datetime

from models.version import Version, VersionList, VersionNew, VersionUpdate

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

versiones_router = APIRouter(
    prefix="/versiones",
    tags=['versiones']
)

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
versiones = db.versiones

# GET /versiones
@versiones_router.get("/", response_model=VersionList)
def get_versions(
    idUsuario: str = None,
    idEntrada: str = None,
    contenido: str = None,
    fechaEdicion: datetime = None
):
    query = {}
    
    if idUsuario:
        if ObjectId.is_valid(idUsuario):
            query["idUsuario"] = ObjectId(idUsuario)
        else:
            raise HTTPException(status_code=400, detail=f"ID de usuario {idUsuario} no tiene formato valido")
    if idEntrada:
        if ObjectId.is_valid(idEntrada):
            query["idEntrada"] = ObjectId(idEntrada)
        else:
            raise HTTPException(status_code=400, detail=f"ID de entrada {idEntrada} no tiene formato valido")
    if contenido:
        query["contenido"] = {"$regex": contenido, "$options": "i"}
    if fechaEdicion:
        query["fechaEdicion"] = {"$regex": fechaEdicion, "$options": "i"}
    
    return VersionList(versiones=versiones.find(query))

# GET /versiones/<id>
@versiones_router.get("/{id}", response_model=Version)
def get_versions_byId(id: str):
    try:
        version = versiones.find_one({"_id": ObjectId(id)})
        if version:
            return version
        else:
            raise HTTPException(status_code=404, detail= "Version no encontrada")
    except Exception as e:
        raise HTTPException(status_code=400, detail= f"Error al buscar la version: {str(e)}")

# POST /versiones
@versiones_router.post("/", response_model=Version, status_code=status.HTTP_201_CREATED)
def create_version(version: VersionNew):
    model = version.model_dump(by_alias=True)
    try:
        model["idUsuario"] = ObjectId(version.idUsuario)
        model["idEntrada"] = ObjectId(version.idEntrada)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Fallo al convertir IDs: {str(e)}")
    model["fechaEdicion"] = version.fechaEdicion
    result = versiones.insert_one(model)
    return versiones.find_one({"_id": result.inserted_id})

# PUT /versiones/<id>
@versiones_router.put("/{id}", response_model=Version)
def update_version(id: str, version: VersionUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID {id} no tiene formato valido")
    
    model = version.model_dump(by_alias=True, exclude_none=True)
    if not model:
        raise HTTPException(status_code=400, detail="Debe incluir alguna actualizacion")
    
    try:
        if model["idUsuario"]:
            model["idUsuario"] = ObjectId(version.idUsuario)
        if model["idEntrada"]:
            model["idEntrada"] = ObjectId(version.idEntrada)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Fallo al convertir IDs: {str(e)}")
    model["fechaEdicion"] = version.fechaEdicion
    result = versiones.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": model},
        return_document=pymongo.ReturnDocument.AFTER,
    )
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail=f"Version con ID {id} no encontrada")

# DELETE /versiones/<id>
@versiones_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_version(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID {id} no tiene formato válido")
    
    result = versiones.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Versión con ID {id} no encontrada")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# DELETE /versiones/
@versiones_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_versions_by_entradaId(idEntrada: str):
    if not ObjectId.is_valid(idEntrada):
        raise HTTPException(status_code=400, detail=f"ID de entrada {idEntrada} no tiene formato válido")
    
    result = versiones.delete_many({"idEntrada": ObjectId(idEntrada)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"No se encontraron versiones con idEntrada {idEntrada}")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)