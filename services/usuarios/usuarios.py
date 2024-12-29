import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request
from pymongo import MongoClient

from middlewares.auth import role_required
from models.user import User, UserList, UserNew, UserUpdate

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

usuarios_router = APIRouter(prefix="/v3/usuarios", tags=["usuarios"])

# Configuración de MongoDB
client = MongoClient(MONGO_URL)
db = client.laWikiv3
usuarios = db.usuarios


# POST /usuarios/register
# @usuarios_router.post("/register", response_model=User)
# def register_user(user: UserRegister):
#     hashed_password = get_password_hash(user.password)
#     print(hashed_password)
#     user_dict = user.model_dump()
#     user_dict["password"] = hashed_password
#     try:
#         result = usuarios.insert_one(user_dict)
#         new_user = usuarios.find_one({"_id": result.inserted_id})
#         new_user["_id"] = str(new_user["_id"])
#         print(new_user)
#         return User(**new_user)
#     except Exception as e:
#         raise HTTPException(
#             status_code=400, detail=f"Error al registrar el usuario: {str(e)}"
#         )


# POST /usuarios/login
@usuarios_router.post("/login")
async def login_user(userData: UserNew, requset: Request):
    try:
        user = usuarios.find_one({"email": userData.email})
        if user:
            usuarios.update_one(
                {"email": userData.email},
                {"$set": {"access_token": userData.access_token, "googleId":userData.googleId, "expires_in":userData.expires_in, "name":userData.name, "wants_emails":userData.wants_emails, "profile_picture":userData.profile_picture}},
            )
        else:
            usuarios.insert_one(userData.to_mongo_dict(exclude_none=True))

        print(requset.state.user.get("role"))

        # return user
        user = usuarios.find_one({"email": userData.email})
        raise HTTPException(status_code=200, detail=User(**user).model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al iniciar sesión: {str(e)}"
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
        user = usuarios.find_one({"googleId": id})
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
# @usuarios_router.post("/", response_model=User)
# def create_user(user: UserNew):
#     try:
#         user_dump = user.model_dump()
#         user_id = usuarios.insert_one(user_dump).inserted_id
#         user = usuarios.find_one({"_id": ObjectId(user_id)})
#         return user
#     except Exception as e:
#         raise HTTPException(
#             status_code=400, detail=f"Error al crear el usuario: {str(e)}"
#         )


# PUT /usuarios/<id>
@usuarios_router.put("/{googleId}")
def update_user(googleId: str, user_update: UserUpdate, user=Depends(role_required(["admin"]))):
    print(user_update)
    user_dump = user_update.model_dump(
        exclude_unset=True,
        exclude_none=True
    )
    print(not user_dump)
    if not user_dump:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    try:
        result = usuarios.update_one({"googleId": googleId}, {"$set": user_dump})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    try:
        updated_user = usuarios.find_one({"googleId": googleId})
        if updated_user:
            updated_user["_id"] = str(updated_user["_id"])
            return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


# DELETE /usuarios/<id>
@usuarios_router.delete("/{googleId}")
def delete_user(googleId: str):
    try:
        result = usuarios.delete_one({"googleId": googleId})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"message": "Usuario eliminado correctamente"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al eliminar el usuario: {str(e)}"
        )
