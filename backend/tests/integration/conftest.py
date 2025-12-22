"""Configuracao de fixtures para testes de integracao."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.shared.infrastructure.database.oracle_pool import OraclePool


@pytest.fixture
def mock_oracle_pool() -> MagicMock:
    """
    Mock do OraclePool para testes de integracao.

    Use esta fixture quando nao tiver acesso ao banco Oracle real.
    """
    pool = MagicMock(spec=OraclePool)
    pool.execute = AsyncMock(return_value=[])
    pool.execute_one = AsyncMock(return_value=None)
    pool.health_check = AsyncMock(return_value={"healthy": True, "latency_ms": 1.0})
    pool.is_ready = MagicMock(return_value=True)
    return pool


@pytest.fixture
def sample_interrupcao_row() -> dict[str, Any]:
    """Linha de exemplo de interrupcao do banco."""
    return {
        "conjunto": 1,
        "municipio_ibge": 1400100,
        "qtd_ucs_atendidas": 0,
        "qtd_programada": 50,
        "qtd_nao_programada": 30,
    }
