import os
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr

load_dotenv()

# Configuración del correo
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_USERNAME"),
    MAIL_PORT=587,
)

app = FastAPI()

class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    body: str

@app.post("/send-email/")
async def send_email(email: EmailSchema, background_tasks: BackgroundTasks):
    message = MessageSchema(
        subject=email.subject,
        recipients=[email.email],  # Lista de destinatarios
        body=email.body,
        subtype="plain",  # "plain" o "html"
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    return {"message": "Correo enviado correctamente"}
