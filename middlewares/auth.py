import os

import requests
from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from starlette.middleware.base import BaseHTTPMiddleware

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
MONGO_URL = os.getenv("MONGO_URL")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
         if request.method in ["POST","PUT","DELETE"]:
                if "Authorization" not in request.headers:
                    raise HTTPException(status_code=401, detail="No se proporcionó un token de autorización")

                access_token = request.headers["Authorization"].split(" ")[1]
                url = "https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=" + access_token
                response = requests.get(url)

                if response.status_code != 200:
                    raise HTTPException(status_code=401, detail="Error al validar el token de autorización. La api de Google devolvió un error")

                # get sub from token
                token_info = response.json()
                googleId = token_info["sub"]

                # get user info
                client = MongoClient(MONGO_URL)
                db = client.laWikiv3
                usuarios = db.usuarios
                user = usuarios.find_one({"googleId": googleId})

                if not user:
                    userData = {
                            "access_token": access_token,
                            "googleId": googleId,
                            "role": "lector",
                            }
                else:
                    userData = {
                            "access_token": access_token,
                            "googleId": googleId,
                            "role": user["role"],
                            }

                request.state.user = userData

        except HTTPException as e:
            return JSONResponse(status_code=401, content={"detail": f"{e}"})
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": f"Error al validar el token de autorización, {e}"})
        response = await call_next(request)
        return response


def role_required(required_roles: list[str]):
    async def role_checker(request: Request):
        # Accedemos al usuario desde `request.state`
        user = request.state.user
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no autenticado")
        
        # Verificamos si el rol del usuario está en los roles requeridos para este endpoint
        if user["role"] not in required_roles:
            raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este recurso")
        
        return user  # Devuelve el usuario (opcional, para uso posterior en el endpoint)
    
    return role_checker
