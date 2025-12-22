"""Configuracao global de testes pytest."""

from datetime import datetime

import pytest

from backend.shared.domain.entities.interrupcao import Interrupcao
from backend.shared.domain.value_objects.codigo_ibge import CodigoIBGE
from backend.shared.domain.value_objects.tipo_interrupcao import TipoInterrupcao


# =============================================================================
# Fixtures - Value Objects
# =============================================================================


@pytest.fixture
def codigo_ibge_boa_vista() -> CodigoIBGE:
    """CodigoIBGE de Boa Vista (capital)."""
    return CodigoIBGE.create(1400100).value


@pytest.fixture
def codigo_ibge_caracarai() -> CodigoIBGE:
    """CodigoIBGE de Caracarai."""
    return CodigoIBGE.create(1400209).value


# =============================================================================
# Fixtures - Entities
# =============================================================================


@pytest.fixture
def interrupcao_programada(codigo_ibge_boa_vista: CodigoIBGE) -> Interrupcao:
    """Interrupcao programada ativa em Boa Vista."""
    return Interrupcao.create(
        id=1,
        tipo=TipoInterrupcao.PROGRAMADA,
        municipio=codigo_ibge_boa_vista,
        conjunto=1,
        ucs_afetadas=100,
        data_inicio=datetime(2025, 12, 19, 10, 0, 0),
        data_fim=None,
    ).value


@pytest.fixture
def interrupcao_nao_programada(codigo_ibge_boa_vista: CodigoIBGE) -> Interrupcao:
    """Interrupcao nao programada ativa em Boa Vista."""
    return Interrupcao.create(
        id=2,
        tipo=TipoInterrupcao.NAO_PROGRAMADA,
        municipio=codigo_ibge_boa_vista,
        conjunto=1,
        ucs_afetadas=50,
        data_inicio=datetime(2025, 12, 19, 14, 30, 0),
        data_fim=None,
    ).value


@pytest.fixture
def interrupcao_finalizada(codigo_ibge_caracarai: CodigoIBGE) -> Interrupcao:
    """Interrupcao ja finalizada (nao ativa)."""
    return Interrupcao.create(
        id=3,
        tipo=TipoInterrupcao.NAO_PROGRAMADA,
        municipio=codigo_ibge_caracarai,
        conjunto=2,
        ucs_afetadas=30,
        data_inicio=datetime(2025, 12, 18, 8, 0, 0),
        data_fim=datetime(2025, 12, 18, 12, 0, 0),
    ).value


# =============================================================================
# Factories
# =============================================================================


def create_interrupcao(
    id: int = 1,
    tipo: TipoInterrupcao = TipoInterrupcao.PROGRAMADA,
    municipio: CodigoIBGE | None = None,
    conjunto: int = 1,
    ucs_afetadas: int = 100,
    data_inicio: datetime | None = None,
    data_fim: datetime | None = None,
) -> Interrupcao:
    """Factory para criar interrupcoes em testes."""
    if municipio is None:
        municipio = CodigoIBGE.create(1400100).value
    if data_inicio is None:
        data_inicio = datetime(2025, 12, 19, 10, 0, 0)

    return Interrupcao.create(
        id=id,
        tipo=tipo,
        municipio=municipio,
        conjunto=conjunto,
        ucs_afetadas=ucs_afetadas,
        data_inicio=data_inicio,
        data_fim=data_fim,
    ).value
