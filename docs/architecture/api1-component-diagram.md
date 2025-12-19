# Diagrama de Componentes - API 1 (Quantitativo de Interrupções Ativas)

## Visão Geral da Arquitetura

Este documento descreve a arquitetura de componentes da API 1 do Projeto RADAR, responsável pelo fornecimento de dados quantitativos de interrupções ativas no sistema elétrico de Roraima.

## Diagrama de Alto Nível

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ANEEL (Cliente)                                 │
│                         Polling a cada 5 minutos                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTPS (x-api-key)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOAD BALANCER / NGINX                             │
│                          (SSL Termination, WAF)                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API RADAR                                       │
│                        FastAPI Application                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Interfaces Layer                                 │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐   │   │
│  │  │   Routes     │  │  Middleware  │  │   Schemas (Pydantic)   │   │   │
│  │  │  /health     │  │  - Auth      │  │  - Request             │   │   │
│  │  │  /quant...   │  │  - RateLimit │  │  - Response            │   │   │
│  │  └──────────────┘  │  - CORS      │  └────────────────────────┘   │   │
│  │                    │  - Logging   │                                │   │
│  │                    └──────────────┘                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Application Layer                                 │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │              GetInterrupcoesAtivasUseCase                     │  │   │
│  │  │  - Orquestra busca de dados                                   │  │   │
│  │  │  - Aplica regras de agregação                                 │  │   │
│  │  │  - Gerencia cache                                             │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       Domain Layer                                   │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐   │   │
│  │  │    Entities     │  │  Value Objects  │  │   Protocols      │   │   │
│  │  │  - Interrupcao  │  │  - CodigoIBGE   │  │  - Repository    │   │   │
│  │  │                 │  │  - TipoInterr.  │  │  - CacheService  │   │   │
│  │  └─────────────────┘  └─────────────────┘  └──────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   Infrastructure Layer                               │   │
│  │  ┌──────────────────────┐        ┌─────────────────────────────┐   │   │
│  │  │  OracleInterrupcao   │        │      RedisCacheService      │   │   │
│  │  │     Repository       │        │  - TTL: 5 minutos           │   │   │
│  │  │  - SQLAlchemy Async  │        │  - Key: api1:interrupcoes   │   │   │
│  │  │  - DBLink: SISTEC    │        └─────────────────────────────┘   │   │
│  │  └──────────────────────┘                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                                      │
                    ▼                                      ▼
┌────────────────────────────┐          ┌─────────────────────────────────────┐
│     Oracle Database        │          │              Redis                   │
│  ┌─────────────────────┐   │          │         (Cache Layer)               │
│  │    Oracle RADAR     │   │          │                                     │
│  │   (Banco Local)     │   │          │  ┌─────────────────────────────┐   │
│  │                     │   │          │  │  api1:interrupcoes:cache    │   │
│  └─────────────────────┘   │          │  │  TTL: 300s                  │   │
│           │                │          │  └─────────────────────────────┘   │
│           │ DBLink SISTEC  │          │                                     │
│           ▼                │          └─────────────────────────────────────┘
│  ┌─────────────────────┐   │
│  │   Oracle SISTEC     │   │
│  │  (Sistema Técnico)  │   │
│  │  - Interrupções     │   │
│  │  - UCs Afetadas     │   │
│  │  - Equipes          │   │
│  └─────────────────────┘   │
└────────────────────────────┘
```

## Diagrama de Sequência - Fluxo Principal

```
┌────────┐     ┌───────────┐     ┌──────────┐     ┌─────────┐     ┌───────┐     ┌────────┐
│ ANEEL  │     │   Route   │     │ UseCase  │     │  Cache  │     │ Repo  │     │ Oracle │
└───┬────┘     └─────┬─────┘     └────┬─────┘     └────┬────┘     └───┬───┘     └───┬────┘
    │                │                │                │              │              │
    │  GET /quant... │                │                │              │              │
    │───────────────>│                │                │              │              │
    │                │                │                │              │              │
    │                │  execute()     │                │              │              │
    │                │───────────────>│                │              │              │
    │                │                │                │              │              │
    │                │                │   get(key)     │              │              │
    │                │                │───────────────>│              │              │
    │                │                │                │              │              │
    │                │                │                │              │              │
    │                │                │  [Cache HIT]   │              │              │
    │                │                │<───────────────│              │              │
    │                │                │   dados        │              │              │
    │                │                │                │              │              │
    │                │                │  [Cache MISS]  │              │              │
    │                │                │   None         │              │              │
    │                │                │<───────────────│              │              │
    │                │                │                │              │              │
    │                │                │                │ buscar()     │              │
    │                │                │                │─────────────>│              │
    │                │                │                │              │              │
    │                │                │                │              │  SQL Query   │
    │                │                │                │              │─────────────>│
    │                │                │                │              │              │
    │                │                │                │              │   rows       │
    │                │                │                │              │<─────────────│
    │                │                │                │              │              │
    │                │                │                │  entities    │              │
    │                │                │                │<─────────────│              │
    │                │                │                │              │              │
    │                │                │   set(key,val) │              │              │
    │                │                │───────────────>│              │              │
    │                │                │                │              │              │
    │                │  Result[data]  │                │              │              │
    │                │<───────────────│                │              │              │
    │                │                │                │              │              │
    │  Response JSON │                │                │              │              │
    │<───────────────│                │                │              │              │
    │                │                │                │              │              │
