import json
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
from models.user import User, UserList, UserNew, UserUpdate, UserRegister
from typing import Optional
from auth import get_password_hash
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

usuarios_router = APIRouter(prefix="/v2/usuarios", tags=["usuarios"])

# Configuración de MongoDB
client = MongoClient(MONGO_URL)
db = client.laWikiv2
usuarios = db.usuarios

#POST /usuarios/register
@usuarios_router.post("/register", response_model=User)
def register_user(user: UserRegister):
    hashed_password = get_password_hash(user.password)
    print(hashed_password)
    user_dict = user.model_dump()
    user_dict["password"] = hashed_password
    try:
        result = usuarios.insert_one(user_dict)
        new_user = usuarios.find_one({"_id": result.inserted_id})
        new_user["_id"] = str(new_user["_id"])
        print(new_user)
        return User(**new_user)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al registrar el usuario: {str(e)}"
        )


# GET /usuarios
@usuarios_router.get("/", response_model=UserList)
def get_users(
    name: Optional[str] = None, email: Optional[str] = None, role: Optional[str] = None
):
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if email:
        query["email"] = {"$regex": email, "$options": "i"}
    if role:
        query["role"] = {"$regex": role, "$options": "i"}

    try:
        users_data = usuarios.find(query).to_list(1000)
        return UserList(users=users_data)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar los usuarios: {str(e)}"
        )


# GET /usuarios/<id>
@usuarios_router.get("/{id}")
def get_user_by_id(id: str):
    try:
        user = usuarios.find_one({"_id": ObjectId(id)})
        if user:
            user["_id"] = str(user["_id"])
            return user
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar el usuario: {str(e)}"
        )


# POST /usuarios
@usuarios_router.post("/", response_model=User)
def create_user(user: UserNew):
    try:
        user_dump = user.model_dump()
        user_id = usuarios.insert_one(user_dump).inserted_id
        user = usuarios.find_one({"_id": ObjectId(user_id)})
        return user
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al crear el usuario: {str(e)}"
        )


# PUT /usuarios/<id>
@usuarios_router.put("/{id}", response_model=User)
def update_user(id: str, user: UserUpdate):
    try:
        user_dump = user.model_dump(
            exclude_unset=True
        )  # Exclude fields that were not set
        user_dump = {
            k: v for k, v in user_dump.items() if v is not None
        }  # Remove fields with None values
        if not user_dump:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        result = usuarios.update_one({"_id": ObjectId(id)}, {"$set": user_dump})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        user = usuarios.find_one({"_id": ObjectId(id)})
        if user:
            user["_id"] = str(user["_id"])  # Convert ObjectId to string
            return user
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al actualizar el usuario: {str(e)}"
        )


# DELETE /usuarios/<id>
@usuarios_router.delete("/{id}")
def delete_user(id: str):
    try:
        result = usuarios.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"message": "Usuario eliminado correctamente"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al eliminar el usuario: {str(e)}"
        )
