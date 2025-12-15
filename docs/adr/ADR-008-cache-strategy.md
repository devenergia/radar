# ADR-008: Estratégia de Cache

## Status

Aceito

## Data

2025-12-12

## Contexto

A API RADAR será consultada pela ANEEL a cada 30 minutos. Os dados vêm de múltiplas tabelas Oracle via DBLinks, o que pode causar:

1. Latência elevada em queries complexas
2. Carga desnecessária nos sistemas fonte
3. Problemas se um DBLink estiver temporariamente indisponível

Requisitos:
- Tempo de resposta < 5 segundos (exigência ANEEL)
- Dados devem ser razoavelmente atuais (tolerância de alguns minutos)
- Disponibilidade alta mesmo com falhas parciais

## Decisão

Implementaremos **cache em memória** com TTL (Time To Live) configurável.

### Arquitetura de Cache

```
┌─────────────────────────────────────────────────────────────────┐
│                        FLUXO COM CACHE                           │
└─────────────────────────────────────────────────────────────────┘

    Request                  Cache                    Database
       │                       │                          │
       │  GET /interrupcoes    │                          │
       │───────────────────────>                          │
       │                       │                          │
       │               ┌───────┴───────┐                  │
       │               │ Cache Hit?    │                  │
       │               └───────┬───────┘                  │
       │                       │                          │
       │            ┌──────────┴──────────┐               │
       │            │                     │               │
       │         [HIT]                 [MISS]             │
       │            │                     │               │
       │            ▼                     │  Query        │
       │    Return cached                 │───────────────>
       │        data                      │               │
       │                                  │    Results    │
       │                                  │<───────────────
       │                                  │               │
       │                           Store in cache         │
       │                                  │               │
       │<─────────────────────────────────┘               │
       │     Response                                     │
```

### Implementação

```python
# app/infrastructure/cache/memory_cache.py

import time
from typing import TypeVar, Generic, Optional, Dict
from dataclasses import dataclass
from threading import Lock

T = TypeVar('T')

@dataclass
class CacheConfig:
    """Configuração de cache"""
    ttl_seconds: int
    max_items: int


@dataclass
class CacheItem(Generic[T]):
    """Item de cache com expiração"""
    data: T
    expires_at: float


class MemoryCache(Generic[T]):
    """Cache em memória com TTL"""

    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: Dict[str, CacheItem[T]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[T]:
        """Retorna item do cache se existir e não estiver expirado"""
        with self._lock:
            item = self._cache.get(key)

            if item is None:
                return None

            # Verificar se expirou
            if time.time() > item.expires_at:
                del self._cache[key]
                return None

            return item.data

    def set(self, key: str, data: T) -> None:
        """Armazena item no cache"""
        with self._lock:
            # Limpar itens expirados se atingir limite
            if len(self._cache) >= self.config.max_items:
                self._cleanup()

            # Adicionar novo item
            self._cache[key] = CacheItem(
                data=data,
                expires_at=time.time() + self.config.ttl_seconds
            )

    def invalidate(self, key: str) -> None:
        """Remove item específico do cache"""
        with self._lock:
            self._cache.pop(key, None)

    def invalidate_all(self) -> None:
        """Limpa todo o cache"""
        with self._lock:
            self._cache.clear()

    def _cleanup(self) -> None:
        """Remove itens expirados do cache"""
        now = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if now > item.expires_at
        ]
        for key in expired_keys:
            del self._cache[key]

    def size(self) -> int:
        """Retorna quantidade de itens no cache"""
        return len(self._cache)

    def stats(self) -> Dict[str, int]:
        """Retorna estatísticas do cache"""
        with self._lock:
            now = time.time()
            active = sum(
                1 for item in self._cache.values()
                if now <= item.expires_at
            )
            expired = len(self._cache) - active

            return {
                "total_items": len(self._cache),
                "active_items": active,
                "expired_items": expired,
                "max_items": self.config.max_items
            }
```

### Estratégia de Cache por Endpoint

| Endpoint | TTL | Justificativa |
|----------|-----|---------------|
| `/quantitativointerrupcoesativas` | 5 min | Dados mudam com frequência |
| `/quantitativodemandas` | 10 min | Menos volátil |
| `/dadosdemanda/{protocolo}` | 30 min | Dados de demanda específica |
| `/health` | Sem cache | Deve sempre verificar |

### Cache Key Strategy

```python
# app/infrastructure/cache/cache_key.py

from typing import Dict, Any

def generate_cache_key(endpoint: str, params: Dict[str, Any]) -> str:
    """
    Gera chave de cache baseada em endpoint + parâmetros

    Args:
        endpoint: Caminho do endpoint
        params: Parâmetros da requisição

    Returns:
        Chave de cache única
    """
    if not params:
        return f"{endpoint}:default"

    # Ordenar parâmetros para garantir consistência
    sorted_params = sorted(params.items())
    params_str = "&".join(f"{k}={v}" for k, v in sorted_params)

    return f"{endpoint}:{params_str}"


# Exemplos:
# /interrupcoes -> "interrupcoes:default"
# /interrupcoes?dthRecuperacao=10/12/2025 14:30
#   -> "interrupcoes:dthRecuperacao=10/12/2025 14:30"
```

### Decorator para Cache

