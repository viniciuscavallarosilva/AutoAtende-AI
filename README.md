# AutoAtende AI

**AI-powered customer service and appointment scheduling prototype**

AutoAtende AI is a Python-based prototype designed to automate customer interactions for a fictional automotive repair shop.

The project demonstrates how an AI agent can interact with customers through messaging platforms, maintain conversational context, and execute business operations such as checking appointment availability and creating bookings.

## Features

- AI-powered customer service using the OpenAI API
- WhatsApp integration through Meta's WhatsApp Cloud API
- Telegram bot integration
- Appointment scheduling and availability checks
- Conversation history and customer data persistence
- Business rules for appointment scheduling
- REST API built with FastAPI
- PostgreSQL database integration
- Cloud deployment using Railway

## Technology Stack

- Python
- FastAPI
- OpenAI API
- PostgreSQL
- SQLAlchemy
- WhatsApp Cloud API
- python-telegram-bot
- Railway

## Architecture

```text
WhatsApp / Telegram / REST API
              |
              v
       FastAPI Backend
              |
              v
     Customer Service Logic
          /       \
         v         v
    OpenAI API   PostgreSQL
```

## Local Setup

1. Clone the repository.
2. Create a Python virtual environment.
3. Install the project dependencies.
4. Configure a PostgreSQL database.
5. Create a `.env` file with the required credentials.
6. Initialize the database schema.
7. Start the FastAPI application.

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Environment Variables

The project requires environment variables for its integrations.

```dotenv
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini

DATABASE_URL=

TELEGRAM_BOT_TOKEN=
TELEGRAM_ENABLED=false

WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_BUSINESS_ACCOUNT_ID=
WHATSAPP_VERIFY_TOKEN=
WHATSAPP_API_VERSION=v25.0

META_APP_SECRET=
```

Variable names and optional settings should be checked against the current source code before configuration.

### WhatsApp Configuration

To enable WhatsApp messaging, you need a Meta developer application, a configured WhatsApp Business Account, an API access token, and a publicly accessible webhook endpoint.

The webhook must be configured and subscribed to the appropriate message events in the Meta developer dashboard.

### Telegram Configuration

Create a bot through Telegram's BotFather, obtain its access token, and configure the corresponding environment variables.

## Current Status

This project is a functional prototype and is not yet intended as a production-ready commercial service.

Planned improvements include:

- Audio message transcription
- Webhook event deduplication and idempotency
- Improved appointment history management
- Appointment editing
- Holiday-aware scheduling
- Enhanced error handling and monitoring
- Cross-channel customer identity management

## Purpose

This project was created as a hands-on learning experience in AI agents, backend development, third-party API integrations, and cloud deployment.

It is also intended to demonstrate practical software engineering skills through an end-to-end implementation.
