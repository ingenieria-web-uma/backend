import os

import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException

from models.valoracion import (Valoracion, ValoracionFiltro, ValoracionList,
                               ValoracionNew, ValoracionUpdate)

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

valoraciones_bp = APIRouter(
    prefix="/v2/valoraciones",
    tags=['valoraciones']
)

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
valoraciones = db.valoraciones

# GET /valoraciones
@valoraciones_bp.get("/")
def get_evaluations(filtro: ValoracionFiltro = Depends()):
    try:
        valoraciones_data = valoraciones.find(filtro.model_dump(exclude_none=True))
        return ValoracionList(valoraciones=[valoracion for valoracion in valoraciones_data]).model_dump(exclude_none=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al buscar las valoraciones: {str(e)}")

# GET /valoraciones/<id>
@valoraciones_bp.get("/{id}")
def get_evaluation_by_id(id):
    try:
        valoracion = valoraciones.find_one({"_id": ObjectId(id)})
        if valoracion:
            return Valoracion(**valoracion).model_dump()
        else:
            raise HTTPException(status_code=404, detail="Valoración no encontrada")
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al buscar la valoración: {str(e)}")
#
# POST /valoraciones
@valoraciones_bp.post("/")
def create_evaluation(newValoracion: ValoracionNew):
    try:
        valoracion_existente = valoraciones.find_one({
            "idUsuarioRedactor": newValoracion.idUsuarioRedactor,
            "idUsuarioValorado": newValoracion.idUsuarioValorado
        })

        if valoracion_existente:
            raise HTTPException(status_code=400, detail="Ya existe una valoración para este usuario")

        res = valoraciones.insert_one(newValoracion.to_mongo_dict(exclude_none=True))
        if res:
            raise HTTPException(status_code=201, detail="Valoración creada correctamente")
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al convertir los datos de la valoración: {str(e)}")
    return {"message": "Valoración creada correctamente"}, 201
#
# PUT /valoraciones/<id>
@valoraciones_bp.put("/{id}")
def update_evaluation(id, datos:ValoracionUpdate):
    try:
        idValoracion = ObjectId(id)
        filter = {"_id": idValoracion}
        valoracion_existente = valoraciones.find_one(filter)
        if not valoracion_existente:
            raise HTTPException(status_code=404, detail="Valoración no encontrada")

        res = valoraciones.update_one(filter, {"$set": datos.to_mongo_dict(exclude_none=True)})
        if res:
            raise HTTPException(status_code=200, detail="Valoración actualizada correctamente")
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al actualizar la valoración: {str(e)}")

# DELETE /valoraciones/<id>
@valoraciones_bp.delete("/{id}")
def delete_evaluation(id):
    try:
        filtro = {"_id": ObjectId(id)}
        valoracion = valoraciones.find_one(filtro)
        if valoracion:
            valoraciones.delete_one(filtro)
            raise HTTPException(status_code=200, detail=f"Valoración con ID {id} eliminada correctamente")
        else:
            raise HTTPException(status_code=404, detail="Valoración no encontrada")
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al eliminar la valoración: {str(e)}")
