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

```typescript
// src/infrastructure/cache/memory-cache.ts

export interface CacheConfig {
  ttlSeconds: number;
  maxItems: number;
}

export interface CacheItem<T> {
  data: T;
  expiresAt: number;
}

export class MemoryCache<T> {
  private cache: Map<string, CacheItem<T>> = new Map();
  private readonly config: CacheConfig;

  constructor(config: CacheConfig) {
    this.config = config;
  }

  get(key: string): T | null {
    const item = this.cache.get(key);

    if (!item) {
      return null;
    }

    if (Date.now() > item.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  set(key: string, data: T): void {
    // Limpar itens expirados se atingir limite
    if (this.cache.size >= this.config.maxItems) {
      this.cleanup();
    }

    this.cache.set(key, {
      data,
      expiresAt: Date.now() + (this.config.ttlSeconds * 1000),
    });
  }

  invalidate(key: string): void {
    this.cache.delete(key);
  }

  invalidateAll(): void {
    this.cache.clear();
  }

  private cleanup(): void {
    const now = Date.now();
    for (const [key, item] of this.cache) {
      if (now > item.expiresAt) {
        this.cache.delete(key);
      }
    }
  }
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

```typescript
// Chave de cache baseada em endpoint + parâmetros
function generateCacheKey(endpoint: string, params: Record<string, string>): string {
  const sortedParams = Object.entries(params)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${k}=${v}`)
    .join('&');

  return `${endpoint}:${sortedParams || 'default'}`;
}

// Exemplos:
// /interrupcoes -> "interrupcoes:default"
// /interrupcoes?dthRecuperacao=10/12/2025 14:30 -> "interrupcoes:dthRecuperacao=10/12/2025 14:30"
```

### Stale-While-Revalidate (Opcional)

```typescript
// Para alta disponibilidade, servir dados stale enquanto revalida
async function getWithStaleRevalidate<T>(
  key: string,
  fetcher: () => Promise<T>,
  cache: MemoryCache<T>,
  staleWhileRevalidateSeconds: number
): Promise<T> {
  const cached = cache.get(key);

  if (cached) {
    return cached;
  }

  // Tentar buscar dados frescos
  try {
    const fresh = await fetcher();
    cache.set(key, fresh);
    return fresh;
  } catch (error) {
    // Se falhar, tentar usar dados stale (se houver)
    const stale = cache.getStale(key, staleWhileRevalidateSeconds);
    if (stale) {
      // Log warning sobre dados stale
      return stale;
    }
    throw error;
  }
}
```

## Consequências

### Positivas

- **Performance**: Respostas mais rápidas para requests repetidos
- **Resiliência**: Pode servir dados em cache se DB estiver lento
- **Economia**: Menos queries aos sistemas fonte
- **Simplicidade**: Cache em memória é simples de implementar

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
