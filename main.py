
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from atendimento import (
    processar_atendimento,
    ClienteNaoEncontrado
)
from database import get_db
from schemas import ChatRequest, ChatResponse
from webhook import router as whatsapp_router


app = FastAPI(
    title="AutoAtende AI",
    description="API para atendimento inteligente multicanal",
    version="0.3.0"
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
        raise HTTPException(
            status_code=502,
            detail="Falha ao processar o atendimento"
        )
