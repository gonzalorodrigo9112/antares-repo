
from flask_mail import Message
from flask import current_app
#from app import mail


from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

mail = Mail(app)





def send_reset_email(to_email, reset_url):
    msg = Message(
        subject="Recuperación de contraseña - Antares",
        sender=("Antares", current_app.config['MAIL_USERNAME']),
        recipients=[to_email]
    )
    msg.body = f"""Hola,

Has solicitado restablecer tu contraseña.

Haz clic en el siguiente enlace para crear una nueva contraseña:
{reset_url}

Este enlace expirará en 1 hora.

Si no lo solicitaste, simplemente ignora este correo.
"""
    mail.send(msg)