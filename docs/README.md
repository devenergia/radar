# Documentacao RADAR - Sistema de Monitoramento de Interrupcoes

> Indice completo da documentacao do Projeto RADAR - Roraima Energia S/A

**Versao:** 2.0 | **Atualizado:** 2025-12-19 | **Status:** Em Desenvolvimento

---

## Visao Geral do Projeto

O Projeto RADAR e composto por **dois contextos principais**:

| Contexto | Objetivo | Prazo |
|----------|----------|-------|
| **APIs ANEEL** | Atender requisitos regulatorios do Oficio Circular 14/2025-SFE/ANEEL | Dez/2025 |
| **Dashboard/Mapa RR** | Monitoramento estilo PowerOutage.us + Portal Publico REN 1.137 | 2026 |

**Documento Principal:** [Visibilidade Integrada do Projeto](tasks/VISIBILIDADE_INTEGRADA_PROJETO_RADAR.md)

---

## Estrutura da Documentacao

```
docs/
├── official/           # Documentos oficiais ANEEL (PDFs)
├── design/             # Arquitetura e design do sistema
├── analysis/           # Analises e requisitos
├── api-specs/          # Especificacoes das APIs ANEEL
├── architecture/       # Documentacao tecnica de arquitetura
├── adr/                # Architectural Decision Records
├── development/        # Guias de desenvolvimento
├── database/           # Configuracao de banco de dados
├── testing/            # Planos de teste
├── deployment/         # Guias de deploy
├── operations/         # Runbooks e troubleshooting
├── reports/            # Relatorios de atividades
└── tasks/              # TASKS DE IMPLEMENTACAO
    ├── VISIBILIDADE_INTEGRADA_PROJETO_RADAR.md
    └── api-interrupcoes/   # Tasks da API 1 (RAD-100 a RAD-130)
```

---

## Navegacao Rapida

### Por Perfil

| Perfil | Comece Por |
|--------|------------|
| **Novo no projeto** | [Visibilidade Integrada](tasks/VISIBILIDADE_INTEGRADA_PROJETO_RADAR.md) → [Design Completo](design/DESIGN_ARQUITETURA_RADAR_RR.md) |
| **Desenvolvedor** | [Guias de Desenvolvimento](development/00-index.md) → [Tasks API 1](tasks/api-interrupcoes/INDEX.md) |
| **Arquiteto** | [ADRs](adr/README.md) → [Arquitetura](architecture/README.md) |
| **Gestor** | [Plano API 1](tasks/api-interrupcoes/PLAN.md) → [Status de Execucao](tasks/api-interrupcoes/EXECUTION_STATUS.md) |

### Por Urgencia

| Prioridade | O Que | Prazo | Documentos |
|------------|-------|-------|------------|
| **CRITICA** | API 1 - Interrupcoes Ativas | Dez/2025 | [Tasks](tasks/api-interrupcoes/INDEX.md) |
| Alta | API 2 e API 3 - Demandas | Abr/2026 | [Specs](api-specs/) |
| Media | Dashboard/Mapa RR | Jun/2026 | [Diagramas](design/DIAGRAMAS_MERMAID_RADAR_RR.md) |

---

## 1. Tasks de Implementacao

### Visao Integrada

| Documento | Descricao |
|-----------|-----------|
| [**VISIBILIDADE_INTEGRADA_PROJETO_RADAR.md**](tasks/VISIBILIDADE_INTEGRADA_PROJETO_RADAR.md) | Visao completa: APIs ANEEL + Dashboard/Mapa RR + Mapa de Roraima |

### API 1 - Quantitativo de Interrupcoes Ativas (31 Tasks)

| Documento | Descricao |
|-----------|-----------|
| [INDEX.md](tasks/api-interrupcoes/INDEX.md) | Indice completo das 31 tasks |
| [PLAN.md](tasks/api-interrupcoes/PLAN.md) | Plano de implementacao |
| [EXECUTION_STATUS.md](tasks/api-interrupcoes/EXECUTION_STATUS.md) | Status atual de execucao |

#### Tasks por Fase

