"""Jobs agendados para API de Interrupções."""

from backend.apps.api_interrupcoes.jobs.interrupcao_cache_warmup import (
    InterrupcaoCacheWarmupJob,
)

__all__ = [
    "InterrupcaoCacheWarmupJob",
]
