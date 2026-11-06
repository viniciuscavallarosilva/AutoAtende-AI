# AutoAtende AI

**AI-powered customer service and appointment scheduling assistant**

AutoAtende AI is a Python-based project that explores how AI agents can support customer service workflows, manage conversations, and interact with business systems.

The current prototype simulates an automotive repair shop, allowing customers to communicate with an AI assistant through Telegram and request vehicle inspection appointments.

The project was developed as a hands-on exercise in AI agents, backend development, database integration, and cloud deployment.

## Tech Stack

- **Python** for application development
- **FastAPI** for backend API development
- **OpenAI API** for natural language understanding and conversational responses
- **PostgreSQL** for persistent data storage
- **SQLAlchemy** for database operations
- **Telegram Bot API** for customer interaction
- **Railway** for cloud hosting and deployment
- **Git and GitHub** for version control

## Current Features

- AI-powered customer service through Telegram
- Context-aware conversations
- Customer and conversation management
- Vehicle inspection appointment scheduling
- Appointment availability checks
- Appointment listing and cancellation
- Persistent storage using PostgreSQL
- Cloud deployment independent of the local development environment

## Architecture

The application integrates a messaging channel with an AI-powered backend and a relational database.

```text
Customer
   |
Telegram Bot
   |
Python Application
   |
AI Agent (OpenAI API)
   |
Business Logic
   |
PostgreSQL
```

The application is hosted on Railway, allowing the bot and database to operate without requiring a local development machine.

## Project Status

**Functional prototype, under active development.**

The initial Telegram integration, cloud deployment, and database initialization have been completed.

The project is not yet intended for production use with real customer data.

## Next Steps

- Implement transactional appointment rescheduling
- Improve error handling and validation
- Expand automated testing
- Integrate WhatsApp Business Platform
- Introduce database migrations
- Improve deployment automation and monitoring
- Add documentation and demonstration materials

## Motivation

The goal of this project is to explore practical applications of AI agents beyond simple conversational interfaces.

By integrating an LLM with business rules, persistent data, and real communication channels, the project demonstrates how AI can become part of operational workflows.

The emphasis is on iterative development, building a working prototype, validating its behavior, and progressively improving reliability and architecture.

## Author

**Vinícius Cavallaro da Silva**

Software Development | Product Management | AI Applications