| Fase | Tasks | Descricao | Status |
|------|-------|-----------|--------|
| **Fase 1** | [RAD-100](tasks/api-interrupcoes/RAD-100.md) a [RAD-104](tasks/api-interrupcoes/RAD-104.md) | Domain Layer | 80% |
| **Fase 2** | [RAD-105](tasks/api-interrupcoes/RAD-105.md) a [RAD-107](tasks/api-interrupcoes/RAD-107.md) | Application Layer | 33% |
| **Fase 3** | [RAD-108](tasks/api-interrupcoes/RAD-108.md) a [RAD-111](tasks/api-interrupcoes/RAD-111.md) | Infrastructure Layer | 75% |
| **Fase 4** | [RAD-112](tasks/api-interrupcoes/RAD-112.md) a [RAD-116](tasks/api-interrupcoes/RAD-116.md) | Interfaces Layer | 100% |
| **Fase 5** | [RAD-117](tasks/api-interrupcoes/RAD-117.md) a [RAD-121](tasks/api-interrupcoes/RAD-121.md) | Testes TDD | 0% |
| **Fase 6** | [RAD-122](tasks/api-interrupcoes/RAD-122.md) a [RAD-125](tasks/api-interrupcoes/RAD-125.md), [RAD-130](tasks/api-interrupcoes/RAD-130.md) | Seguranca | 25% |
| **Fase 7** | [RAD-126](tasks/api-interrupcoes/RAD-126.md) a [RAD-129](tasks/api-interrupcoes/RAD-129.md) | Database | 0% |

---

## 2. Documentos Oficiais ANEEL

| Documento | Descricao |
|-----------|-----------|
| [Oficio Circular 14/2025-SFE/ANEEL](official/Oficio_Circular_14-2025_SMA-ANEEL_RADAR.pdf) | Especificacao tecnica das APIs |
| [REN 1.137-2025](official/REN%201.137-2025.pdf) | Resiliencia a Eventos Climaticos Severos |
| [Apresentacao Tecnica](official/RADAR_Apresentação%20Técnica%20-%2030-7-2025.pdf) | Apresentacao do projeto |

---

## 3. Design e Arquitetura

| Documento | Descricao | Linhas |
|-----------|-----------|--------|
| [DESIGN_ARQUITETURA_RADAR_RR.md](design/DESIGN_ARQUITETURA_RADAR_RR.md) | Design completo (v2.0) | 3.968 |
| [DIAGRAMAS_MERMAID_RADAR_RR.md](design/DIAGRAMAS_MERMAID_RADAR_RR.md) | 22 Diagramas Mermaid | 1.997 |
| [INTEGRACAO_SISTEMA_TECNICO_RADAR_RR.md](design/INTEGRACAO_SISTEMA_TECNICO_RADAR_RR.md) | Integracao com sistemas legados | - |

### Diagramas Disponiveis

| # | Diagrama | Contexto |
|---|----------|----------|
| 1 | Arquitetura Geral do Sistema | Ambos |
| 2 | Fluxo de Dados - APIs ANEEL | API ANEEL |
| 3 | Fluxo de Recuperacao de Dados | API ANEEL |
| 4 | Modelo de Dados (ERD) | Ambos |
| 5 | Estados de Demanda | API ANEEL |
| 6 | Componentes do Dashboard | Dashboard RR |
| 7 | APIs - Endpoints ANEEL | API ANEEL |
| 8 | Casos de Uso | Ambos |
| 9 | Cronograma de Implementacao | Ambos |
| 10 | Modelos de Resposta API | API ANEEL |
| 11 | Fluxo de Autenticacao | API ANEEL |
| 12 | Estrutura Geografica de Roraima | Dashboard RR |
| 13 | Niveis de Severidade - Heat Map | Dashboard RR |
| 14 | Canais de Atendimento | Dashboard RR |
| 15 | Infraestrutura de Deploy | Ambos |
| 16 | Sistema de Alertas | Dashboard RR |
| 17 | Dashboard PowerOutage Style | Dashboard RR |
| 18 | Integracao Sistemas Internos | Ambos |
| 19 | Portal Publico de Interrupcoes | Dashboard RR |
| 20 | Sistema de Notificacao SMS/WhatsApp | Dashboard RR |
| 21 | Modulo DISE - Indicador de Emergencia | Dashboard RR |
| 22 | Fluxo de Situacao de Emergencia | Dashboard RR |

---

## 4. Especificacoes das APIs ANEEL

### APIs Principais

