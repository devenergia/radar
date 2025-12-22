"""Protocol CacheService para inversao de dependencia (RAD-106).

Define contrato que permite diferentes implementacoes de cache
(memoria, Redis, etc.) sem acoplar a camada de dominio.
"""

from typing import Protocol, TypeVar

T = TypeVar("T")


class CacheService(Protocol[T]):
    """
    Protocol para servico de cache.

    Define contrato que permite diferentes implementacoes
    (memoria, Redis, etc.) sem acoplar a camada de dominio.
    """

    async def get(self, key: str) -> T | None:
        """
        Recupera valor do cache.

        Args:
            key: Chave do cache

        Returns:
            Valor armazenado ou None se nao existir/expirado
        """
        ...

    async def set(self, key: str, value: T, ttl_seconds: int = 300) -> None:
        """
        Armazena valor no cache.

        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl_seconds: Tempo de vida em segundos (padrao: 300)
        """
        ...

    async def delete(self, key: str) -> None:
        """
        Remove valor do cache.

        Args:
            key: Chave a remover
        """
        ...

    async def exists(self, key: str) -> bool:
        """
        Verifica se chave existe no cache.

        Args:
            key: Chave a verificar

        Returns:
            True se existir e nao expirado
        """
        ...

    async def clear(self) -> None:
        """Remove todos os valores do cache."""
        ...


class CacheKeys:
    """Chaves padrao do cache."""

    INTERRUPCOES_ATIVAS = "interrupcoes:ativas"
    UNIVERSO_MUNICIPIOS = "universo:municipios"
    UNIVERSO_CONJUNTOS = "universo:conjuntos"


class CacheTTL:
    """TTLs padrao em segundos."""

    INTERRUPCOES = 300  # 5 minutos
    UNIVERSO = 3600  # 1 hora
    CURTA = 60  # 1 minuto