```python
# app/infrastructure/cache/cache_decorator.py

from functools import wraps
from typing import Callable, TypeVar, Any
from app.infrastructure.cache.memory_cache import MemoryCache
from app.infrastructure.cache.cache_key import generate_cache_key
from app.core.logging import get_logger

logger = get_logger(__name__)
T = TypeVar('T')

def cached(
    cache: MemoryCache,
    key_prefix: str,
    ttl_seconds: Optional[int] = None
):
    """
    Decorator para cachear resultado de funções

    Args:
        cache: Instância do cache
        key_prefix: Prefixo da chave de cache
        ttl_seconds: TTL customizado (opcional)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave de cache
            cache_key = generate_cache_key(key_prefix, kwargs)

            # Tentar buscar do cache
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.debug("Cache hit", key=cache_key)
                return cached_data

            # Cache miss - executar função
            logger.debug("Cache miss", key=cache_key)
            result = await func(*args, **kwargs)

            # Armazenar no cache
            cache.set(cache_key, result)

            return result

        return wrapper
    return decorator


# Exemplo de uso
from app.infrastructure.cache import cache_instance

@cached(cache_instance, key_prefix="interrupcoes", ttl_seconds=300)
async def get_interrupcoes_ativas(params: dict):
    # Lógica de busca
    ...
```

### Stale-While-Revalidate (Opcional)

```python
# app/infrastructure/cache/stale_while_revalidate.py

from typing import TypeVar, Callable, Optional
import asyncio
from app.infrastructure.cache.memory_cache import MemoryCache
from app.core.logging import get_logger

logger = get_logger(__name__)
T = TypeVar('T')

async def get_with_stale_revalidate(
    key: str,
    fetcher: Callable[[], T],
    cache: MemoryCache[T],
    stale_while_revalidate_seconds: int
) -> T:
    """
    Para alta disponibilidade, servir dados stale enquanto revalida

    Args:
        key: Chave de cache
        fetcher: Função para buscar dados frescos
        cache: Instância de cache
        stale_while_revalidate_seconds: Tempo que dados stale são aceitáveis

    Returns:
        Dados (frescos ou stale)
    """
    # Tentar cache normal
    cached = cache.get(key)
    if cached is not None:
        return cached

    # Cache miss - tentar buscar dados frescos
    try:
        fresh = await fetcher()
        cache.set(key, fresh)
        return fresh
    except Exception as e:
        logger.warning(
            "Erro ao buscar dados frescos",
            error=str(e),
            key=key
        )

        # Se falhar, tentar usar dados stale (se houver)
        stale = cache._get_stale(key, stale_while_revalidate_seconds)
        if stale is not None:
            logger.warning(
                "Usando dados stale",
                key=key,
                age_seconds=stale_while_revalidate_seconds
            )
            return stale

        # Sem dados stale disponíveis, propagar erro
        raise
```

### Integração com FastAPI

```python
# app/infrastructure/cache/__init__.py

from app.infrastructure.cache.memory_cache import MemoryCache, CacheConfig
from app.core.config import settings

# Instância global de cache
cache_instance = MemoryCache(
    config=CacheConfig(
        ttl_seconds=settings.CACHE_TTL_SECONDS,
        max_items=settings.CACHE_MAX_ITEMS
    )
)

def get_cache() -> MemoryCache:
    """Dependency para injeção de cache"""
    return cache_instance


# Endpoint para limpar cache manualmente
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/cache/invalidate")
async def invalidate_cache(
    cache: MemoryCache = Depends(get_cache)
):
    """Endpoint para invalidar todo o cache"""
    cache.invalidate_all()
    return {"message": "Cache invalidado com sucesso"}


@router.get("/cache/stats")
async def cache_stats(
    cache: MemoryCache = Depends(get_cache)
):
    """Endpoint para obter estatísticas do cache"""
    return cache.stats()
```

## Consequências

### Positivas

- **Performance**: Respostas mais rápidas para requests repetidos
- **Resiliência**: Pode servir dados em cache se DB estiver lento
- **Economia**: Menos queries aos sistemas fonte
- **Simplicidade**: Cache em memória é simples de implementar
- **Thread-Safe**: Uso de locks para operações concorrentes

### Negativas

- **Dados Não Realtime**: Dados podem estar até TTL segundos desatualizados
- **Memória**: Consome RAM do servidor
- **Não Distribuído**: Cache não é compartilhado entre instâncias

### Mitigações

1. **TTL Curto**: 5 minutos é aceitável para a frequência de consulta (30 min)
2. **Invalidação Manual**: Endpoint para forçar limpeza do cache se necessário
3. **Monitoring**: Métricas de hit rate e tamanho do cache

## Alternativas Consideradas

### Alternativa 1: Redis

Cache distribuído externo.

**Rejeitado porque**: Adiciona dependência externa, para uma única instância não é necessário.

### Alternativa 2: Materialized View Oracle

Cache no próprio banco de dados.

**Rejeitado porque**: Adiciona complexidade no banco, refresh da MV pode ser lento.

### Alternativa 3: Sem Cache

Consultar banco em toda requisição.

**Rejeitado porque**: Pode não atender ao requisito de 5 segundos em momentos de carga.

## Configuração

```python
# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Cache
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 300  # 5 minutos
    CACHE_MAX_ITEMS: int = 100
    CACHE_STALE_WHILE_REVALIDATE_SECONDS: int = 600  # 10 minutos

    class Config:
        env_file = ".env"
```

```bash
# .env
CACHE_ENABLED=true
CACHE_TTL_SECONDS=300
CACHE_MAX_ITEMS=100
CACHE_STALE_WHILE_REVALIDATE_SECONDS=600
```

## Referências

- [Caching Strategies](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/caching-patterns.html)
- [Stale-While-Revalidate](https://web.dev/stale-while-revalidate/)
- [Python Threading](https://docs.python.org/3/library/threading.html)