```

## Componentes Detalhados

### 1. Interfaces Layer

#### Routes (`/quantitativointerrupcoesativas`)

| Componente | Arquivo | Responsabilidade |
|------------|---------|------------------|
| `interrupcoes_router` | `interfaces/http/routes/interrupcoes.py` | Endpoint principal da API |
| `health_router` | `interfaces/http/routes/health.py` | Health check e métricas |

#### Middleware Stack

```
Request
    │
    ▼
┌──────────────────────┐
│  RequestIdMiddleware │  ← Gera X-Request-ID
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│  LoggingMiddleware   │  ← Log estruturado (structlog)
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│  CORSMiddleware      │  ← Controle de origem
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│  RateLimitMiddleware │  ← 12 req/min por API key
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│  AuthMiddleware      │  ← Validação x-api-key
└──────────────────────┘
    │
    ▼
  Route Handler
```

#### Schemas (Pydantic)

| Schema | Arquivo | Descrição |
|--------|---------|-----------|
| `QuantitativoInterrupcoesResponse` | `schemas/interrupcoes.py` | Response principal |
| `InterrupcaoAtivaItem` | `schemas/interrupcoes.py` | Item de interrupção |
| `ErrorResponse` | `schemas/common.py` | Resposta de erro padrão |
| `HealthResponse` | `schemas/health.py` | Status do health check |

### 2. Application Layer

#### Use Cases

| Use Case | Arquivo | Responsabilidade |
|----------|---------|------------------|
| `GetInterrupcoesAtivasUseCase` | `application/use_cases/get_interrupcoes_ativas.py` | Busca e agrega interrupções |

```python
class GetInterrupcoesAtivasUseCase:
    """
    Fluxo:
    1. Verificar cache
    2. Se miss, buscar do repositório
    3. Agregar por município e tipo
    4. Atualizar cache
    5. Retornar Result[list[InterrupcaoAgregada]]
    """
```

### 3. Domain Layer

#### Entities

| Entity | Arquivo | Atributos |
|--------|---------|-----------|
| `Interrupcao` | `domain/entities/interrupcao.py` | id, municipio, tipo, ucs_afetadas, etc. |

#### Value Objects

| Value Object | Arquivo | Validações |
|--------------|---------|------------|
| `CodigoIBGE` | `domain/value_objects/codigo_ibge.py` | 7 dígitos, prefixo "14" (RR) |
| `TipoInterrupcao` | `domain/value_objects/tipo_interrupcao.py` | Enum: PROGRAMADA(1), NAO_PROGRAMADA(2) |
| `QuantidadeUCs` | `domain/value_objects/quantidade_ucs.py` | Inteiro não-negativo |

#### Protocols (Interfaces)

| Protocol | Arquivo | Métodos |
|----------|---------|---------|
| `InterrupcaoRepository` | `domain/protocols/interrupcao_repository.py` | `buscar_ativas() -> list[Interrupcao]` |
| `CacheService` | `domain/protocols/cache_service.py` | `get(key)`, `set(key, value, ttl)` |

### 4. Infrastructure Layer

#### Repository

| Implementação | Arquivo | Detalhes |
|---------------|---------|----------|
| `OracleInterrupcaoRepository` | `infrastructure/repositories/oracle_interrupcao.py` | SQLAlchemy async, DBLink SISTEC |

```sql
-- Query principal via DBLink
SELECT
    CODIGO_IBGE,
    TIPO_INTERRUPCAO,
    COUNT(*) as QTD_INTERRUPCOES,
    SUM(QTD_UCS_AFETADAS) as QTD_UCS,
    SUM(QTD_EQUIPES) as QTD_EQUIPES,
    MAX(DTH_ATUALIZACAO) as DTH_ULT_RECUPERACAO
