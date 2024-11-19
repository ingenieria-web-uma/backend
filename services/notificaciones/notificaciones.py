import json
import os

from fastapi import APIRouter, HTTPException, Response, status
import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Blueprint, current_app, jsonify, request
from models.notificacion import Notificacion, ColeccionNotificaciones

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

entradas_router = APIRouter(
    prefix="/notificaciones",
    tags=['notificaciones']
)

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
notificaciones = db.notificaciones

# Rnotifaciones /POST
@notificaciones_router.post("/", response_model=Notificacion)
async def create_notification(notificacion: Notificacion):
    # Convertir la notificación a un diccionario para MongoDB
    notificacion_data = notificacion.dict()
    result = ColeccionNotificaciones.insert_one(notificacion_data)
    notificacion_data["_id"] = str(result.inserted_id)  # Convertir ObjectId a string
    return notificacion_data