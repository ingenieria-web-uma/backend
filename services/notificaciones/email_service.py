import os
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from models.email import EmailSchema, EmailSchemaNew

load_dotenv()

# Configuración del correo
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_EMAIL"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_EMAIL"),
    MAIL_PORT=587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True  
)

app = FastAPI()

async def send_email(background_tasks: BackgroundTasks, email: EmailSchema):

    message = MessageSchema(
        subject=email.subject,
        recipients=[email.email],  # Lista de destinatarios
        body= email.body,
        subtype="plain"  # "plain" o "html"
    )

    fm = FastMail(conf)
    try:
        background_tasks.add_task(fm.send_message, message)
        return {"Correo enviado correctamente"}
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando correo: {str(e)}")
