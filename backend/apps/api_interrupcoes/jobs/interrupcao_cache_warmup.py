"""Job para pré-aquecimento de cache de interrupções."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.apps.api_interrupcoes.use_cases.get_interrupcoes_ativas import (
        GetInterrupcoesAtivasUseCase,
    )

logger = logging.getLogger(__name__)


class InterrupcaoCacheWarmupJob:
    """
    Job que pré-aquece o cache de interrupções ativas.

    Executa a cada 30 minutos para garantir que dados
    estejam sempre disponíveis em cache para consultas ANEEL.

    Implementa o Protocol Job do SchedulerService.
    """

    CACHE_KEY = "interrupcoes:ativas:v1"
    CRON_EXPRESSION = "*/30 * * * *"

    def __init__(
        self,
        use_case: GetInterrupcoesAtivasUseCase,
    ) -> None:
        """
        Inicializa o job de cache warmup.

        Args:
            use_case: Use case para buscar interrupções ativas
        """
        self._use_case = use_case

    @property
    def name(self) -> str:
        """Nome do job para identificação."""
        return "interrupcao_cache_warmup"

    async def execute(self) -> None:
        """
        Executa pré-aquecimento do cache.

        1. Busca dados frescos do Oracle (ignora cache)
        2. Atualiza cache com TTL renovado
        3. Registra métricas de execução

        Raises:
            RuntimeError: Se o use case falhar ao buscar dados
        """
        start_time = datetime.now()

        logger.info(
            "Iniciando warmup de cache de interrupções",
            extra={"cache_key": self.CACHE_KEY},
        )

        # Força busca do Oracle (ignora cache)
        result = await self._use_case.execute(force_refresh=True)

        if result.is_failure:
            logger.error(
                f"Falha no warmup de cache: {result.error}",
                extra={"cache_key": self.CACHE_KEY},
            )
            raise RuntimeError(f"Cache warmup failed: {result.error}")

        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        items_count = len(result.value) if result.value else 0

        logger.info(
            "Cache warmup concluído",
            extra={
                "duration_ms": duration_ms,
                "items_cached": items_count,
                "cache_key": self.CACHE_KEY,
            },
        )
