
from dataclasses import dataclass

from sqlalchemy.orm import Session

from agent import responder_cliente
from models import Cliente, Conversa, Mensagem, IdentidadeCanal


@dataclass
class ResultadoAtendimento:
    cliente_id: int
    conversa_id: int
    resposta: str
    resposta_id: str | None


class ClienteNaoEncontrado(Exception):
    pass


def processar_atendimento(
    db: Session,
    mensagem: str,
    nome: str | None = None,
    telefone: str | None = None,
    cliente_id: int | None = None,
    canal: str = "api",
    identificador_externo: str | None = None
) -> ResultadoAtendimento:

    if not mensagem or not mensagem.strip():
        raise ValueError("A mensagem não pode estar vazia")

    try:
        cliente = None

        # Identificação por canal externo, como Telegram.
        if identificador_externo:
            identidade = (
                db.query(IdentidadeCanal)
                .filter(
                    IdentidadeCanal.canal == canal,
                    IdentidadeCanal.identificador
                    == identificador_externo
                )
                .first()
            )

            if identidade:
                cliente = db.get(
                    Cliente,
                    identidade.cliente_id
                )
                if cliente is None:
                    raise ClienteNaoEncontrado(
                        "Identidade vinculada a cliente inexistente"
                    )

        # Identificação pelo telefone, usada pela API.
        if cliente is None and telefone:
            telefone = telefone.strip()
            if not telefone:
                raise ValueError("Telefone inválido")

            cliente = (
                db.query(Cliente)
                .filter(Cliente.telefone == telefone)
                .first()
            )

        # Identificação por ID interno.
        if cliente is None and cliente_id is not None:
            cliente = db.get(Cliente, cliente_id)

            if cliente is None:
                raise ClienteNaoEncontrado(
                    "Cliente não encontrado"
                )

        # Criação de cliente.
        if cliente is None:
            if not telefone and not identificador_externo:
                raise ValueError(
                    "Informe telefone ou identidade do canal"
                )

            cliente = Cliente(
                nome=nome or "Cliente",
                telefone=telefone
            )
            db.add(cliente)
            db.flush()

        # Vincula o identificador externo ao cliente.
        if identificador_externo and identidade is None:
            db.add(
                IdentidadeCanal(
                    cliente_id=cliente.id,
                    canal=canal,
                    identificador=identificador_externo
                )
            )
            db.flush()

        # Recupera a conversa aberta mais recente.
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

        # Recupera o contexto da OpenAI.
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
            if ultima_resposta else None
        )

        resposta, resposta_id = responder_cliente(
            mensagem=mensagem,
            resposta_anterior_id=resposta_anterior_id,
            db=db,
            cliente_id=cliente.id
        )

        db.add(
            Mensagem(
                conversa_id=conversa.id,
                papel="user",
                conteudo=mensagem
            )
        )

        db.add(
            Mensagem(
                conversa_id=conversa.id,
                papel="assistant",
                conteudo=resposta,
                resposta_id=resposta_id
            )
        )

        db.commit()

        return ResultadoAtendimento(
            cliente_id=cliente.id,
            conversa_id=conversa.id,
            resposta=resposta,
            resposta_id=resposta_id
        )

    except Exception:
        db.rollback()
        raise
