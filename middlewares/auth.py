import os

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from google.auth.transport import requests
from google.oauth2 import id_token
from starlette.middleware.base import BaseHTTPMiddleware

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            if request.method in ["POST","PUT","DELETE"]:
                if "Authorization" not in request.headers:
                    raise HTTPException(status_code=401, detail="No se proporcionó un token de autorización")
                token = request.headers["Authorization"].split(" ")[1]
                idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
                request.state.user = idinfo
        except HTTPException:
            return JSONResponse(status_code=401, content={"detail": "Error al validar el token de autorización"})
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": f"Error al validar el token de autorización, {e}"})
        response = await call_next(request)
        return response