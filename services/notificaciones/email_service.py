import os
from dotenv import load_dotenv
from fastapi import FastAPI
from models.email import EmailSchema
from mailjet_rest import Client

load_dotenv()

MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")
MAIL_FROM = os.getenv("MAIL_EMAIL")

if not all([MAILJET_API_KEY, MAILJET_API_SECRET, MAIL_FROM]):
    raise ValueError(
        "Por favor, define las variables de entorno MAILJET_API_KEY, MAILJET_API_SECRET y MAIL_EMAIL."
    )

app = FastAPI()


async def send_email(email: EmailSchema):
    mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version="v3")
    data = {
        "FromEmail": MAIL_FROM,
        "FromName": "LaWiki",
        "Recipients": [{"Email": email.email, "Name": ""}],
        "Subject": email.subject,
        "Text-part": email.body,
        "Html-part": "",
    }
    # Enviar correo directamente para obtener la respuesta
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())
    return "Correo enviado?"
