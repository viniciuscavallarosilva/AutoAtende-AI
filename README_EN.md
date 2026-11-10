# AutoAtende AI

**AI-powered customer service and in-person vehicle assessment scheduling prototype**

**AutoAtende AI** is a prototype customer service agent for a fictional auto repair shop. It receives messages through **WhatsApp** and **Telegram**, uses the OpenAI API to conduct conversations, and combines business rules with a PostgreSQL database to check availability and manage appointments.

> **Status:** Functional prototype intended for technical demonstration and learning. It is not ready for unrestricted commercial use without additional testing, monitoring, and security improvements.

**Languages:** English | [Português](https://github.com/viniciuscavallarosilva/AutoAtende-AI/blob/master/README_PT.md)

## Features

- Conversational customer support through WhatsApp and Telegram.
- Customer identification and persistence of customer and conversation records.
- Conversational context maintained across messages within a conversation.
- Availability checks and scheduling of in-person vehicle assessments.
- Appointment rescheduling and lookup of the current booking, subject to the implemented business rules.
- Persistent storage of messages and appointments in PostgreSQL.
- HTTP endpoint for testing and integration with other systems.
- Cloud deployment on Railway.

## Tech stack

| Layer | Technologies |
| --- | --- |
| Backend | Python, FastAPI |
| AI agent | OpenAI API |
| Persistence | PostgreSQL, SQLAlchemy |
| WhatsApp | Meta WhatsApp Cloud API and webhooks |
| Telegram | Telegram Bot API, `python-telegram-bot` |
| Hosting | Railway |

## High-level architecture

```text
WhatsApp Cloud API ── webhook ──┐
                                │
Telegram Bot API ─── polling ───┼── FastAPI / shared service logic
                                │                │
REST API ───────────────────────┘                ├── OpenAI API
                                                 └── PostgreSQL
```

All channels use the same customer service logic and database. The HTTP service and Telegram polling can run within the same application process, depending on environment configuration.

## Main project files

| File | Responsibility |
| --- | --- |
| `main.py` | FastAPI initialization, HTTP endpoints, and application lifecycle |
| `webhook.py` | WhatsApp webhook event handling |
| `telegram_bot.py` | Telegram integration |
| `atendimento.py` | Shared customer service flow and persistence |
| `agent.py` | Model interaction and agent operations |
| `database.py` | Database connection and sessions |
| `models.py` | SQLAlchemy data models |
| `schemas.py` | API request and response schemas |

> These modules reflect the structure discussed during development. Check the repository for the current file names before following the instructions.

## Run locally

### Prerequisites

- A Python version compatible with the project's dependencies.
- An accessible PostgreSQL database, either local or remote.
- An OpenAI API key.
- Meta and/or Telegram credentials for the messaging channels you intend to enable.

### Installation

```bash
git clone <REPOSITORY_URL>
cd <REPOSITORY_DIRECTORY>
python -m venv .venv
```

On Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in the required configuration values. **Never commit a `.env` file containing real credentials.**

```bash
uvicorn main:app --reload
```

If the application starts on the default port, its interactive API documentation is available at `http://localhost:8000/docs`.

**Important:** Database table creation must follow the mechanism actually implemented in the project (for example, application initialization, a setup script, or migrations). Prepare the database schema before using the customer service endpoints.

## Integration configuration

### OpenAI and PostgreSQL

Configure a valid OpenAI API key and PostgreSQL connection URL. The model name and exact environment variable names must match those read by the source code.

### WhatsApp (Meta Cloud API)

1. Create or select an application in [Meta for Developers](https://developers.facebook.com/).
2. Configure the WhatsApp product and obtain the necessary credentials.
3. Expose the backend through a publicly accessible HTTPS endpoint.
4. Register the webhook URL and verification token in the Meta developer dashboard.
5. Subscribe the application to the relevant message events.
6. Check the permissions and restrictions associated with the WhatsApp Business Account and phone number.

Meta integration requires configuration outside the codebase and may differ between testing and production environments. Never expose access tokens, app secrets, or customer information.

### Telegram

1. Create a bot using [BotFather](https://t.me/BotFather).
2. Configure the bot token in the environment.
3. Enable polling only in the process intended to consume the bot's messages.
4. Avoid running multiple polling instances with the same token simultaneously, as this can cause conflicts.

## Deploy to Railway

The prototype uses one application service for the API and messaging integrations, plus a PostgreSQL database. The deployment start command is:

```bash
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
```

Configure the environment variables in Railway, connect the PostgreSQL database, and use the HTTPS domain provided by Railway as the WhatsApp webhook endpoint. In production, run only one Telegram polling instance per bot.

## Known limitations and planned improvements

- Handle incoming audio messages and eventually support transcription.
- Ensure idempotent processing of WhatsApp webhook events.
- Expand appointment history queries to include canceled bookings.
- Improve editing of appointment details.
- Block national, state, and municipal holidays in the scheduling calendar.
- Improve error handling, observability, and security.
- Improve customer identity matching across messaging channels.

## Security and responsible use

This repository must not include credentials, `.env` files, real customer data, or production database dumps. Before making it public, review the commit history and revoke any credentials that may have been exposed.

## Code usage

This repository is publicly available for technical demonstration, inspection, and study.

The source code remains protected by copyright. No license is currently granted for redistribution, modification, or use in other projects.

If you would like to reuse any part of the implementation, please contact the author to request permission.

## About the project

AutoAtende AI demonstrates an end-to-end integration of AI agents, messaging platforms, APIs, business rules, and persistent data storage. The goal is to showcase a functional implementation and document its technical evolution.
