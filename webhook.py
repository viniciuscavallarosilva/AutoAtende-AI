
import hashlib
import hmac
import json
import logging
import os

from collections import deque
from threading import Lock

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from starlette.concurrency import run_in_threadpool

from atendimento import processar_atendimento
from database import SessionLocal
from whatsapp import enviar_mensagem_whatsapp

load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

# Proteção inicial contra eventos repetidos.
# Para produção, substituiremos por controle persistente no banco.
ids_processados = set()
ordem_ids = deque()
lock_ids = Lock()
LIMITE_IDS = 1000


def registrar_mensagem(message_id):
    if not message_id:
        return True

    with lock_ids:
        if message_id in ids_processados:
            return False

        ids_processados.add(message_id)
        ordem_ids.append(message_id)

        if len(ordem_ids) > LIMITE_IDS:
            antigo = ordem_ids.popleft()
            ids_processados.discard(antigo)

    return True


def liberar_mensagem(message_id):
    if not message_id:
        return

    with lock_ids:
        ids_processados.discard(message_id)


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
        and token is not None
        and hmac.compare_digest(token, esperado)
        and challenge is not None
    ):
        return PlainTextResponse(challenge)

    raise HTTPException(
        status_code=403,
        detail="Verificação inválida"
    )


def processar_mensagem(telefone, nome, texto, message_id):
    db = SessionLocal()

    try:
        resultado = processar_atendimento(
            db=db,
            mensagem=texto,
            nome=nome,
            telefone=telefone
        )

        enviar_mensagem_whatsapp(
            telefone=telefone,
            mensagem=resultado.resposta
        )

        logger.info(
            "Mensagem WhatsApp processada: %s",
            message_id
        )

    except Exception:
        db.rollback()
        liberar_mensagem(message_id)

        logger.exception(
            "Falha ao processar mensagem WhatsApp: %s",
            message_id
        )

        raise

    finally:
        db.close()


@router.post("/webhook/whatsapp")
async def receber_webhook(request: Request):
    segredo = os.getenv("META_APP_SECRET")

    if not segredo:
        raise HTTPException(
            status_code=503,
            detail="META_APP_SECRET não configurado"
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

    try:
        evento = json.loads(corpo)
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(
            status_code=400,
            detail="JSON inválido"
        )

    if evento.get("object") != "whatsapp_business_account":
        return {"status": "ignored"}

    for entry in evento.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") != "messages":
                continue

            value = change.get("value", {})

            # Evita processar eventos de outros números.
            phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
            recebido_id = value.get(
                "metadata", {}
            ).get("phone_number_id")

            if phone_id and str(recebido_id) != str(phone_id):
                continue

            contatos = {
                contato.get("wa_id"): contato.get(
                    "profile", {}
                ).get("name", "Cliente")
                for contato in value.get("contacts", [])
            }

            for mensagem in value.get("messages", []):
                if mensagem.get("type") != "text":
                    continue

                telefone = mensagem.get("from")
                texto = mensagem.get(
                    "text", {}
                ).get("body", "").strip()
                message_id = mensagem.get("id")

                if not telefone or not texto:
                    continue

                if not registrar_mensagem(message_id):
                    continue

                nome = contatos.get(telefone) or "Cliente"

                try:
                    await run_in_threadpool(
                        processar_mensagem,
                        telefone,
                        nome,
                        texto,
                        message_id
                    )
                except Exception:
                    # A Meta poderá reenviar o evento.
                    raise HTTPException(
                        status_code=503,
                        detail="Falha temporária no atendimento"
                    )

    return {"status": "received"}
