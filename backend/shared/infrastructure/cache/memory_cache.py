"""Implementacao de cache em memoria."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class CacheItem(Generic[T]):
    """Item do cache com metadados."""

    value: T
    expires_at: float
    created_at: float


@dataclass
class CacheStats:
    """Estatisticas do cache."""

    item_count: int
    hits: int
    misses: int
    hit_rate: float


class MemoryCache:
    """
    Implementacao de cache em memoria.

    Caracteristicas:
    - TTL por item
    - Suporte a dados stale para fallback
    - Estatisticas de uso
    - Limpeza automatica de itens expirados
    """

    def __init__(
        self,
        default_ttl_seconds: int = 300,
        stale_ttl_seconds: int = 3600,
        max_items: int = 1000,
    ) -> None:
        self._cache: dict[str, CacheItem[Any]] = {}
        self._stale_cache: dict[str, CacheItem[Any]] = {}
        self._hits = 0
        self._misses = 0
        self._default_ttl = default_ttl_seconds
        self._stale_ttl = stale_ttl_seconds
        self._max_items = max_items
        self._cleanup_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Inicia a task de limpeza periodica."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self) -> None:
        """Para a task de limpeza."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def get(self, key: str) -> Any | None:
        """
        Obtem um valor do cache.

        Args:
            key: Chave do item

        Returns:
            Valor ou None se nao existir ou estiver expirado
        """
        item = self._cache.get(key)

        if item is None:
            self._misses += 1
            return None

        now = time.time()
        if now > item.expires_at:
            # Item expirado - mover para stale
            self._stale_cache[key] = CacheItem(
                value=item.value,
                expires_at=now + self._stale_ttl,
                created_at=item.created_at,
            )
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return item.value

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int | None = None,
    ) -> None:
        """
        Armazena um valor no cache.

        Args:
            key: Chave do item
            value: Valor a ser armazenado
            ttl_seconds: Tempo de vida em segundos (usa padrao se None)
        """
        # Verificar limite
        if len(self._cache) >= self._max_items:
            self._evict_oldest()

        ttl = ttl_seconds or self._default_ttl
        now = time.time()

        self._cache[key] = CacheItem(
            value=value,
            expires_at=now + ttl,
            created_at=now,
        )

        # Remover da stale cache
        self._stale_cache.pop(key, None)

    async def invalidate(self, key: str) -> None:
        """Remove um item do cache."""
        self._cache.pop(key, None)
        self._stale_cache.pop(key, None)

    async def invalidate_all(self) -> None:
        """Remove todos os itens do cache."""
        self._cache.clear()
        self._stale_cache.clear()

    async def get_stale(self, key: str) -> Any | None:
        """
        Obtem um valor do cache, mesmo que esteja expirado.

        Util para fallback quando o banco esta indisponivel.
        """
        # Primeiro tentar cache normal
        fresh = await self.get(key)
        if fresh is not None:
            return fresh

        # Tentar stale cache
        item = self._stale_cache.get(key)
        if item is None:
            return None

        now = time.time()
        if now > item.expires_at:
            del self._stale_cache[key]
            return None

        return item.value

    def get_stats(self) -> CacheStats:
        """Retorna estatisticas do cache."""
        total = self._hits + self._misses
        return CacheStats(
            item_count=len(self._cache),
            hits=self._hits,
            misses=self._misses,
            hit_rate=self._hits / total if total > 0 else 0.0,
        )

    def _evict_oldest(self) -> None:
        """Remove o item mais antigo."""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at,
        )

        item = self._cache.pop(oldest_key)
        self._stale_cache[oldest_key] = CacheItem(
            value=item.value,
            expires_at=time.time() + self._stale_ttl,
            created_at=item.created_at,
        )

    async def _cleanup_loop(self) -> None:
        """Loop de limpeza periodica."""
        while True:
            await asyncio.sleep(60)  # A cada minuto
            self._cleanup()

    def _cleanup(self) -> None:
        """Remove itens expirados."""
        now = time.time()

        # Limpar cache principal
        expired_keys = [
            key for key, item in self._cache.items() if now > item.expires_at
        ]
        for key in expired_keys:
            item = self._cache.pop(key)
            self._stale_cache[key] = CacheItem(
                value=item.value,
                expires_at=now + self._stale_ttl,
                created_at=item.created_at,
            )

        # Limpar stale cache
        expired_stale = [
            key for key, item in self._stale_cache.items() if now > item.expires_at
        ]
        for key in expired_stale:
            del self._stale_cache[key]


# Instancia singleton
memory_cache = MemoryCache()


async def get_cache() -> MemoryCache:
    """Dependency injection para FastAPI."""
    return memory_cache
