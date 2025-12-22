# Indice de Tasks - Projeto RADAR

**Projeto:** RADAR - Sistema de Monitoramento de Indicadores ANEEL
**Total de Tasks:** 62 (RAD-100 a RAD-130 + RAD-200 a RAD-230)
**Ultima Atualizacao:** 2025-12-19

---

## Navegacao Rapida

| Documento | Descricao |
|-----------|-----------|
| [VISIBILIDADE_INTEGRADA_PROJETO_RADAR.md](./VISIBILIDADE_INTEGRADA_PROJETO_RADAR.md) | **Visao completa do projeto** - APIs ANEEL + Dashboard/Mapa RR |

### API 1 - Interrupcoes ANEEL

| Documento | Descricao |
|-----------|-----------|
| [api-interrupcoes/PLAN.md](./api-interrupcoes/PLAN.md) | Plano de implementacao API 1 |
| [api-interrupcoes/INDEX.md](./api-interrupcoes/INDEX.md) | Indice detalhado das 31 tasks |
| [api-interrupcoes/ADERENCIA_DESIGN.md](./api-interrupcoes/ADERENCIA_DESIGN.md) | **Validacao tasks vs documentos de design** |
| [api-interrupcoes/EXECUTION_STATUS.md](./api-interrupcoes/EXECUTION_STATUS.md) | Status atual de execucao |

### Mapa de Interrupcoes Roraima (Portal Publico)

| Documento | Descricao |
|-----------|-----------|
| [mapa-interrupcoes/PLAN.md](./mapa-interrupcoes/PLAN.md) | Plano de implementacao Mapa |
| [mapa-interrupcoes/INDEX.md](./mapa-interrupcoes/INDEX.md) | Indice detalhado das 31 tasks (RAD-200 a RAD-230) |

---

## Contextos do Projeto

O projeto RADAR possui dois contextos principais:

### Contexto 1: APIs ANEEL (Regulatorio)

**Prazo:** Dezembro/2025
**Base Legal:** Oficio Circular 14/2025-SFE/ANEEL

| API | Endpoint | Status | Tasks |
|-----|----------|--------|-------|
| API 1 - Interrupcoes | `/quantitativointerrupcoesativas` | Em Desenvolvimento | RAD-100 a RAD-130 |
| API 2 - Demanda | `/quantitativoreclamacoespordemanda` | Planejado | - |
| API 3 - Demandas Diversas | `/quantitativoreclamacoesdemandasdiversas` | Planejado | - |
| API 4 - Tempo Real | `/tempomedioatendimento` | Planejado | - |

### Contexto 2: Mapa de Interrupcoes RR (Portal Publico)

