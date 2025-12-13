"""Camada de infraestrutura - Implementacoes concretas."""

from backend.shared.infrastructure.database.oracle_pool import OraclePool
from backend.shared.infrastructure.cache.memory_cache import MemoryCache
from backend.shared.infrastructure.logger import get_logger, create_logger
from backend.shared.infrastructure.http.aneel_response import AneelResponseBuilder
from backend.shared.infrastructure.config import Settings, get_settings

__all__ = [
    "OraclePool",
    "MemoryCache",
    "get_logger",
    "create_logger",
    "AneelResponseBuilder",
    "Settings",
    "get_settings",
]
