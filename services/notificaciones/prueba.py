import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración de la connexión
sender = 'lawikiuma@gmail.com'
password = 'WikiFAPI'
server = 'mail.swmanuales.com'
port = 465

# Configuración del destinatario
to = 'miguelangeldorado10@gmail.com'

# configuración de las cabeceras y del mensaje
message = MIMEMultipart("alternative")
message["Subject"] = "Bienvenido/a a SWPanel"
message["From"] = sender
message["To"] = to

body = """
Bienvenido/a a SWPanel

Accede a tu SWPanel: https://swpanel.com
"""

part = MIMEText(body, "plain")
message.attach(part)

# Envío del mensaje
try:
    smtp_server = smtplib.SMTP_SSL(server, port)
    smtp_server.ehlo()
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, to, message.as_string())
    smtp_server.close()
    print ("¡Se ha enviado correctamente!")
except Exception as ex:
    print ("Ha ocurrido un error...",ex)