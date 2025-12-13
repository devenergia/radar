"""Casos de uso da API 1 - Interrupcoes."""

from backend.apps.api_interrupcoes.use_cases.get_interrupcoes_ativas import (
    GetInterrupcoesAtivasUseCase,
    get_interrupcoes_ativas_use_case,
)

__all__ = ["GetInterrupcoesAtivasUseCase", "get_interrupcoes_ativas_use_case"]
