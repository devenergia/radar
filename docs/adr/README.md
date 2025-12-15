# Architecture Decision Records (ADR)

Este diretório contém os registros de decisões de arquitetura do Projeto RADAR.

## O que são ADRs?

ADRs são documentos curtos que capturam decisões arquiteturais importantes junto com seu contexto e consequências. Eles servem como um registro histórico do "porquê" das decisões tomadas.

## Lista de ADRs

| ADR | Título | Status | Data |
|-----|--------|--------|------|
| [ADR-001](./ADR-001-arquitetura-hexagonal.md) | Adoção de Arquitetura Hexagonal | Aceito | 2025-12-12 |
| [ADR-002](./ADR-002-banco-dados-oracle.md) | Banco de Dados Oracle com DBLinks | Aceito | 2025-12-12 |
| [ADR-003](./ADR-003-linguagem-python.md) | Python como Linguagem Principal | Aceito | 2025-12-15 |
| [ADR-004](./ADR-004-framework-fastapi.md) | FastAPI como Framework HTTP | Aceito | 2025-12-15 |
| [ADR-005](./ADR-005-estrategia-testes.md) | Estratégia de Testes (TDD) | Aceito | 2025-12-12 |
| [ADR-006](./ADR-006-autenticacao-api-key.md) | Autenticação via API Key | Aceito | 2025-12-12 |
| [ADR-007](./ADR-007-padrao-resposta-aneel.md) | Padrão de Resposta ANEEL | Aceito | 2025-12-12 |
| [ADR-008](./ADR-008-cache-strategy.md) | Estratégia de Cache | Aceito | 2025-12-12 |
| [ADR-009](./ADR-009-logging-monitoring.md) | Logging e Monitoramento | Aceito | 2025-12-12 |
| [ADR-010](./ADR-010-error-handling.md) | Tratamento de Erros | Aceito | 2025-12-12 |

## Template de ADR

Ao criar uma nova ADR, use o [template](./TEMPLATE.md).

## Status

- **Proposto**: A decisão está sendo discutida
- **Aceito**: A decisão foi aprovada e deve ser seguida
- **Depreciado**: A decisão foi substituída por outra
- **Substituído**: A decisão foi substituída (referenciar nova ADR)
