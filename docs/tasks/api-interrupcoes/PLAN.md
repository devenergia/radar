# Plano de Implementacao: API 1 - Quantitativo de Interrupcoes Ativas

**Data:** 2025-12-19
**Status:** Em Andamento
**Base Legal:** Oficio Circular n 14/2025-SFE/ANEEL
**Prazo:** Dezembro/2025

## Visao Geral

API para retornar o quantitativo de unidades consumidoras com interrupcao do fornecimento de energia eletrica ativas no momento da consulta, conforme especificacao da ANEEL.

### Endpoint Principal

```
GET /quantitativointerrupcoesativas
```

### Stack Tecnica

| Componente | Tecnologia |
|------------|------------|
| Framework | FastAPI (Python 3.11+) |
| Banco de Dados | Oracle 19c (via DBLink) |
| ORM | SQLAlchemy (async) |
| Validacao | Pydantic v2 |
| Cache | Memory Cache (Redis futuro) |
| Testes | pytest + pytest-asyncio |

---

## Decisoes de Design

| Decisao | Escolha | Justificativa |
|---------|---------|---------------|
| Arquitetura | Clean Architecture | Separacao de responsabilidades |
| Patterns | DDD + Result Pattern | Modelagem de dominio rica |
| Repository | Protocol (typing) | Inversao de dependencia |
| Cache | Memory (5 min TTL) | Performance ANEEL |
| Autenticacao | API Key (x-api-key) | Requisito ANEEL |
| Rate Limit | 12 req/min | Requisito ANEEL |

---

## Formato de Resposta (ANEEL)

```json
{
  "idcStatusRequisicao": 1,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "",
  "interrupcaoFornecimento": [
    {
      "ideConjuntoUnidadeConsumidora": 1,
      "ideMunicipio": 1400100,
      "qtdUCsAtendidas": 150000,
      "qtdOcorrenciaProgramada": 500,
      "qtdOcorrenciaNaoProgramada": 1200
    }
  ]
}
```

---

## Tasks de Implementacao

### Fase 1: Domain Layer (RAD-100 a RAD-104)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-100 | Value Object CodigoIBGE | Alta | [RAD-100.md](./RAD-100.md) |
| RAD-101 | Value Object TipoInterrupcao | Alta | [RAD-101.md](./RAD-101.md) |
| RAD-102 | Entity Interrupcao | Alta | [RAD-102.md](./RAD-102.md) |
| RAD-103 | Result Pattern | Alta | [RAD-103.md](./RAD-103.md) |
| RAD-104 | Protocol InterrupcaoRepository | Alta | [RAD-104.md](./RAD-104.md) |

### Fase 2: Application Layer (RAD-105 a RAD-107)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-105 | Domain Service InterrupcaoAggregator | Alta | [RAD-105.md](./RAD-105.md) |
| RAD-106 | Protocol CacheService | Alta | [RAD-106.md](./RAD-106.md) |
| RAD-107 | Use Case GetInterrupcoesAtivas | Alta | [RAD-107.md](./RAD-107.md) |

### Fase 3: Infrastructure Layer (RAD-108 a RAD-111)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-108 | Oracle Connection Pool | Alta | [RAD-108.md](./RAD-108.md) |
| RAD-109 | Oracle InterrupcaoRepository | Alta | [RAD-109.md](./RAD-109.md) |
| RAD-110 | Memory Cache Service | Media | [RAD-110.md](./RAD-110.md) |
| RAD-111 | Settings/Config | Alta | [RAD-111.md](./RAD-111.md) |

### Fase 4: Interfaces Layer (RAD-112 a RAD-116)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-112 | Schemas Pydantic (ANEEL) | Alta | [RAD-112.md](./RAD-112.md) |
| RAD-113 | Dependencies (DI) | Alta | [RAD-113.md](./RAD-113.md) |
| RAD-114 | Middlewares (Logging/Error) | Media | [RAD-114.md](./RAD-114.md) |
| RAD-115 | Routes/Endpoints | Alta | [RAD-115.md](./RAD-115.md) |
| RAD-116 | Main App Factory | Alta | [RAD-116.md](./RAD-116.md) |

### Fase 5: Testes TDD (RAD-117 a RAD-121)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-117 | Testes Unit - Value Objects | Critica | [RAD-117.md](./RAD-117.md) |
| RAD-118 | Testes Unit - Entity | Critica | [RAD-118.md](./RAD-118.md) |
| RAD-119 | Testes Unit - Use Case | Critica | [RAD-119.md](./RAD-119.md) |
| RAD-120 | Testes Integration - Repository | Critica | [RAD-120.md](./RAD-120.md) |
| RAD-121 | Testes E2E - API | Critica | [RAD-121.md](./RAD-121.md) |

