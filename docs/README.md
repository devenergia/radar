# Documentação RADAR - Sistema de Atendimento à ANEEL

> Índice completo da documentação do projeto RADAR (Roraima Energia - Sistema de APIs ANEEL)

## Estrutura da Documentação

```
docs/
├── design/          # Arquitetura e design do sistema
├── analysis/        # Análises e requisitos
├── api-specs/       # Especificações das APIs ANEEL
├── architecture/    # Documentação técnica de arquitetura
├── adr/             # Architectural Decision Records
├── development/     # Guias de desenvolvimento
├── reports/         # Relatórios de atividades
└── official/        # Documentos oficiais ANEEL (PDFs)
```

---

## Design e Arquitetura

Documentos de design de alto nível e arquitetura do sistema.

| Documento | Descrição |
|-----------|-----------|
| [Design Completo](design/DESIGN_ARQUITETURA_RADAR_RR.md) | Design e arquitetura completo (v2.0) - contexto, escopo, obrigações ANEEL |
| [Diagramas Mermaid](design/DIAGRAMAS_MERMAID_RADAR_RR.md) | Diagramas visuais de arquitetura e fluxos |
| [Integração Sistema Técnico](design/INTEGRACAO_SISTEMA_TECNICO_RADAR_RR.md) | Detalhes de integração com sistemas existentes |

---

## Análises e Requisitos

Documentos de análise de requisitos e mapeamento.

| Documento | Descrição |
|-----------|-----------|
| [Análise de Requisitos](analysis/ANALISE_REQUISITOS_RADAR_RR.md) | Análise detalhada dos requisitos ANEEL |
| [Requisitos Sistema Técnico](analysis/REQUISITOS_SISTEMA_TECNICO_RADAR.md) | Requisitos do sistema técnico |
| [Requisitos Sistema Comercial](analysis/REQUISITOS_SISTEMA_COMERCIAL_RADAR.md) | Requisitos do sistema comercial |
| [Mapeamento Equipes](analysis/MAPEAMENTO_EQUIPES_SISTEMAS_RADAR.md) | Mapeamento de equipes e sistemas |
| [Requisitos AJURI API1](analysis/REQUISITOS_AJURI_API1.md) | Requisitos AJURI para API 1 |
| [Requisitos Técnicos API1](analysis/REQUISITOS_SISTEMA_TECNICO_API1.md) | Requisitos técnicos para API 1 |

---

## Especificações das APIs ANEEL

Documentação técnica dos 4 endpoints obrigatórios.

### APIs Principais

| API | Documento de Especificação | Documentação Técnica |
|-----|---------------------------|---------------------|
| **API 1** - Interrupções Ativas | [Especificação](api-specs/API_01_QUANTITATIVO_INTERRUPCOES_ATIVAS.md) | [Doc Técnica](api-specs/01-interrupcoes.md) |
| **API 2** - Dados de Demanda | [Especificação](api-specs/API_02_DADOS_DEMANDA.md) | [Doc Técnica](api-specs/03-dados-demanda.md) |
| **API 3** - Demandas Diversas | [Especificação](api-specs/API_03_QUANTITATIVO_DEMANDAS_DIVERSAS.md) | [Doc Técnica](api-specs/02-demandas-diversas.md) |
| **API 4** - Tempo Real REN 1.137 | [Especificação](api-specs/API_04_TEMPO_REAL_REN_1137.md) | - |

### Segurança

| Documento | Descrição |
|-----------|-----------|
| [Guia de Segurança](api-specs/04-seguranca.md) | Autenticação, autorização e boas práticas |

---

## Arquitetura Técnica

Documentação técnica detalhada da arquitetura do sistema.

| Documento | Descrição |
|-----------|-----------|
| [Índice](architecture/README.md) | Índice da documentação de arquitetura |
| [Visão Geral](architecture/01-visao-geral.md) | Visão geral do sistema |
| [Arquitetura Hexagonal](architecture/02-arquitetura-hexagonal.md) | Detalhamento da arquitetura hexagonal |
| [Fluxo de Dados](architecture/03-fluxo-dados.md) | Fluxo de dados entre sistemas |
| [Diagramas de Sequência](architecture/04-diagramas-sequencia.md) | Diagramas de sequência das operações |
| [Modelo de Domínio](architecture/05-modelo-dominio.md) | Modelo de domínio DDD |
| [Infraestrutura](architecture/06-infraestrutura.md) | Infraestrutura e integrações |

---

## ADRs - Architectural Decision Records

Registro das decisões arquiteturais do projeto.

