from flask import Flask, request
import requests
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_NUMBER_ID = os.getenv("WHATSAPP_NUMBER_ID")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Función para enviar el archivo al correo
def send_email(file_url, file_name):
    msg = EmailMessage()
    msg["Subject"] = "Nuevo archivo de WhatsApp"
    msg["From"] = EMAIL_USER
    msg["To"] = RECIPIENT_EMAIL
    msg.set_content("Te enviaron un archivo desde WhatsApp.")

    # Descargar el archivo y adjuntarlo al correo
    response = requests.get(file_url)
    msg.add_attachment(response.content, maintype="application", subtype="octet-stream", filename=file_name)

    # Configurar el servidor de correo
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp.send_message(msg)

# Endpoint para recibir mensajes
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    # Comprobar si el mensaje contiene un archivo
    if "messages" in data["entry"][0]["changes"][0]["value"]:
        for message in data["entry"][0]["changes"][0]["value"]["messages"]:
            if "document" in message:
                file_id = message["document"]["id"]
                file_name = message["document"]["filename"]

                # Obtener la URL de descarga del archivo
                file_url = f"https://graph.facebook.com/v15.0/{file_id}"
                headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
                response = requests.get(file_url, headers=headers)

                if response.status_code == 200:
                    file_data = response.json()
                    send_email(file_data["url"], file_name)

    return "OK", 200

if __name__ == "__main__":
    app.run(port=3000)