| API | Endpoint | Documento | Prazo |
|-----|----------|-----------|-------|
| **API 1** | `/quantitativointerrupcoesativas` | [Especificacao](api-specs/API_01_QUANTITATIVO_INTERRUPCOES_ATIVAS.md) | **Dez/2025** |
| **API 2** | `/dadosdemanda` | [Especificacao](api-specs/API_02_DADOS_DEMANDA.md) | Abr/2026 |
| **API 3** | `/quantitativodemandasdiversas` | [Especificacao](api-specs/API_03_QUANTITATIVO_DEMANDAS_DIVERSAS.md) | Abr/2026 |
| **API 4** | REN 1.137 Tempo Real | [Especificacao](api-specs/API_04_TEMPO_REAL_REN_1137.md) | 60 dias |

### Documentacao Tecnica

| Documento | Descricao |
|-----------|-----------|
| [01-interrupcoes.md](api-specs/01-interrupcoes.md) | Detalhes tecnicos API 1 |
| [02-demandas-diversas.md](api-specs/02-demandas-diversas.md) | Detalhes tecnicos API 3 |
| [03-dados-demanda.md](api-specs/03-dados-demanda.md) | Detalhes tecnicos API 2 |
| [04-seguranca.md](api-specs/04-seguranca.md) | Autenticacao, Rate Limiting, IP Whitelist |
| [openapi-api1-interrupcoes.yaml](api-specs/openapi-api1-interrupcoes.yaml) | OpenAPI 3.0 Spec |

---

## 5. Analises e Requisitos

| Documento | Descricao |
|-----------|-----------|
| [ANALISE_REQUISITOS_RADAR_RR.md](analysis/ANALISE_REQUISITOS_RADAR_RR.md) | Analise completa dos requisitos ANEEL |
| [REQUISITOS_SISTEMA_TECNICO_RADAR.md](analysis/REQUISITOS_SISTEMA_TECNICO_RADAR.md) | Requisitos do sistema tecnico |
| [REQUISITOS_SISTEMA_COMERCIAL_RADAR.md](analysis/REQUISITOS_SISTEMA_COMERCIAL_RADAR.md) | Requisitos do sistema comercial |
| [REQUISITOS_AJURI_API1.md](analysis/REQUISITOS_AJURI_API1.md) | Requisitos AJURI para API 1 |
| [REQUISITOS_SISTEMA_TECNICO_API1.md](analysis/REQUISITOS_SISTEMA_TECNICO_API1.md) | Requisitos tecnicos API 1 |
| [MAPEAMENTO_EQUIPES_SISTEMAS_RADAR.md](analysis/MAPEAMENTO_EQUIPES_SISTEMAS_RADAR.md) | Mapeamento de equipes |
| [MELHORIAS-ABSORVIDAS-RADAR-BACKEND.md](analysis/MELHORIAS-ABSORVIDAS-RADAR-BACKEND.md) | Melhorias incorporadas |

---

## 6. Arquitetura Tecnica

| Documento | Descricao |
|-----------|-----------|
| [README.md](architecture/README.md) | Indice de arquitetura |
| [01-visao-geral.md](architecture/01-visao-geral.md) | Visao geral do sistema |
| [02-arquitetura-hexagonal.md](architecture/02-arquitetura-hexagonal.md) | Ports & Adapters |
| [03-fluxo-dados.md](architecture/03-fluxo-dados.md) | Fluxo de dados |
| [04-diagramas-sequencia.md](architecture/04-diagramas-sequencia.md) | Diagramas de sequencia |
| [05-modelo-dominio.md](architecture/05-modelo-dominio.md) | Modelo de dominio DDD |
| [06-infraestrutura.md](architecture/06-infraestrutura.md) | Infraestrutura |
| [api1-component-diagram.md](architecture/api1-component-diagram.md) | Diagrama de componentes API 1 |

---

## 7. ADRs - Architectural Decision Records

| ADR | Titulo | Status |
|-----|--------|--------|
| [ADR-001](adr/ADR-001-arquitetura-hexagonal.md) | Arquitetura Hexagonal (Ports & Adapters) | Aceito |
| [ADR-002](adr/ADR-002-banco-dados-oracle.md) | Banco de Dados Oracle com DBLinks | Aceito |
| [ADR-003](adr/ADR-003-linguagem-python.md) | Python como Linguagem Principal | Aceito |
| [ADR-004](adr/ADR-004-framework-fastapi.md) | FastAPI como Framework HTTP | Aceito |
| [ADR-005](adr/ADR-005-estrategia-testes.md) | Estrategia de Testes (TDD) | Aceito |
| [ADR-006](adr/ADR-006-autenticacao-api-key.md) | Autenticacao via API Key | Aceito |
| [ADR-007](adr/ADR-007-padrao-resposta-aneel.md) | Padrao de Resposta ANEEL | Aceito |
| [ADR-008](adr/ADR-008-cache-strategy.md) | Estrategia de Cache | Aceito |
| [ADR-009](adr/ADR-009-logging-monitoring.md) | Logging e Monitoramento | Aceito |
| [ADR-010](adr/ADR-010-error-handling.md) | Tratamento de Erros | Aceito |

