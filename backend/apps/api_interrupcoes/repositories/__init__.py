"""Repositorios da API 1 - Interrupcoes."""

from backend.apps.api_interrupcoes.repositories.interrupcao_repository import (
    InterrupcaoAgregadaDB,
    InterrupcaoRepository,
    get_interrupcao_repository,
    interrupcao_repository,
)
from backend.apps.api_interrupcoes.repositories.oracle_interrupcao_repository import (
    OracleInterrupcaoRepository,
)

__all__ = [
    "InterrupcaoAgregadaDB",
    "InterrupcaoRepository",
    "OracleInterrupcaoRepository",
    "get_interrupcao_repository",
    "interrupcao_repository",
]
