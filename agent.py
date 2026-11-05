import json
import os
from datetime import date, timedelta
from zoneinfo import ZoneInfo
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.orm import Session

from agenda import (
    listar_disponibilidade,
    criar_agendamento,
    listar_agendamentos_cliente,
    cancelar_agendamento,
)

load_dotenv()
client = OpenAI()
MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')
FUSO = ZoneInfo('America/Sao_Paulo')

SYSTEM_PROMPT = '''
Você é o assistente virtual da AutoAtende, uma oficina mecânica fictícia.
Atenda cordialmente em português brasileiro, sem inventar preços, diagnósticos,
horários ou ações realizadas. Peça modelo e ano do veículo quando necessário.
Encaminhe casos complexos a atendimento humano, sem afirmar que fez um encaminhamento
real se não existir tal integração. Evite repetir perguntas já respondidas.

AGENDA
- Atendimento de segunda a sexta, 08h30-12h e 13h30-18h.
- Avaliações duram 30 minutos. Agendamentos até 14 dias à frente.
- Use SEMPRE as ferramentas para consultar disponibilidade. Nunca invente horários.
- Ao receber pedido genérico, consulte os próximos dias e ofereça dias/períodos.
- Em geral, apresente no máximo três horários por mensagem, ou pergunte o período
  preferido. Se o cliente solicitar todos os horários, mostre todos.
- Se um dia tiver muitos horários, não afirme que os poucos mostrados são os únicos.
- Antes de chamar criar_agendamento, obtenha veículo, data, horário e confirmação
  explícita do cliente para essa combinação. Uma escolha inicial de horário NÃO é
  confirmação final: recapitule e pergunte se pode confirmar.
- Só diga que agendou quando a ferramenta retornar sucesso.
- Se o horário ficar indisponível, explique e ofereça alternativas consultadas.
- Interprete hoje, amanhã e dias da semana com a data local informada no contexto.
- Não prometa verificação de feriados: o sistema ainda não os bloqueia.

CANCELAMENTO
- Quando o cliente solicitar cancelamento, consulte seus agendamentos ativos.
- Se houver mais de um, identifique qual ele deseja cancelar.
- Informe veículo, data e horário antes de solicitar confirmação.
- Só execute cancelar_agendamento após confirmação explícita.
- Só informe que o cancelamento foi realizado se a ferramenta retornar sucesso.
- Um agendamento cancelado libera o horário para novas reservas.
- Não afirme que consegue remarcar automaticamente: a ferramenta de remarcação ainda não existe.
- Nunca tente cancelar agendamentos pertencentes a outros clientes.
'''

TOOLS = [
    {
        'type': 'function', 'name': 'consultar_proximos_dias',
        'description': 'Consulta os próximos dias úteis com vagas reais. Use quando o cliente ainda não escolheu uma data.',
        'parameters': {
            'type': 'object', 'properties': {}, 'required': [],
            'additionalProperties': False,
        },
        'strict': True,
    },
    {
        'type': 'function', 'name': 'consultar_disponibilidade',
        'description': 'Lista os horários reais disponíveis numa data. Filtre manhã/tarde ao apresentar ao cliente.',
        'parameters': {
            'type': 'object',
            'properties': {'data': {'type': 'string', 'description': 'Data no formato AAAA-MM-DD'}},
            'required': ['data'], 'additionalProperties': False,
        },
        'strict': True,
    },
    {
        'type': 'function', 'name': 'criar_agendamento',
        'description': 'Confirma reserva somente depois de o cliente autorizar explicitamente a data, horário e veículo apresentados.',
        'parameters': {
            'type': 'object',
            'properties': {
                'data': {'type': 'string', 'description': 'Data AAAA-MM-DD'},
                'horario': {'type': 'string', 'description': 'Horário HH:MM, 24h'},
                'veiculo': {'type': 'string', 'description': 'Modelo e ano do veículo'},
                'descricao': {'type': ['string', 'null'], 'description': 'Motivo da avaliação ou null'},
            },
            'required': ['data', 'horario', 'veiculo', 'descricao'],
            'additionalProperties': False,
        },
        'strict': True,
    },

    {
        'type': 'function',
        'name': 'listar_agendamentos_cliente',
        'description': 'Consulta os agendamentos ativos e futuros do cliente atual.',
        'parameters': {
            'type': 'object',
            'properties': {},
            'required': [],
            'additionalProperties': False,
        },
        'strict': True,
    },
    {
        'type': 'function',
        'name': 'cancelar_agendamento',
        'description': (
            'Cancela um agendamento do cliente atual. '
            'Use somente após identificar o agendamento e '
            'receber confirmação explícita do cancelamento.'
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'agendamento_id': {
                    'type': 'integer',
                    'description': 'ID do agendamento a cancelar'
                }
            },
            'required': ['agendamento_id'],
            'additionalProperties': False,
        },
        'strict': True,
    },
]


