
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def enviar_mensagem_whatsapp(telefone: str, mensagem: str):
    token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    version = os.getenv("WHATSAPP_API_VERSION", "v23.0")

    if not token or not phone_id:
        raise RuntimeError(
            "Credenciais do WhatsApp não configuradas"
        )

    url = (
        f"https://graph.facebook.com/{version}/"
        f"{phone_id}/messages"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": telefone,
        "type": "text",
        "text": {
            "body": mensagem
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=15
    )

    response.raise_for_status()
    return response.json()
