
import os
import asyncio
import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from atendimento import processar_atendimento
from database import SessionLocal


load_dotenv()

logger = logging.getLogger(__name__)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def atender_telegram(
    mensagem: str,
    nome: str,
    telegram_id: str
) -> str:
    db = SessionLocal()

    try:
        resultado = processar_atendimento(
            db=db,
            mensagem=mensagem,
            nome=nome,
            canal="telegram",
            identificador_externo=telegram_id
        )

        return resultado.resposta

    finally:
        db.close()


async def iniciar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if update.message:
        await update.message.reply_text(
            "Olá! Sou o AutoAtende AI, assistente virtual "
            "da nossa oficina. Como posso ajudar?"
        )


async def receber_mensagem(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message or not update.effective_user:
        return

    mensagem = update.message.text
    usuario = update.effective_user

    if not mensagem:
        return

    try:
        resposta = await asyncio.to_thread(
            atender_telegram,
            mensagem,
            usuario.full_name,
            str(usuario.id)
        )

        await update.message.reply_text(resposta)

    except Exception:
        logger.exception(
            "Erro ao processar mensagem do Telegram"
        )

        await update.message.reply_text(
            "Desculpe, não consegui processar sua "
            "mensagem agora. Tente novamente em instantes."
        )


def criar_aplicacao_telegram():
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN não configurado"
        )

    app = Application.builder().token(token).build()

    app.add_handler(
        CommandHandler("start", iniciar)
    )

    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE
            & filters.TEXT
            & ~filters.COMMAND,
            receber_mensagem
        )
    )

    return app


async def iniciar_telegram(app):
    await app.initialize()
    await app.start()

    try:
        if app.updater is None:
            raise RuntimeError(
                "Updater do Telegram não disponível"
            )

        await app.updater.start_polling(
            drop_pending_updates=False
        )

    except Exception:
        await app.stop()
        await app.shutdown()
        raise

    logger.info("AutoAtende AI conectado ao Telegram!")


async def encerrar_telegram(app):
    if app.updater and app.updater.running:
        await app.updater.stop()

    if app.running:
        await app.stop()

    await app.shutdown()

    logger.info("Telegram encerrado corretamente.")
