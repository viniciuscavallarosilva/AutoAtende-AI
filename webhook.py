
import hashlib
import hmac
import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query, Request

load_dotenv()

router = APIRouter()


@router.get("/webhook/whatsapp")
def verificar_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    esperado = os.getenv("WHATSAPP_VERIFY_TOKEN")

    if (
        esperado
        and mode == "subscribe"
        and token
        and hmac.compare_digest(token, esperado)
        and challenge is not None
    ):
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(challenge)

    raise HTTPException(
        status_code=403,
        detail="Verificação inválida"
    )


@router.post("/webhook/whatsapp")
async def receber_webhook(request: Request):
    segredo = os.getenv("META_APP_SECRET")

    if not segredo:
        raise HTTPException(
            status_code=503,
            detail="Segredo do aplicativo não configurado"
        )

    corpo = await request.body()
    assinatura = request.headers.get(
        "X-Hub-Signature-256", ""
    )

    assinatura_esperada = "sha256=" + hmac.new(
        segredo.encode("utf-8"),
        corpo,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(
        assinatura,
        assinatura_esperada
    ):
        raise HTTPException(
            status_code=403,
            detail="Assinatura inválida"
        )

    evento = await request.json()

    # Nesta etapa, apenas confirmamos o recebimento.
    # O processamento das mensagens será integrado
    # ao serviço de atendimento posteriormente.

    return {"status": "received"}
