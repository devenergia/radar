"""Pacote compartilhado entre todas as APIs do RADAR."""

from backend.shared.domain import *
from backend.shared.infrastructure import *

__all__ = [
    # Domain
    "Result",
    "CodigoIBGE",
    "TipoInterrupcao",
    "Interrupcao",
    # Infrastructure
    "OraclePool",
    "MemoryCache",
    "get_logger",
    "AneelResponseBuilder",
    # Config
    "Settings",
    "get_settings",
]
