import httpx
import json
import os

from fastapi import APIRouter, HTTPException, Response, status
import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from models.notificacion import Notification, NotificationList, NotificationNew, NotificationUpdate
from services.notificaciones.email_service import EmailService

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

notificaciones_bp = APIRouter(
    prefix="/notificaciones",
    tags=['notificaciones']
)

# Configuración de MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.laWikiv2
notificaciones = db.notificaciones

SERVICE_USUARIOS_PORT = os.getenv("SERVICE_USUARIOS_PORT")
ENDPOINT_USUARIOS = os.getenv("ENDPOINT_USUARIOS")


USER_SERVICE_URL = f"http://localhost:{SERVICE_USUARIOS_PORT}/{ENDPOINT_USUARIOS}"

# Crear nueva notificacion
# @notificaciones_bp.post("/")
# async def create_notification(notification: NotificationNew):
#     # Convertir la notificación a un diccionario para MongoDB
#     print(notification)

#     notificaciones.insert_one(notification.model_dump())
#     return ("Creado satisfactoriamente")

@notificaciones_bp.post("/")
async def create_notification(notification: NotificationNew):
    # Convertir la notificación a un diccionario para MongoDB
    print(notification)

    # Buscar al usuario en la colección de usuarios
    user = await get_user(notification.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar si el usuario quiere recibir correos
    if not user.get("wants_emails", True):
        raise HTTPException(status_code=400, detail="El usuario no quiere recibir correos")

    # Extraer el correo electrónico
    recipient_email = user["email"]

    # Enviar el correo
    body = "Este es el contenido de la notificación."
    try:
        await EmailService.send_email(
            subject="Att: El equipo de laWiki",
            recipient=recipient_email,
            body=body
        )
        notificaciones.insert_one(notification.model_dump())
        return {"message": "Correo enviado con éxito y notificación creada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando correo: {str(e)}")


# Mostrar todas las notificaciones
@notificaciones_bp.get("/", response_model=NotificationList)
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
@notificaciones_bp.get("/{notification_id}", response_model=Notification)
async def get_notification(notification_id: str):
    notification = notificaciones.find_one({"_id": ObjectId(notification_id)})
    if not notification:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    notification["_id"] = str(notification["_id"])  # Convertir ObjectId a string
    return Notification(**notification)

# Obtener todas las Notificaciones de un Usuario (GET)
@notificaciones_bp.get("/usuario/{user_id}", response_model=NotificationList)
async def get_notifications(user_id: str):
    # Validar si el user_id es un ObjectId válido
    print(user_id)
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    # Buscar todas las notificaciones en la base de datos para ese usuario
    notifications = list(notificaciones.find({"user_id": user_id}))
    if not notifications:
        raise HTTPException(status_code=404, detail="No se encontraron notificaciones para el usuario proporcionado")

    # Convertir `_id` (ObjectId) a `str` en los resultados
    for notification in notifications:
        notification["_id"] = str(notification["_id"])

    # Retornar la lista de notificaciones
    return NotificationList(notifications=[Notification(**notification) for notification in notifications])
    
# Actualizar Notificación (PUT)
@notificaciones_bp.put("/{notification_id}", response_model=Notification)
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
@notificaciones_bp.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: str):
    result = notificaciones.delete_one({"_id": ObjectId(notification_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

async def get_user(user_id: str):
    try:
        async with httpx.AsyncClient() as client:
            print(f"{USER_SERVICE_URL}/{user_id}")
            response = await client.get(f"{USER_SERVICE_URL}/{user_id}")
            response.raise_for_status()
            user = response.json()
            return user
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Usuario no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con el servicio de usuarios: {str(e)}")