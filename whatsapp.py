
import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def enviar_mensagem_whatsapp(
    telefone: str,
    mensagem: str
):
    token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    version = os.getenv(
        "WHATSAPP_API_VERSION",
        "v23.0"
    )

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
        "recipient_type": "individual",
        "to": telefone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": mensagem
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=15
    )

    if not response.ok:
        logger.error(
            "Erro na API do WhatsApp. HTTP %s: %s",
            response.status_code,
            response.text[:1000]
        )

    response.raise_for_status()

    return response.json()
