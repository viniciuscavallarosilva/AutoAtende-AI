
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    cliente_id: int | None = None
    conversa_id: int | None = None
    nome: str | None = None
    telefone: str | None = None
    mensagem: str = Field(min_length=1)
    resposta_anterior_id: str | None = None


class ChatResponse(BaseModel):
    cliente_id: int
    conversa_id: int
    resposta: str
    resposta_id: str | None = None
