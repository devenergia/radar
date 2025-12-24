"""Configuracao de fixtures para testes E2E."""

from __future__ import annotations

import os
import sys
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Configurar variaveis de ambiente para testes ANTES de importar a app
# Settings usa prefixo PRD_RADAR_ para todas as variaveis
os.environ["PRD_RADAR_API_KEY"] = "test-api-key-12345"
os.environ["PRD_RADAR_ORACLE_USER"] = "test_user"
os.environ["PRD_RADAR_ORACLE_PASSWORD"] = "test_password"
os.environ["PRD_RADAR_ORACLE_DSN"] = "localhost:1521/XE"
os.environ["PRD_RADAR_EMAIL_INDISPONIBILIDADE"] = "test@test.com"
os.environ["PRD_RADAR_ENVIRONMENT"] = "development"


def _clear_module_cache() -> None:
    """Remove modulos da API do cache para garantir patches funcionem."""
    modules_to_clear = [
        key for key in sys.modules.keys()
        if key.startswith("backend.apps.api_interrupcoes")
    ]
    for mod in modules_to_clear:
        del sys.modules[mod]


@pytest.fixture
def api_key() -> str:
    """API Key valida para testes."""
    return "test-api-key-12345"


@pytest.fixture
def mock_oracle_pool() -> MagicMock:
    """Mock do OraclePool para evitar conexao real ao banco."""
    pool = MagicMock()
    pool.initialize = AsyncMock()
    pool.close = AsyncMock()
    pool.execute = AsyncMock(return_value=[])
    pool.health_check = AsyncMock(return_value={"healthy": True, "latency_ms": 1.0})
    pool.is_ready = MagicMock(return_value=True)
    return pool


@pytest.fixture
def mock_memory_cache() -> MagicMock:
    """Mock do MemoryCache."""
    cache = MagicMock()
    cache.start = AsyncMock()
    cache.stop = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.get_stale = AsyncMock(return_value=None)
    cache.get_stats = MagicMock(
        return_value=MagicMock(item_count=0, hit_rate=0.0)
    )
    return cache


@pytest.fixture
async def client(
    mock_oracle_pool: MagicMock,
    mock_memory_cache: MagicMock,
) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP para testes E2E."""
    # Limpar cache de modulos para garantir patches funcionem
    _clear_module_cache()

    # Limpar cache do lru_cache de get_settings
    from backend.shared.infrastructure.config import get_settings
    get_settings.cache_clear()

    # Patch nos modulos onde oracle_pool e memory_cache sao definidos
    with patch(
        "backend.shared.infrastructure.database.oracle_pool.oracle_pool",
        mock_oracle_pool,
    ), patch(
        "backend.shared.infrastructure.cache.memory_cache.memory_cache",
        mock_memory_cache,
    ):
        from backend.apps.api_interrupcoes.main import create_app

        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as ac:
            yield ac