**Prazo:** 180 dias apos vigencia REN 1.137/2025 (~Abril 2026)
**Base Legal:** REN 1.137/2025 - Art. 106-107
**Referencia:** [PowerOutage.us](https://poweroutage.us/)

| Componente | Descricao | Status | Tasks |
|------------|-----------|--------|-------|
| Backend Domain | Value Objects, Entity, Services | PENDENTE | RAD-200 a RAD-204 |
| Backend Application | Protocols, Use Cases | PENDENTE | RAD-205 a RAD-207 |
| Backend Infrastructure | Repository Oracle, MV, Scheduler | PENDENTE | RAD-208 a RAD-211 |
| Backend API | Endpoints REST | PENDENTE | RAD-212 a RAD-215 |
| Frontend React | Mapa Leaflet, Dashboard | PENDENTE | RAD-216 a RAD-222 |
| Testes | Unit, Integration, E2E, WCAG | PENDENTE | RAD-223 a RAD-227 |
| Deploy | NGINX, Health Check, Docs | PENDENTE | RAD-228 a RAD-230 |

---

## Estrutura de Tasks

### API 1 - Interrupcoes Ativas

```
docs/tasks/api-interrupcoes/
├── PLAN.md                 # Plano geral
├── INDEX.md                # Indice das tasks
├── EXECUTION_STATUS.md     # Status de execucao
├── RAD-100.md              # Value Object CodigoIBGE
├── RAD-101.md              # Value Object TipoInterrupcao
├── RAD-102.md              # Entity Interrupcao
├── RAD-103.md              # Result Pattern
├── RAD-104.md              # Protocol Repository
├── RAD-105.md              # Domain Service Aggregator
├── RAD-106.md              # Protocol CacheService
├── RAD-107.md              # Use Case GetInterrupcoesAtivas
├── RAD-108.md              # Oracle Connection Pool
├── RAD-109.md              # Oracle Repository
├── RAD-110.md              # Memory Cache Service
├── RAD-111.md              # Settings/Config
├── RAD-112.md              # Schemas Pydantic
├── RAD-113.md              # Dependencies (DI)
├── RAD-114.md              # Middlewares
├── RAD-115.md              # Routes/Endpoints
├── RAD-116.md              # Main App Factory
├── RAD-117.md              # Testes Unit - Value Objects
├── RAD-118.md              # Testes Unit - Entity
├── RAD-119.md              # Testes Unit - Use Case
├── RAD-120.md              # Testes Integration
├── RAD-121.md              # Testes E2E
├── RAD-122.md              # Autenticacao API Key
├── RAD-123.md              # Rate Limiting (10 req/min)
├── RAD-124.md              # Logging e Auditoria
├── RAD-125.md              # Documentacao OpenAPI
├── RAD-126.md              # Alembic Migrations
├── RAD-127.md              # Tabelas Auditoria
├── RAD-128.md              # View VW_INTERRUPCAO_FORNECIMENTO
├── RAD-129.md              # Entity Consulta
└── RAD-130.md              # IP Whitelist ANEEL
```

### Mapa de Interrupcoes Roraima (Portal Publico)

```
docs/tasks/mapa-interrupcoes/
├── PLAN.md                 # Plano geral
├── INDEX.md                # Indice das tasks
├── RAD-200.md              # Value Object FaixaDuracao
├── RAD-201.md              # Value Object StatusOcorrencia
├── RAD-202.md              # Value Object Coordenadas
├── RAD-203.md              # Entity InterrupcaoMapa
├── RAD-204.md              # Domain Service CalculadorCHI
├── RAD-205.md              # Protocol MapaRepository
├── RAD-206.md              # Use Case GetInterrupcoesMapa
├── RAD-207.md              # Use Case GetEquipesEmCampo
├── RAD-208.md              # Oracle MapaRepository
├── RAD-209.md              # Materialized View MV_PORTAL_PUBLICO
├── RAD-210.md              # Scheduler Celery (30 min)
├── RAD-211.md              # GeoJSON Municipios Roraima
├── RAD-212.md              # Schemas Pydantic
├── RAD-213.md              # Endpoint GET /api/mapa/interrupcoes
├── RAD-214.md              # Endpoint GET /api/mapa/municipios
├── RAD-215.md              # Endpoint GET /api/mapa/estatisticas
├── RAD-216.md              # Setup React + TypeScript + Vite
├── RAD-217.md              # Componente MapaRoraima (Leaflet)
├── RAD-218.md              # Componente PainelEstatisticas
├── RAD-219.md              # Componente ListaInterrupcoes
├── RAD-220.md              # Componente FiltroFaixaDuracao
├── RAD-221.md              # Componente GraficoEvolucao
├── RAD-222.md              # Layout Responsivo (Mobile)
├── RAD-223.md              # Testes Unit - Value Objects
├── RAD-224.md              # Testes Unit - Use Cases
├── RAD-225.md              # Testes Integration - Repository
├── RAD-226.md              # Testes E2E - Frontend
├── RAD-227.md              # Testes Acessibilidade (WCAG)
├── RAD-228.md              # Configuracao NGINX (SSL, Cache)
├── RAD-229.md              # Monitoramento (Health Check)
└── RAD-230.md              # Documentacao Usuario Final
```

---

## Fases de Implementacao

### API 1 - Interrupcoes ANEEL (RAD-100 a RAD-130)

| Fase | Descricao | Tasks | Progresso |
|------|-----------|-------|-----------|
| **Fase 1** | Domain Layer | RAD-100 a RAD-104 | 80% |
| **Fase 2** | Application Layer | RAD-105 a RAD-107 | 33% |
| **Fase 3** | Infrastructure Layer | RAD-108 a RAD-111 | 75% |
| **Fase 4** | Interfaces Layer | RAD-112 a RAD-116 | 100% |
| **Fase 5** | Testes TDD | RAD-117 a RAD-121 | 0% |
| **Fase 6** | Seguranca e Compliance | RAD-122-125, RAD-130 | 25% |
| **Fase 7** | Infraestrutura de Dados | RAD-126 a RAD-129 | 0% |

### Mapa de Interrupcoes Roraima (RAD-200 a RAD-230)

| Fase | Descricao | Tasks | Progresso |
|------|-----------|-------|-----------|
| **Fase 1** | Domain Layer | RAD-200 a RAD-204 | 0% |
| **Fase 2** | Application Layer | RAD-205 a RAD-207 | 0% |
| **Fase 3** | Infrastructure Layer | RAD-208 a RAD-211 | 0% |
| **Fase 4** | API Endpoints | RAD-212 a RAD-215 | 0% |
| **Fase 5** | Frontend React | RAD-216 a RAD-222 | 0% |
| **Fase 6** | Testes TDD | RAD-223 a RAD-227 | 0% |
| **Fase 7** | Deploy e Operacao | RAD-228 a RAD-230 | 0% |

---

## Progresso Geral

### API 1 - Interrupcoes ANEEL

```
Domain Layer:        [████████░░] 80%
Application Layer:   [███░░░░░░░] 33%
Infrastructure:      [███████░░░] 75%
Interfaces:          [██████████] 100%
Testes TDD:          [░░░░░░░░░░] 0%   <- CRITICO
Seguranca:           [██░░░░░░░░] 25%
Infraestrutura DB:   [░░░░░░░░░░] 0%
───────────────────────────────────────
TOTAL:               [██████░░░░] ~55%
```

### Mapa de Interrupcoes Roraima

```
Domain Layer:        [░░░░░░░░░░] 0%
Application Layer:   [░░░░░░░░░░] 0%
Infrastructure:      [░░░░░░░░░░] 0%
API Endpoints:       [░░░░░░░░░░] 0%
Frontend React:      [░░░░░░░░░░] 0%
Testes TDD:          [░░░░░░░░░░] 0%
Deploy:              [░░░░░░░░░░] 0%
───────────────────────────────────────
TOTAL:               [░░░░░░░░░░] 0%
```

---

## Prioridades Criticas

### Bloqueadores de Entrega

| # | Task | Descricao | Impacto |
|---|------|-----------|---------|
| 1 | RAD-117 | Testes Unit Value Objects | Coverage 0% |
| 2 | RAD-118 | Testes Unit Entity | Coverage 0% |
| 3 | RAD-119 | Testes Unit Use Case | Coverage 0% |
| 4 | RAD-120 | Testes Integration | Validacao Oracle |
| 5 | RAD-121 | Testes E2E | Validacao API |
| 6 | RAD-123 | Rate Limiting (10 req/min) | Requisito ANEEL |
| 7 | RAD-130 | IP Whitelist ANEEL | Requisito ANEEL |

**Meta de Cobertura:** >= 80%

---

## Requisitos ANEEL

### Oficio Circular 14/2025-SFE/ANEEL (API 1)

| Requisito | Task | Status |
|-----------|------|--------|
| Endpoint minusculo | RAD-115 | OK |
| Formato JSON camelCase | RAD-112 | OK |
| Campos obrigatorios | RAD-112 | OK |
| Autenticacao x-api-key | RAD-122 | OK |
| Rate Limiting 10 req/min | RAD-123 | PENDENTE |
| IP Whitelist 200.198.220.128/25 | RAD-130 | PENDENTE |
| Historico 7 dias | - | Abril/2026 |

### REN 1.137/2025 Art. 106-107 (Mapa Portal Publico)

| Requisito | Task | Status |
|-----------|------|--------|
| Mapa georreferenciado | RAD-217 | PENDENTE |
| Atualizacao 30 minutos | RAD-210 | PENDENTE |
| Acesso publico | RAD-213 | PENDENTE |
| Faixas de duracao (7 faixas) | RAD-200 | PENDENTE |
| Status da ocorrencia | RAD-201 | PENDENTE |
| CHI (Consumidor Hora Interrompido) | RAD-204 | PENDENTE |
| Equipes em campo | RAD-207 | PENDENTE |
| Causa (quando conhecida) | RAD-203 | PENDENTE |
| Previsao restabelecimento | RAD-203 | PENDENTE |
| Acessibilidade WCAG 2.1 AA | RAD-227 | PENDENTE |

---

## Documentacao Relacionada

| Area | Documento |
|------|-----------|
| **Arquitetura** | [../development/01-clean-architecture.md](../development/01-clean-architecture.md) |
| **SOLID** | [../development/02-solid-principles.md](../development/02-solid-principles.md) |
| **DDD** | [../development/03-domain-driven-design.md](../development/03-domain-driven-design.md) |
| **TDD** | [../development/04-tdd-test-driven-development.md](../development/04-tdd-test-driven-development.md) |
| **Clean Code** | [../development/05-clean-code.md](../development/05-clean-code.md) |
| **API Specs** | [../api-specs/01-interrupcoes.md](../api-specs/01-interrupcoes.md) |
| **OpenAPI** | [../api-specs/openapi-api1-interrupcoes.yaml](../api-specs/openapi-api1-interrupcoes.yaml) |
| **Plano de Testes** | [../testing/api1-test-plan.md](../testing/api1-test-plan.md) |
| **Diagramas** | [../design/DIAGRAMAS_MERMAID_RADAR_RR.md](../design/DIAGRAMAS_MERMAID_RADAR_RR.md) |

---

## Comandos Uteis

```bash
# Iniciar task
/start-task RAD-117

# Verificar status
/workflow-status

# Executar testes
pytest backend/tests/ -v --cov=backend --cov-fail-under=80

# Validar arquitetura
@clean-architecture-guardian validate
```

---

**Proximo Passo:**
- API 1 ANEEL: Ver [api-interrupcoes/PLAN.md](./api-interrupcoes/PLAN.md)
- Mapa Portal Publico: Ver [mapa-interrupcoes/PLAN.md](./mapa-interrupcoes/PLAN.md)
