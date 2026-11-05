
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

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN não configurado no .env"
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def main():
    app = Application.builder().token(TOKEN).build()

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

    print("AutoAtende AI conectado ao Telegram!")

    app.run_polling()


if __name__ == "__main__":
    main()
