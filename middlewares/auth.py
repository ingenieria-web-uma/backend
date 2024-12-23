import os

import requests
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

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
                    raise HTTPException(status_code=401, detail="Error al validar el token de autorización")

        except HTTPException:
            return JSONResponse(status_code=401, content={"detail": "Error al validar el token de autorización"})
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": f"Error al validar el token de autorización, {e}"})
        response = await call_next(request)
        return response
