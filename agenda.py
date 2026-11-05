
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models import Agendamento, Cliente


FUSO = ZoneInfo("America/Sao_Paulo")
DURACAO = timedelta(minutes=30)
ANTECEDENCIA = timedelta(minutes=30)
JANELA_DIAS = 14

STATUS_ATIVOS = ("pendente", "confirmado")


def agora_local():
    return datetime.now(FUSO)


def gerar_horarios():
    """Retorna os 16 horários de início de avaliação."""
    horarios = []

    for inicio, fim in [
        (time(8, 30), time(12, 0)),
        (time(13, 30), time(18, 0)),
    ]:
        atual = datetime.combine(date.today(), inicio)
        limite = datetime.combine(date.today(), fim)

        while atual + DURACAO <= limite:
            horarios.append(atual.time())
            atual += DURACAO

    return horarios


def validar_data(data_agendamento):
    agora = agora_local()

    if data_agendamento.tzinfo is None:
        raise ValueError(
            "A data deve incluir um fuso horário"
        )

    data_agendamento = data_agendamento.astimezone(FUSO)

    if data_agendamento < agora + ANTECEDENCIA:
        raise ValueError(
            "O horário precisa ter 30 minutos de antecedência"
        )

    if data_agendamento.date() > (
        agora.date() + timedelta(days=JANELA_DIAS)
    ):
        raise ValueError(
            "Agendamentos permitidos até 14 dias à frente"
        )

    if data_agendamento.weekday() >= 5:
        raise ValueError(
            "A oficina não atende aos finais de semana"
        )

    if data_agendamento.time().replace(
        tzinfo=None
    ) not in gerar_horarios():
        raise ValueError(
            "Horário fora do expediente ou intervalo inválido"
        )

    return data_agendamento


def listar_disponibilidade(
    db: Session,
    dia: date
):
    agora = agora_local()

    if dia < agora.date():
        return []

    if dia > agora.date() + timedelta(days=JANELA_DIAS):
        return []

    if dia.weekday() >= 5:
        return []

    inicio_dia = datetime.combine(
        dia, time.min, tzinfo=FUSO
    )
    fim_dia = inicio_dia + timedelta(days=1)

    ocupados = db.scalars(
        select(Agendamento.data_hora).where(
            Agendamento.data_hora >= inicio_dia,
            Agendamento.data_hora < fim_dia,
            Agendamento.status.in_(STATUS_ATIVOS)
        )
    ).all()

    ocupados = {
        horario.astimezone(FUSO)
        for horario in ocupados
    }

    disponiveis = []

    for horario in gerar_horarios():
        inicio = datetime.combine(
            dia, horario, tzinfo=FUSO
        )

        if inicio < agora + ANTECEDENCIA:
            continue

        if inicio not in ocupados:
            disponiveis.append(
                inicio.strftime("%H:%M")
            )

    return disponiveis


def criar_agendamento(
    db: Session,
    cliente_id: int,
    data_agendamento: datetime,
    veiculo: str,
    descricao: str | None = None
):
    inicio = validar_data(data_agendamento)

    if not veiculo or not veiculo.strip():
        raise ValueError("Informe o veículo")

    if db.get(Cliente, cliente_id) is None:
        raise ValueError("Cliente não encontrado")

    horario = inicio.strftime("%H:%M")

    if horario not in listar_disponibilidade(
        db, inicio.date()
    ):
        raise ValueError(
            "Este horário não está mais disponível"
        )

    agendamento = Agendamento(
        cliente_id=cliente_id,
        veiculo=veiculo.strip(),
        descricao=descricao,
        data_hora=inicio,
        status="confirmado"
    )

    try:
        db.add(agendamento)
        db.commit()
        db.refresh(agendamento)
        return agendamento

    except IntegrityError:
        db.rollback()
        raise ValueError(
            "HORARIO_INDISPONIVEL: "
            "Este horário acabou de ser reservado. "
            "Consulte novamente a disponibilidade "
            "e ofereça alternativas ao cliente."
        )

    except Exception:
        db.rollback()
        raise

def listar_agendamentos_cliente(db: Session, cliente_id: int):
    agora = agora_local()

    return db.scalars(
        select(Agendamento)
        .where(
            Agendamento.cliente_id == cliente_id,
            Agendamento.status.in_(STATUS_ATIVOS),
            Agendamento.data_hora >= agora
        )
        .order_by(Agendamento.data_hora)
    ).all()

def cancelar_agendamento(
        db: Session,
        cliente_id: int,
        agendamento_id: int
):
    agendamento = db.scalar(
        select(Agendamento)
        .where(
            Agendamento.id == agendamento_id,
            Agendamento.cliente_id == cliente_id,
            Agendamento.status.in_(STATUS_ATIVOS),
            Agendamento.data_hora >= agora_local()
        )
        .with_for_update()
    )

    if agendamento is None:
        raise ValueError(
            "Agendamento ativo e futuro não encontrado para este cliente"
        )

    agendamento.status = "cancelado"

    try:
        db.commit()
        db.refresh(agendamento)
        return agendamento
    except Exception:
        db.rollback()
        raise


