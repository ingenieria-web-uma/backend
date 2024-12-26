import os
from datetime import datetime

import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Response, status

from models.entrada import EntradaId
from models.version import (Version, VersionFilter, VersionId, VersionList,
                            VersionNew, VersionUpdate)

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

versiones_router = APIRouter(prefix="/v3/versiones", tags=["versiones"])

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv3
versiones = db.versiones


# GET /versiones
@versiones_router.get("/", response_model=VersionList)
def get_versions(filter: VersionFilter = Depends()):

    query = filter.to_mongo_dict(exclude_none=True)
    return VersionList(versiones=versiones.find(query).sort("fechaEdicion", -1))


# GET /versiones/<id>
@versiones_router.get("/{id}", response_model=Version)
def get_versions_byId(id: str):
    try:
        version = versiones.find_one({"_id": ObjectId(id)})
        if version:
            return version
        else:
            raise HTTPException(status_code=404, detail="Version no encontrada")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar la version: {str(e)}"
        )


# POST /versiones
@versiones_router.post("/", response_model=VersionId, status_code=201)
def create_version(version: VersionNew):
    try:
        version_dump = version.to_mongo_dict(exclude_none=True)
        version_id = versiones.insert_one(version_dump).inserted_id
        return VersionId(idVersion=str(version_id))
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al crear la versión: {str(e)}"
        )


# PUT /versiones/<id>
@versiones_router.put("/{id}")
def update_version(id, datos: VersionUpdate):
    try:
        idVersion = ObjectId(id)
        filter = {"_id": idVersion}
        version_existente = versiones.find_one(filter)
        if not version_existente:
            raise HTTPException(status_code=404, detail="Versión no encontada")

        res = versiones.update_one(
            filter, {"$set": datos.to_mongo_dict(exclude_none=True)}
        )

        if res.modified_count == 0:
            raise HTTPException(status_code=404, detail="Versión no modificada")

        return {"message": "Versión actualizada correctamente"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al actualizar la versión: {str(e)}"
        )


# DELETE /versiones/<id>
@versiones_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_version(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID {id} no tiene formato válido")

    result = versiones.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404, detail=f"Versión con ID {id} no encontrada"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# DELETE /versiones/
@versiones_router.delete("/")
def delete_versions_by_entradaId(idEntrada: EntradaId):
    try:
        res = versiones.delete_many(idEntrada.to_mongo_dict(exclude_none=True))
        return {
            "message": f"{res.deleted_count} versiones eliminadas de la entrada {idEntrada.idEntrada}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al eliminar las versiones de la entrada: {str(e)}",
        )
