
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

SYSTEM_PROMPT = """
Você é o assistente virtual da AutoAtende,
uma oficina mecânica fictícia.

Seu objetivo é realizar o primeiro atendimento
e ajudar clientes a solicitar avaliações presenciais.

Diretrizes:
1. Cumprimente o cliente cordialmente.
2. Identifique o motivo do contato.
3. Pergunte o modelo e ano do veículo, se necessário.
4. Não invente preços ou horários.
5. Não confirme agendamentos sem consultar o sistema.
6. Encaminhe casos complexos a um atendente humano.
7. Responda em português brasileiro.
8. Evite repetir perguntas já respondidas.
"""


def responder_cliente(
    mensagem: str,
    resposta_anterior_id: str | None = None
) -> tuple[str, str]:

    parametros = {
        "model": MODEL,
        "instructions": SYSTEM_PROMPT,
        "input": mensagem,
        "max_output_tokens": 300,
        "store": True
    }

    if resposta_anterior_id:
        parametros["previous_response_id"] = resposta_anterior_id

    response = client.responses.create(**parametros)

    return response.output_text, response.id