def _executar_ferramenta(nome: str, argumentos: dict, db: Session, cliente_id: int) -> dict:
    hoje = datetime.now(FUSO).date()
    try:
        if nome == 'consultar_proximos_dias':
            dias = []
            for deslocamento in range(15):
                dia = hoje + timedelta(days=deslocamento)
                horarios = listar_disponibilidade(db, dia)
                if horarios:
                    dias.append({
                        'data': dia.isoformat(),
                        'dia_semana': dia.strftime('%A'),
                        'total_horarios': len(horarios),
                        'manha': sum(h < '12:00' for h in horarios),
                        'tarde': sum(h >= '13:30' for h in horarios),
                    })
                if len(dias) >= 5:
                    break
            return {'dias': dias}

        if nome == 'consultar_disponibilidade':
            dia = date.fromisoformat(argumentos['data'])
            return {'data': dia.isoformat(), 'horarios': listar_disponibilidade(db, dia)}

        if nome == 'criar_agendamento':
            data_hora = datetime.fromisoformat(
                f"{argumentos['data']}T{argumentos['horario']}"
            ).replace(tzinfo=FUSO)
            agendamento = criar_agendamento(
                db=db,
                cliente_id=cliente_id,
                data_agendamento=data_hora,
                veiculo=argumentos['veiculo'],
                descricao=argumentos.get('descricao'),
            )
            return {
                'sucesso': True, 'agendamento_id': agendamento.id,
                'data': argumentos['data'], 'horario': argumentos['horario'],
                'veiculo': agendamento.veiculo,
            }

        if nome == 'listar_agendamentos_cliente':
            agendamentos = listar_agendamentos_cliente(
                db, cliente_id
            )

            return {
                'agendamentos': [
                    {
                        'id': item.id,
                        'veiculo': item.veiculo,
                        'data_hora': item.data_hora.astimezone(
                            FUSO
                        ).isoformat(),
                        'status': item.status,
                    }
                    for item in agendamentos
                ]
            }

        if nome == 'cancelar_agendamento':
            agendamento = cancelar_agendamento(
                db=db,
                cliente_id=cliente_id,
                agendamento_id=argumentos['agendamento_id'],
            )

            return {
                'sucesso': True,
                'agendamento_id': agendamento.id,
                'status': agendamento.status,
                'veiculo': agendamento.veiculo,
            }

        if nome == 'listar_agendamentos_cliente':
            agendamentos = listar_agendamentos_cliente(
                db, cliente_id
            )

            return {
                'agendamentos': [
                    {
                        'id': item.id,
                        'veiculo': item.veiculo,
                        'data_hora': item.data_hora.astimezone(
                            FUSO
                        ).isoformat(),
                        'status': item.status,
                    }
                    for item in agendamentos
                ]
            }

        if nome == 'cancelar_agendamento':
            agendamento = cancelar_agendamento(
                db=db,
                cliente_id=cliente_id,
                agendamento_id=argumentos['agendamento_id'],
            )

            return {
                'sucesso': True,
                'agendamento_id': agendamento.id,
                'status': agendamento.status,
                'veiculo': agendamento.veiculo,
            }
    except (ValueError, TypeError, KeyError) as exc:
        db.rollback()
        return {'sucesso': False, 'erro': str(exc)}


def responder_cliente(
    mensagem: str,
    resposta_anterior_id: str | None = None,
    *,
    db: Session,
    cliente_id: int,
) -> tuple[str, str]:
    agora = datetime.now(FUSO)
    instrucoes = (
        SYSTEM_PROMPT
        + f'\nData e hora local atual: {agora.isoformat()} '
        + '(America/Sao_Paulo).\n'
    )
    parametros = {
        'model': MODEL,
        'instructions': instrucoes,
        'input': mensagem,
        'tools': TOOLS,
        'max_output_tokens': 650,
        'store': True,
    }
    if resposta_anterior_id:
        parametros['previous_response_id'] = resposta_anterior_id

    resposta = client.responses.create(**parametros)
    for _ in range(6):
        chamadas = [item for item in resposta.output if item.type == 'function_call']
        if not chamadas:
            if not resposta.output_text:
                raise RuntimeError('O agente não produziu uma resposta de texto.')
            return resposta.output_text, resposta.id

        saidas = []
        for chamada in chamadas:
            argumentos = json.loads(chamada.arguments)
            resultado = _executar_ferramenta(chamada.name, argumentos, db, cliente_id)
            saidas.append({
                'type': 'function_call_output',
                'call_id': chamada.call_id,
                'output': json.dumps(resultado, ensure_ascii=False),
            })

        resposta = client.responses.create(
            model=MODEL,
            instructions=instrucoes,
            previous_response_id=resposta.id,
            input=saidas,
            tools=TOOLS,
            max_output_tokens=650,
            store=True,
        )

    raise RuntimeError('O agente excedeu o limite de etapas de ferramentas.')