| ADR | Título | Status |
|-----|--------|--------|
| [ADR-001](adr/ADR-001-arquitetura-hexagonal.md) | Arquitetura Hexagonal (Ports & Adapters) | Aceito |
| [ADR-002](adr/ADR-002-banco-dados-oracle.md) | Banco de Dados Oracle com DBLinks | Aceito |
| [ADR-003](adr/ADR-003-linguagem-python.md) | Python como Linguagem Principal | Aceito |
| [ADR-004](adr/ADR-004-framework-fastapi.md) | FastAPI como Framework HTTP | Aceito |
| [ADR-005](adr/ADR-005-estrategia-testes.md) | Estratégia de Testes (TDD) | Aceito |
| [ADR-006](adr/ADR-006-autenticacao-api-key.md) | Autenticação via API Key | Aceito |
| [ADR-007](adr/ADR-007-padrao-resposta-aneel.md) | Padrão de Resposta ANEEL | Aceito |
| [ADR-008](adr/ADR-008-cache-strategy.md) | Estratégia de Cache | Aceito |
| [ADR-009](adr/ADR-009-logging-monitoring.md) | Logging e Monitoramento | Aceito |
| [ADR-010](adr/ADR-010-error-handling.md) | Tratamento de Erros | Aceito |

- [Índice ADRs](adr/README.md)
- [Template para novas ADRs](adr/TEMPLATE.md)

---

## Guias de Desenvolvimento

Guias de boas práticas e padrões de desenvolvimento.

### Padrões e Princípios

| Documento | Descrição |
|-----------|-----------|
| [Índice](development/00-index.md) | Guia de leitura recomendado |
| [Clean Architecture](development/01-clean-architecture.md) | Arquitetura limpa - estrutura em camadas |
| [Princípios SOLID](development/02-solid-principles.md) | Princípios SOLID com exemplos |
| [Domain-Driven Design](development/03-domain-driven-design.md) | DDD - Entidades, VOs, Aggregates |
| [TDD](development/04-tdd-test-driven-development.md) | Test-Driven Development - Red-Green-Refactor |
| [Clean Code](development/05-clean-code.md) | Clean Code - boas práticas |

### Guias Técnicos

| Documento | Descrição |
|-----------|-----------|
| [Oracle Database](development/oracle-database.md) | Guia de conexão Oracle/SQLAlchemy |
| [Email Service](development/email-service.md) | Guia de integração Mailgun |

### Recursos

| Arquivo | Descrição |
|---------|-----------|
| [tasks.json](development/tasks.json) | Tarefas com checklists TDD |

---

## Relatórios

Relatórios de atividades e análises.

| Documento | Descrição |
|-----------|-----------|
| [Relatório 12/12/2025](reports/RELATORIO_ATIVIDADES_12-12-2025.md) | Relatório da sessão de desenvolvimento |
| [Consistência Integração](reports/RELATORIO_CONSISTENCIA_INTEGRACAO.md) | Relatório de consistência |
| [Comparativo PowerOutage](reports/RELATORIO_COMPARATIVO_POWEROUTAGE_US.md) | Análise comparativa com PowerOutage.us |

---

## Documentos Oficiais ANEEL

Documentos regulatórios e oficiais.

| Documento | Descrição |
|-----------|-----------|
| [REN 1.137-2025.pdf](official/REN%201.137-2025.pdf) | Resolução Normativa ANEEL |
| [Ofício Circular 14/2025](official/Oficio_Circular_14-2025_SMA-ANEEL.pdf) | Ofício Circular SMA-ANEEL |
| [Apresentação Técnica](official/RADAR_Apresentação%20Técnica%20-%2030-7-2025.pdf) | Apresentação técnica do RADAR |

---

## Navegação Rápida

### Por Função

- **Desenvolvedor novo no projeto**: Comece pelo [README principal](../README.md), depois [Design Completo](design/DESIGN_ARQUITETURA_RADAR_RR.md) e [Guias de Desenvolvimento](development/00-index.md)
- **Implementar uma API**: Veja as [Especificações de API](api-specs/) e [Arquitetura Técnica](architecture/)
- **Entender decisões**: Consulte os [ADRs](adr/)
- **Integração com sistemas**: [Integração Sistema Técnico](design/INTEGRACAO_SISTEMA_TECNICO_RADAR_RR.md)

### Por Urgência/Prazo

1. **Dezembro/2025**: API 1 - Interrupções Ativas
2. **Abril/2025**: API 2 e API 3 - Dados de Demanda e Demandas Diversas
3. **Maio/2025**: API 4 - Tempo Real REN 1.137

---

## Recursos Externos

- [Pasta api/](../api/) - Exemplos de código, OpenAPI specs e requests HTTP
- [Backend](../backend/) - Código fonte do backend Python/FastAPI
- [Frontend](../frontend/) - Código fonte do frontend Vue.js
