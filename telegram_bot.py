
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN não configurado no .env")


async def iniciar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Olá! Sou o AutoAtende AI. Como posso ajudar?"
    )


async def receber_mensagem(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    mensagem = update.message.text

    print(f"Mensagem recebida: {mensagem}")

    await update.message.reply_text(
        f"Recebi sua mensagem: {mensagem}"
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", iniciar))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receber_mensagem
        )
    )

    print("AutoAtende AI conectado ao Telegram!")

    app.run_polling()


if __name__ == "__main__":
    main()
