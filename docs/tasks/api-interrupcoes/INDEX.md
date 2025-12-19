# Indice de Tasks - API 1 Interrupcoes

**Projeto:** RADAR - API Quantitativo de Interrupcoes Ativas
**Total de Tasks:** 26 (RAD-100 a RAD-125)
**Ultima Atualizacao:** 2025-12-19

---

## Navegacao Rapida

- [Fase 1: Domain Layer](#fase-1-domain-layer-rad-100-a-rad-104)
- [Fase 2: Application Layer](#fase-2-application-layer-rad-105-a-rad-107)
- [Fase 3: Infrastructure Layer](#fase-3-infrastructure-layer-rad-108-a-rad-111)
- [Fase 4: Interfaces Layer](#fase-4-interfaces-layer-rad-112-a-rad-116)
- [Fase 5: Testes TDD](#fase-5-testes-tdd-rad-117-a-rad-121)
- [Fase 6: Seguranca e Compliance](#fase-6-seguranca-e-compliance-rad-122-a-rad-125)
- [Documentos de Referencia](#documentos-de-referencia)
- [Matriz de Dependencias](#matriz-de-dependencias)

---

## Fase 1: Domain Layer (RAD-100 a RAD-104)

### Camada: Value Objects

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-100** | Value Object CodigoIBGE | Domain | Alta | - | [RAD-100.md](./RAD-100.md) |
| **RAD-101** | Value Object TipoInterrupcao | Domain | Alta | - | [RAD-101.md](./RAD-101.md) |

**Descricao RAD-100:** Criar Value Object imutavel para codigo IBGE de municipio (7 digitos), com validacao de pertencer a Roraima.

**Descricao RAD-101:** Criar Enum Value Object para tipo de interrupcao (PROGRAMADA/NAO_PROGRAMADA), com factory from_plan_id().

**Entregaveis:**
- `backend/shared/domain/value_objects/codigo_ibge.py`
- `backend/shared/domain/value_objects/tipo_interrupcao.py`

---

### Camada: Entities

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-102** | Entity Interrupcao | Domain | Alta | RAD-100, RAD-101 | [RAD-102.md](./RAD-102.md) |

**Descricao:** Criar entidade Interrupcao com comportamentos de negocio (is_ativa, is_programada) e factory method com validacao de invariantes.

**Entregaveis:**
- `backend/shared/domain/entities/interrupcao.py`

---

### Camada: Core

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-103** | Result Pattern | Domain | Alta | - | [RAD-103.md](./RAD-103.md) |
| **RAD-104** | Protocol InterrupcaoRepository | Domain | Alta | RAD-102 | [RAD-104.md](./RAD-104.md) |

**Descricao RAD-103:** Implementar Result Pattern generico para tratamento de erros sem exceptions (Result.ok, Result.fail).

**Descricao RAD-104:** Criar Protocol (interface) para repositorio de interrupcoes, seguindo Dependency Inversion Principle.

**Entregaveis:**
- `backend/shared/domain/result.py`
- `backend/shared/domain/repositories/interrupcao_repository.py`

---

## Fase 2: Application Layer (RAD-105 a RAD-107)

### Camada: Domain Services

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-105** | Domain Service InterrupcaoAggregator | Application | Alta | RAD-102 | [RAD-105.md](./RAD-105.md) |

**Descricao:** Criar servico de dominio para agregar interrupcoes por Municipio + Conjunto, separando programadas de nao programadas.

**Entregaveis:**
- `backend/shared/domain/services/interrupcao_aggregator.py`

---

### Camada: Protocols

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-106** | Protocol CacheService | Application | Alta | - | [RAD-106.md](./RAD-106.md) |

**Descricao:** Criar Protocol para servico de cache com metodos get, set, invalidate.

**Entregaveis:**
- `backend/shared/domain/protocols/cache_service.py`

---

### Camada: Use Cases

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-107** | Use Case GetInterrupcoesAtivas | Application | Alta | RAD-104, RAD-105, RAD-106 | [RAD-107.md](./RAD-107.md) |

**Descricao:** Criar caso de uso que orquestra busca de interrupcoes com cache, agregacao e retorno no formato esperado.

**Entregaveis:**
- `backend/apps/api_interrupcoes/use_cases/get_interrupcoes_ativas.py`

---

## Fase 3: Infrastructure Layer (RAD-108 a RAD-111)

### Camada: Database

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-108** | Oracle Connection Pool | Infrastructure | Alta | - | [RAD-108.md](./RAD-108.md) |
| **RAD-109** | Oracle InterrupcaoRepository | Infrastructure | Alta | RAD-104, RAD-108 | [RAD-109.md](./RAD-109.md) |

**Descricao RAD-108:** Configurar connection pool async para Oracle com SQLAlchemy e oracledb.

**Descricao RAD-109:** Implementar repositorio concreto com query via DBLink (INSERVICE, INDICADORES).

**Entregaveis:**
- `backend/shared/infrastructure/database/oracle_connection.py`
- `backend/apps/api_interrupcoes/repositories/oracle_interrupcao_repository.py`

---

### Camada: Cache e Config

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-110** | Memory Cache Service | Infrastructure | Media | RAD-106 | [RAD-110.md](./RAD-110.md) |
| **RAD-111** | Settings/Config | Infrastructure | Alta | - | [RAD-111.md](./RAD-111.md) |

**Descricao RAD-110:** Implementar cache em memoria com TTL de 5 minutos.

**Descricao RAD-111:** Configurar Settings com Pydantic BaseSettings para variaveis de ambiente.

**Entregaveis:**
- `backend/shared/infrastructure/cache/memory_cache.py`
- `backend/shared/infrastructure/config.py`

---

## Fase 4: Interfaces Layer (RAD-112 a RAD-116)

### Camada: Schemas

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-112** | Schemas Pydantic (ANEEL) | Interfaces | Alta | - | [RAD-112.md](./RAD-112.md) |

**Descricao:** Criar schemas Pydantic no formato exato especificado pela ANEEL (camelCase, campos obrigatorios).

**Entregaveis:**
- `backend/apps/api_interrupcoes/schemas.py`

---

### Camada: Dependency Injection

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-113** | Dependencies (DI) | Interfaces | Alta | RAD-107, RAD-109, RAD-110 | [RAD-113.md](./RAD-113.md) |

**Descricao:** Configurar injecao de dependencias via FastAPI Depends() para repository, cache e use case.

**Entregaveis:**
- `backend/apps/api_interrupcoes/dependencies.py`

---

### Camada: Middlewares

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-114** | Middlewares (Logging/Error) | Interfaces | Media | - | [RAD-114.md](./RAD-114.md) |

**Descricao:** Criar middlewares para logging de requisicoes e tratamento global de erros.

**Entregaveis:**
- `backend/apps/api_interrupcoes/middleware.py`

---

### Camada: API

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-115** | Routes/Endpoints | API | Alta | RAD-112, RAD-113 | [RAD-115.md](./RAD-115.md) |
| **RAD-116** | Main App Factory | API | Alta | RAD-114, RAD-115 | [RAD-116.md](./RAD-116.md) |

**Descricao RAD-115:** Criar endpoints GET /quantitativointerrupcoesativas e /health.

**Descricao RAD-116:** Criar application factory com lifespan, middlewares e rotas.

**Entregaveis:**
- `backend/apps/api_interrupcoes/routes.py`
- `backend/apps/api_interrupcoes/main.py`

---

## Fase 5: Testes TDD (RAD-117 a RAD-121)

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-117** | Testes Unit - Value Objects | Test | Critica | RAD-100, RAD-101 | [RAD-117.md](./RAD-117.md) |
| **RAD-118** | Testes Unit - Entity | Test | Critica | RAD-102 | [RAD-118.md](./RAD-118.md) |
| **RAD-119** | Testes Unit - Use Case | Test | Critica | RAD-107 | [RAD-119.md](./RAD-119.md) |
| **RAD-120** | Testes Integration - Repository | Test | Critica | RAD-109 | [RAD-120.md](./RAD-120.md) |
| **RAD-121** | Testes E2E - API | Test | Critica | RAD-116 | [RAD-121.md](./RAD-121.md) |

**Entregaveis Fase 5:**
- `backend/tests/conftest.py`
- `backend/tests/unit/domain/value_objects/test_codigo_ibge.py`
- `backend/tests/unit/domain/value_objects/test_tipo_interrupcao.py`
- `backend/tests/unit/domain/entities/test_interrupcao.py`
- `backend/tests/unit/use_cases/test_get_interrupcoes_ativas.py`
- `backend/tests/integration/repositories/test_oracle_interrupcao_repository.py`
- `backend/tests/e2e/api/test_interrupcoes.py`

---

## Fase 6: Seguranca e Compliance (RAD-122 a RAD-125)

| Task | Titulo | Tipo | Prioridade | Dependencias | Arquivo |
|------|--------|------|------------|--------------|---------|
| **RAD-122** | Autenticacao API Key | Security | Alta | RAD-113 | [RAD-122.md](./RAD-122.md) |
| **RAD-123** | Rate Limiting (12 req/min) | Security | Alta | RAD-116 | [RAD-123.md](./RAD-123.md) |
| **RAD-124** | IP Whitelist ANEEL | Security | Media | RAD-113 | [RAD-124.md](./RAD-124.md) |
| **RAD-125** | Validacao Final ANEEL | Compliance | Critica | Todas | [RAD-125.md](./RAD-125.md) |

**Descricao RAD-122:** Implementar validacao de API Key no header x-api-key.

**Descricao RAD-123:** Implementar rate limiting de 12 requisicoes por minuto.

**Descricao RAD-124:** Implementar whitelist de IPs autorizados da ANEEL.

**Descricao RAD-125:** Validacao final de conformidade com especificacao ANEEL.

**Entregaveis Fase 6:**
- Atualizacao de `dependencies.py` com autenticacao
- Middleware de rate limiting
- Validacao de IP whitelist
- Relatorio de conformidade

---

## Documentos de Referencia

| Documento | Descricao | Arquivo |
|-----------|-----------|---------|
| Plano Geral | Visao geral do projeto | [PLAN.md](./PLAN.md) |
| Status de Execucao | Controle de progresso | [EXECUTION_STATUS.md](./EXECUTION_STATUS.md) |
| Especificacao API | Detalhes da API ANEEL | [../../api-specs/01-interrupcoes.md](../../api-specs/01-interrupcoes.md) |
| OpenAPI Spec | Swagger/OpenAPI | [../../api-specs/openapi-api1-interrupcoes.yaml](../../api-specs/openapi-api1-interrupcoes.yaml) |
| Plano de Testes | Casos de teste | [../../testing/api1-test-plan.md](../../testing/api1-test-plan.md) |

---

## Matriz de Dependencias

### Tabela de Dependencias Diretas

| Task | Depende de | Bloqueia |
|------|------------|----------|
| RAD-100 | - | RAD-102 |
| RAD-101 | - | RAD-102 |
| RAD-102 | RAD-100, RAD-101 | RAD-104, RAD-105, RAD-118 |
| RAD-103 | - | RAD-107 |
| RAD-104 | RAD-102 | RAD-107, RAD-109 |
| RAD-105 | RAD-102 | RAD-107 |
| RAD-106 | - | RAD-107, RAD-110 |
| RAD-107 | RAD-103, RAD-104, RAD-105, RAD-106 | RAD-113, RAD-119 |
| RAD-108 | - | RAD-109 |
| RAD-109 | RAD-104, RAD-108 | RAD-113, RAD-120 |
| RAD-110 | RAD-106 | RAD-113 |
| RAD-111 | - | RAD-108, RAD-116 |
| RAD-112 | - | RAD-115 |
| RAD-113 | RAD-107, RAD-109, RAD-110 | RAD-115, RAD-122, RAD-124 |
| RAD-114 | - | RAD-116 |
| RAD-115 | RAD-112, RAD-113 | RAD-116 |
| RAD-116 | RAD-114, RAD-115 | RAD-121, RAD-123 |
| RAD-117 | RAD-100, RAD-101 | - |
| RAD-118 | RAD-102 | - |
| RAD-119 | RAD-107 | - |
| RAD-120 | RAD-109 | - |
| RAD-121 | RAD-116 | - |
| RAD-122 | RAD-113 | RAD-125 |
| RAD-123 | RAD-116 | RAD-125 |
| RAD-124 | RAD-113 | RAD-125 |
| RAD-125 | Todas | - |

---

## Metricas do Projeto

| Metrica | Valor |
|---------|-------|
| Total de Tasks | 26 |
| Tasks Domain | 5 |
| Tasks Application | 3 |
| Tasks Infrastructure | 4 |
| Tasks Interfaces | 5 |
| Tasks Testes | 5 |
| Tasks Seguranca | 4 |
| Fases | 6 |
| Coverage Minimo | 80% |

---

## Legenda de Prioridades

| Prioridade | Descricao |
|------------|-----------|
| **Critica** | Bloqueia entrega, requisito ANEEL |
| **Alta** | Core do sistema, deve ser feito primeiro |
| **Media** | Importante mas nao bloqueante |
| **Baixa** | Nice-to-have, pode ser adiado |

---

## Legenda de Tipos

| Tipo | Descricao |
|------|-----------|
| **Domain** | Camada de dominio (entities, VOs) |
| **Application** | Camada de aplicacao (use cases, services) |
| **Infrastructure** | Camada de infraestrutura (DB, cache) |
| **Interfaces** | Camada de interfaces (API, schemas) |
| **Test** | Testes automatizados |
| **Security** | Seguranca e autenticacao |
| **Compliance** | Conformidade com ANEEL |

---

**Proximo Passo:** Ver [EXECUTION_STATUS.md](./EXECUTION_STATUS.md) para acompanhar o progresso de execucao.
