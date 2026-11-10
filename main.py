
import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from atendimento import (
    processar_atendimento,
    ClienteNaoEncontrado
)
from database import get_db
from schemas import ChatRequest, ChatResponse
from webhook import router as whatsapp_router

from telegram_bot import (
    criar_aplicacao_telegram,
    iniciar_telegram,
    encerrar_telegram
)


load_dotenv()

logger = logging.getLogger(__name__)


def telegram_habilitado() -> bool:
    return os.getenv(
        "TELEGRAM_ENABLED", "false"
    ).strip().lower() in ("true", "1", "yes", "on")


@asynccontextmanager
async def lifespan(app: FastAPI):
    telegram_app = None

    try:
        if telegram_habilitado():
            logger.info("Iniciando integração com Telegram...")

            telegram_app = criar_aplicacao_telegram()
            await iniciar_telegram(telegram_app)

            logger.info("Telegram iniciado com sucesso.")
        else:
            logger.info(
                "Telegram desativado por TELEGRAM_ENABLED."
            )

        logger.info(
            "AutoAtende AI iniciado. FastAPI e WhatsApp disponíveis."
        )

        yield

    finally:
        if telegram_app is not None:
            logger.info("Encerrando integração com Telegram...")
            await encerrar_telegram(telegram_app)
            logger.info("Telegram encerrado.")


app = FastAPI(
    title="AutoAtende AI",
    description="API para atendimento inteligente multicanal",
    version="0.4.1",
    lifespan=lifespan
)

app.include_router(whatsapp_router)


@app.get("/")
def home():
    return {
        "message": "Bem-vindo ao AutoAtende AI!",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "autoatende-ai"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        resultado = processar_atendimento(
            db=db,
            mensagem=request.mensagem,
            nome=request.nome,
            telefone=request.telefone,
            cliente_id=request.cliente_id
        )

        return ChatResponse(
            cliente_id=resultado.cliente_id,
            conversa_id=resultado.conversa_id,
            resposta=resultado.resposta,
            resposta_id=resultado.resposta_id
        )

    except ClienteNaoEncontrado as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro)
        )

    except Exception:
        logger.exception(
            "Erro inesperado no endpoint /chat"
        )

        raise HTTPException(
            status_code=502,
            detail="Falha ao processar o atendimento"
        )