- [Indice ADRs](adr/README.md) | [Template](adr/TEMPLATE.md)

---

## 8. Guias de Desenvolvimento

### Padroes e Principios

| Documento | Descricao |
|-----------|-----------|
| [00-index.md](development/00-index.md) | Guia de leitura recomendado |
| [01-clean-architecture.md](development/01-clean-architecture.md) | Arquitetura Limpa |
| [02-solid-principles.md](development/02-solid-principles.md) | Principios SOLID |
| [03-domain-driven-design.md](development/03-domain-driven-design.md) | DDD |
| [04-tdd-test-driven-development.md](development/04-tdd-test-driven-development.md) | TDD |
| [05-clean-code.md](development/05-clean-code.md) | Clean Code |

### Guias Tecnicos

| Documento | Descricao |
|-----------|-----------|
| [oracle-database.md](development/oracle-database.md) | Conexao Oracle/SQLAlchemy |
| [email-service.md](development/email-service.md) | Integracao Mailgun |
| [BRANCHING-STRATEGY.md](development/BRANCHING-STRATEGY.md) | Estrategia de branches Git |

---

## 9. Database

| Documento | Descricao |
|-----------|-----------|
| [dblink-configuration.md](database/dblink-configuration.md) | Configuracao DBLink Oracle |

---

## 10. Testes

| Documento | Descricao |
|-----------|-----------|
| [api1-test-plan.md](testing/api1-test-plan.md) | Plano de testes API 1 |

---

## 11. Deployment e Operations

### Deployment

| Documento | Descricao |
|-----------|-----------|
| [deployment-guide.md](deployment/deployment-guide.md) | Guia de deploy |

### Operations

| Documento | Descricao |
|-----------|-----------|
| [api1-runbook.md](operations/api1-runbook.md) | Runbook API 1 |
| [api1-troubleshooting.md](operations/api1-troubleshooting.md) | Troubleshooting API 1 |
| [monitoring-metrics.md](operations/monitoring-metrics.md) | Metricas de monitoramento |

---

## 12. Relatorios

| Documento | Descricao |
|-----------|-----------|
| [RELATORIO_ATIVIDADES_12-12-2025.md](reports/RELATORIO_ATIVIDADES_12-12-2025.md) | Sessao de desenvolvimento |
| [RELATORIO_CONSISTENCIA_INTEGRACAO.md](reports/RELATORIO_CONSISTENCIA_INTEGRACAO.md) | Consistencia de integracao |
| [RELATORIO_COMPARATIVO_POWEROUTAGE_US.md](reports/RELATORIO_COMPARATIVO_POWEROUTAGE_US.md) | Comparativo PowerOutage.us |

---

## Recursos Externos

| Recurso | Descricao |
|---------|-----------|
| [api/](../api/) | Exemplos de codigo, OpenAPI specs |
| [backend/](../backend/) | Codigo fonte Python/FastAPI |
| [frontend/](../frontend/) | Codigo fonte Vue.js |
| [.claude/](../.claude/) | Configuracao Claude Code |

---

## Mapa de Roraima - Referencia Rapida

O estado de Roraima possui **15 municipios** com aproximadamente **150.000 UCs**:

| Regiao | Municipios |
|--------|------------|
| **Capital** | Boa Vista (1400100) - ~120.000 UCs |
| **Norte** | Amajari, Pacaraima, Uiramuta |
| **Sul** | Caracarai, Rorainopolis, Sao Joao da Baliza, Sao Luiz, Caroebe, Iracema |
| **Leste** | Bonfim, Normandia |
| **Central** | Alto Alegre, Mucajai, Canta |

**Detalhes completos:** [Visibilidade Integrada](tasks/VISIBILIDADE_INTEGRADA_PROJETO_RADAR.md#1-mapa-de-roraima-e-localidades)

---

**Documento atualizado em:** 2025-12-19