### Fase 6: Seguranca e Compliance (RAD-122 a RAD-125)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-122 | Autenticacao API Key | Alta | [RAD-122.md](./RAD-122.md) |
| RAD-123 | Rate Limiting (12 req/min) | Alta | [RAD-123.md](./RAD-123.md) |
| RAD-124 | IP Whitelist ANEEL | Media | [RAD-124.md](./RAD-124.md) |
| RAD-125 | Validacao Final ANEEL | Critica | [RAD-125.md](./RAD-125.md) |

---

## Grafo de Dependencias

```
RAD-100 (CodigoIBGE)
RAD-101 (TipoInterrupcao)
    |
    +---> RAD-102 (Entity Interrupcao)
    |         |
RAD-103      |
(Result)     |
    |        |
    +--------+---> RAD-104 (Protocol Repository)
                        |
                        +---> RAD-105 (Aggregator Service)
                        |         |
                   RAD-106        |
                   (Cache)        |
                        |         |
                        +---------+---> RAD-107 (Use Case)
                                             |
    +----------------------------------------+
    |
    +---> RAD-108 (Oracle Connection)
    |         |
    |         +---> RAD-109 (Oracle Repository)
    |
    +---> RAD-110 (Memory Cache)
    |
    +---> RAD-111 (Settings)
    |
    +---> RAD-112 (Schemas)
    |         |
    |         +---> RAD-113 (Dependencies)
    |                   |
    +---> RAD-114       +---> RAD-115 (Routes)
    (Middlewares)             |
          |                   |
          +-------------------+---> RAD-116 (Main App)
                                        |
    +-----------------------------------+
    |
    +---> RAD-117 a RAD-121 (Testes)
    |
    +---> RAD-122 a RAD-125 (Seguranca)
```

---

## Arquivos a Criar

### Backend - Domain
- `backend/shared/domain/value_objects/codigo_ibge.py`
- `backend/shared/domain/value_objects/tipo_interrupcao.py`
- `backend/shared/domain/entities/interrupcao.py`
- `backend/shared/domain/result.py`
- `backend/shared/domain/repositories/interrupcao_repository.py`
- `backend/shared/domain/services/interrupcao_aggregator.py`

### Backend - Infrastructure
- `backend/shared/infrastructure/database/oracle_connection.py`
- `backend/shared/infrastructure/cache/memory_cache.py`
- `backend/shared/infrastructure/config.py`

### Backend - API
- `backend/apps/api_interrupcoes/main.py`
- `backend/apps/api_interrupcoes/routes.py`
- `backend/apps/api_interrupcoes/schemas.py`
- `backend/apps/api_interrupcoes/dependencies.py`
- `backend/apps/api_interrupcoes/middleware.py`
- `backend/apps/api_interrupcoes/repositories/oracle_interrupcao_repository.py`
- `backend/apps/api_interrupcoes/use_cases/get_interrupcoes_ativas.py`

### Testes
- `backend/tests/conftest.py`
- `backend/tests/unit/domain/value_objects/test_codigo_ibge.py`
- `backend/tests/unit/domain/value_objects/test_tipo_interrupcao.py`
- `backend/tests/unit/domain/entities/test_interrupcao.py`
- `backend/tests/unit/use_cases/test_get_interrupcoes_ativas.py`
- `backend/tests/integration/repositories/test_oracle_interrupcao_repository.py`
- `backend/tests/e2e/api/test_interrupcoes.py`

---

## Metricas de Qualidade

| Metrica | Meta | Bloqueante |
|---------|------|------------|
| Coverage de Testes | >= 80% | Sim |
| Testes Unitarios | 100% pass | Sim |
| Testes Integracao | 100% pass | Sim |
| Tempo de Resposta API | < 2s | Sim |
| Rate Limiting | 12 req/min | Sim |

---

## Referencias

- [Especificacao API 1 - ANEEL](../../api-specs/01-interrupcoes.md)
- [OpenAPI Specification](../../api-specs/openapi-api1-interrupcoes.yaml)
- [Plano de Testes](../../testing/api1-test-plan.md)
- [Clean Architecture](../../development/01-clean-architecture.md)
- [DDD](../../development/03-domain-driven-design.md)
- [TDD](../../development/04-tdd-test-driven-development.md)

---

**Proximo Passo:** Ver [INDEX.md](./INDEX.md) para navegacao detalhada das tasks.
