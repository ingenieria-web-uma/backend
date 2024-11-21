import json
import os

from fastapi import APIRouter, HTTPException, Response, status
import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from models.notificacion import Notification, NotificationList, NotificationNew, NotificationUpdate

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

notificaciones_router = APIRouter(
    prefix="/notificaciones",
    tags=['notificaciones']
)

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
notificaciones = db.notificaciones

# Crear nueva notificacion
@notificaciones_router.post("/", response_model=Notification)
async def create_notification(notification: NotificationNew):
    # Convertir la notificación a un diccionario para MongoDB
    result = NotificationList.insert_one(notification)
    return notification

# Mostrar todas las notificaciones
@notificaciones_router.get("/", response_model=NotificationList)
async def get_all_notifications():
    # Obtener todas las notificaciones de la colección sin filtros
    notifications = list(notificaciones.find())  # Obtiene todas las notificaciones
    
    # Si no hay notificaciones, lanzar un error 404
    if not notifications:
        raise HTTPException(status_code=404, detail="No se encontraron notificaciones")
    
    # Convertir ObjectId a string en cada notificación
    for notification in notifications:
        notification["_id"] = str(notification["_id"])  # Convertir ObjectId a string
    
    # Crear una lista de objetos Notification a partir de los resultados
    return NotificationList(notifications=[Notification(**notif) for notif in notifications])

# Obtener Notificación por ID (GET)
@notificaciones_router.get("/{notification_id}", response_model=Notification)
async def get_notification(notification_id: str):
    notification = notificaciones.find_one({"_id": ObjectId(notification_id)})
    if not notification:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    notification["_id"] = str(notification["_id"])  # Convertir ObjectId a string
    return Notification(**notification)

# Obtener todas las Notificaciones de un Usuario (GET)
@notificaciones_router.get("/user/{user_id}", response_model=NotificationList)
async def get_notifications_for_user(user_id: int):
    notifications = list(notificaciones.find({"user_id": user_id}))
    if not notifications:
        raise HTTPException(status_code=404, detail="No se encontraron notificaciones")
    
# Actualizar Notificación (PATCH)
@notificaciones_router.patch("/{notification_id}", response_model=Notification)
async def update_notification(notification_id: str, update_data: NotificationUpdate):
    result = notificaciones.update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": update_data.dict(exclude_unset=True)}  # Solo actualiza los campos proporcionados
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    updated_notification = notificaciones.find_one({"_id": ObjectId(notification_id)})
    updated_notification["_id"] = str(updated_notification["_id"])  # Convertir ObjectId a string
    return Notification(**updated_notification)

# Eliminar Notificación (DELETE)
@notificaciones_router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: str):
    result = notificaciones.delete_one({"_id": ObjectId(notification_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
