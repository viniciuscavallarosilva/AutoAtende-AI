
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from webhook import router as whatsapp_router

from agent import responder_cliente
from database import get_db
from models import Cliente, Conversa, Mensagem
from schemas import ChatRequest, ChatResponse


app = FastAPI(
    title="AutoAtende AI",
    description="API para atendimento inteligente e agendamento",
    version="0.2.0"
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
def chat(request: ChatRequest, db: Session = Depends(get_db)):

    # 1. Identificar cliente
    if request.telefone:
        telefone = request.telefone.strip()

        cliente = db.query(Cliente).filter(
            Cliente.telefone == telefone
        ).first()

        if cliente is None:
            cliente = Cliente(
                nome=request.nome or "Cliente",
                telefone=telefone
            )
            db.add(cliente)
            db.flush()

    elif request.cliente_id is not None:
        cliente = db.get(Cliente, request.cliente_id)

        if cliente is None:
            raise HTTPException(
                status_code=404,
                detail="Cliente não encontrado"
            )
    else:
        raise HTTPException(
            status_code=422,
            detail="Informe o telefone do cliente"
        )

    # 2. Recuperar conversa aberta
    conversa = (
        db.query(Conversa)
        .filter(
            Conversa.cliente_id == cliente.id,
            Conversa.status == "aberta"
        )
        .order_by(Conversa.id.desc())
        .first()
    )

    if conversa is None:
        conversa = Conversa(
            cliente_id=cliente.id,
            status="aberta"
        )
        db.add(conversa)
        db.flush()

    # 3. Recuperar última resposta da OpenAI
    ultima_resposta = (
        db.query(Mensagem)
        .filter(
            Mensagem.conversa_id == conversa.id,
            Mensagem.papel == "assistant",
            Mensagem.resposta_id.isnot(None)
        )
        .order_by(Mensagem.id.desc())
        .first()
    )

    resposta_anterior_id = (
        ultima_resposta.resposta_id
        if ultima_resposta
        else None
    )

    # 4. Consultar o agente
    try:
        resposta, resposta_id = responder_cliente(
            mensagem=request.mensagem,
            resposta_anterior_id=resposta_anterior_id
        )

        # 5. Registrar mensagens
        db.add(Mensagem(
            conversa_id=conversa.id,
            papel="user",
            conteudo=request.mensagem
        ))

        db.add(Mensagem(
            conversa_id=conversa.id,
            papel="assistant",
            conteudo=resposta,
            resposta_id=resposta_id
        ))

        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=502,
            detail="Falha ao processar o atendimento"
        )

    # 6. Retornar resposta
    return ChatResponse(
        cliente_id=cliente.id,
        conversa_id=conversa.id,
        resposta=resposta,
        resposta_id=resposta_id
    )
