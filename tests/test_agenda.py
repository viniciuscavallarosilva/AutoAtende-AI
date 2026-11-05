
import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from agenda import gerar_horarios, validar_data


def test_quantidade_de_horarios():
    horarios = gerar_horarios()

    assert len(horarios) == 16
    assert horarios[0].strftime("%H:%M") == "08:30"
    assert horarios[-1].strftime("%H:%M") == "17:30"


def test_nao_permite_fim_de_semana():
    sabado = datetime(
        2026, 11, 7, 10, 0,
        tzinfo=ZoneInfo("America/Sao_Paulo")
    )

    with pytest.raises(ValueError):
        validar_data(sabado)
