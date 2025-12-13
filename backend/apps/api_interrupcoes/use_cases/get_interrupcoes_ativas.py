"""Caso de uso: Obter Interrupcoes Ativas."""

from __future__ import annotations

from dataclasses import dataclass

from backend.shared.domain.result import Result
from backend.shared.infrastructure.cache.memory_cache import MemoryCache, memory_cache
from backend.shared.infrastructure.logger import get_logger

from backend.apps.api_interrupcoes.repositories.interrupcao_repository import (
    InterrupcaoRepository,
    interrupcao_repository,
)
from backend.apps.api_interrupcoes.schemas import InterrupcaoAgregadaItem


@dataclass
class InterrupcaoAgregada:
    """Dados agregados de interrupcao por municipio e conjunto."""

    conjunto: int
    municipio_ibge: int
    qtd_ucs_atendidas: int
    qtd_programada: int
    qtd_nao_programada: int

    def to_aneel_format(self) -> InterrupcaoAgregadaItem:
        """Converte para formato ANEEL."""
        return InterrupcaoAgregadaItem(
            ideConjuntoUnidadeConsumidora=self.conjunto,
            ideMunicipio=self.municipio_ibge,
            qtdUCsAtendidas=self.qtd_ucs_atendidas,
            qtdOcorrenciaProgramada=self.qtd_programada,
            qtdOcorrenciaNaoProgramada=self.qtd_nao_programada,
        )


class GetInterrupcoesAtivasUseCase:
    """
    Caso de uso para obter interrupcoes ativas agregadas.

    Busca interrupcoes ativas no banco de dados (via DBLink),
    agrega por municipio e conjunto, e retorna no formato ANEEL.

    Utiliza cache para melhorar performance.
    """

    CACHE_KEY = "interrupcoes:ativas"
    CACHE_TTL_SECONDS = 300  # 5 minutos

    def __init__(
        self,
        repository: InterrupcaoRepository,
        cache: MemoryCache,
    ) -> None:
        self.repository = repository
        self.cache = cache
        self.logger = get_logger("use_case.interrupcoes")

    async def execute(self) -> Result[list[InterrupcaoAgregadaItem]]:
        """
        Executa o caso de uso.

        Returns:
            Result com lista de interrupcoes agregadas ou erro
        """
        # Tentar obter do cache
        cached = await self.cache.get(self.CACHE_KEY)
        if cached is not None:
            self.logger.debug("Cache hit para interrupcoes ativas")
            return Result.ok(cached)

        self.logger.debug("Cache miss - buscando do banco")

        # Buscar do banco
        try:
            interrupcoes = await self.repository.find_ativas_agregadas()
        except Exception as e:
            self.logger.error(
                "Erro ao buscar interrupcoes",
                error=str(e),
                exc_info=True,
            )

            # Tentar stale cache como fallback
            stale = await self.cache.get_stale(self.CACHE_KEY)
            if stale is not None:
                self.logger.warning("Usando dados stale do cache")
                return Result.ok(stale)

            return Result.fail(f"Erro ao consultar banco de dados: {str(e)}")

        # Converter para formato ANEEL
        result = [item.to_aneel_format() for item in interrupcoes]

        # Armazenar no cache
        await self.cache.set(self.CACHE_KEY, result, self.CACHE_TTL_SECONDS)
        self.logger.debug(
            "Dados armazenados no cache",
            count=len(result),
            ttl=self.CACHE_TTL_SECONDS,
        )

        return Result.ok(result)


# Dependency injection
async def get_interrupcoes_ativas_use_case() -> GetInterrupcoesAtivasUseCase:
    """Factory para injecao de dependencia."""
    return GetInterrupcoesAtivasUseCase(
        repository=interrupcao_repository,
        cache=memory_cache,
    )