FROM SISTEC.VW_INTERRUPCOES_ATIVAS@DBLINK_SISTEC
GROUP BY CODIGO_IBGE, TIPO_INTERRUPCAO
```

#### Cache Service

| Implementação | Arquivo | Configuração |
|---------------|---------|--------------|
| `RedisCacheService` | `infrastructure/cache/redis_cache.py` | TTL: 300s, Prefix: "api1:" |

## Diagrama de Dependências

```
┌─────────────────────────────────────────────────────────────────┐
│                        Interfaces                                │
│  ┌─────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │ Routes  │  │ Middleware  │  │         Schemas             │ │
│  └────┬────┘  └──────┬──────┘  └──────────────┬──────────────┘ │
│       │              │                         │                 │
└───────┼──────────────┼─────────────────────────┼─────────────────┘
        │              │                         │
        ▼              ▼                         │
┌─────────────────────────────────────────┐     │
│             Application                  │     │
│  ┌───────────────────────────────────┐  │     │
│  │   GetInterrupcoesAtivasUseCase    │  │     │
│  └─────────────────┬─────────────────┘  │     │
│                    │                     │     │
└────────────────────┼─────────────────────┘     │
                     │                           │
                     ▼                           │
┌─────────────────────────────────────────┐     │
│               Domain                     │     │
│  ┌─────────────┐  ┌─────────────────┐   │     │
│  │  Entities   │  │   Protocols     │   │◄────┘
│  │  ┌───────┐  │  │  ┌───────────┐  │   │
│  │  │Interr.│  │  │  │Repository │  │   │
│  │  └───────┘  │  │  │Cache      │  │   │
│  │             │  │  └───────────┘  │   │
│  └─────────────┘  └─────────────────┘   │
│  ┌─────────────────────────────────┐    │
│  │        Value Objects            │    │
│  │  CodigoIBGE │ TipoInterrupcao   │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
                     ▲
                     │ implements
┌────────────────────┼────────────────────┐
│           Infrastructure                 │
│  ┌─────────────────┴─────────────────┐  │
│  │                                    │  │
│  │  OracleRepository  │  RedisCache   │  │
│  │                                    │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Regras de Dependência (Clean Architecture)

| Camada | Pode Importar | Não Pode Importar |
|--------|---------------|-------------------|
| Domain | (nada externo) | Application, Infrastructure, Interfaces |
| Application | Domain | Infrastructure, Interfaces |
| Infrastructure | Domain, Application | Interfaces |
| Interfaces | Domain, Application, Infrastructure | - |

## Configurações de Ambiente

### Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `RADAR_DATABASE_URL` | Connection string Oracle | `oracle+oracledb_async://...` |
| `RADAR_REDIS_URL` | URL do Redis | `redis://localhost:6379/0` |
| `RADAR_API_KEY_HASH` | Hash da API key ANEEL | `sha256:...` |
| `RADAR_CACHE_TTL` | TTL do cache em segundos | `300` |
| `RADAR_RATE_LIMIT` | Requisições por minuto | `12` |
| `RADAR_LOG_LEVEL` | Nível de log | `INFO` |

### Portas e Protocolos

| Serviço | Porta | Protocolo |
|---------|-------|-----------|
| API RADAR | 8001 | HTTPS |
| Oracle RADAR | 1521 | Oracle Net |
| Redis Cache | 6379 | Redis Protocol |

## Considerações de Segurança

```
┌─────────────────────────────────────────────────────────────┐
│                    Camadas de Segurança                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Network Layer                                       │ │
│  │     - Firewall (porta 443 apenas)                       │ │
│  │     - WAF (SQL Injection, XSS protection)               │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐ │
│  │  2. Transport Layer                                     │ │
│  │     - TLS 1.3                                           │ │
│  │     - Certificate pinning (opcional)                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐ │
│  │  3. Application Layer                                   │ │
│  │     - API Key validation (x-api-key header)             │ │
│  │     - Rate limiting (12 req/min)                        │ │
│  │     - Input validation (Pydantic)                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐ │
│  │  4. Data Layer                                          │ │
│  │     - Parameterized queries (SQL Injection prevention)  │ │
│  │     - Encrypted connections (Oracle, Redis)             │ │
│  │     - Secrets em variáveis de ambiente                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Métricas e Observabilidade

```
┌─────────────────────────────────────────────────────────────┐
│                    Stack de Observabilidade                  │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Logs      │  │   Metrics   │  │      Traces         │  │
│  │ (structlog) │  │(Prometheus) │  │ (OpenTelemetry)     │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│         ▼                ▼                     ▼             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Grafana Dashboard                     ││
│  │  - Request rate        - Latency p50/p95/p99            ││
│  │  - Error rate          - Cache hit/miss ratio           ││
│  │  - DB query duration   - Active connections             ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Referências

- [Especificação API 1 - ANEEL](../api-specs/API_01_QUANTITATIVO_INTERRUPCOES_ATIVAS.md)
- [OpenAPI Specification](../api-specs/openapi-api1-interrupcoes.yaml)
- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
