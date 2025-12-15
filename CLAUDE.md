# Projeto RADAR - Instrucoes para Claude Code

## Visao Geral

Este e o Projeto RADAR - Sistema de monitoramento de indicadores do setor eletrico para a ANEEL.
Stack: Python 3.11+, FastAPI, SQLAlchemy, oracledb, Pydantic, pytest.

## Regras Fundamentais

### Arquitetura
- **SEMPRE** siga Clean Architecture com camadas: domain > application > infrastructure > interfaces
- **NUNCA** importe de camadas externas para internas (domain nao importa de infrastructure)
- Use Dependency Injection via FastAPI `Depends()`

### Padroes de Codigo
- Use `Protocol` para interfaces (nao ABC)
- Use `@dataclass(frozen=True)` para Value Objects
- Use Result Pattern para operacoes que podem falhar
- Funcoes pequenas (< 20 linhas)
- Nomes em portugues para termos de dominio (Interrupcao, Demanda, CodigoIBGE)

### Testes (TDD)
- **SEMPRE** escreva o teste ANTES do codigo de producao
- Cobertura minima: 80%
- Use pytest com markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`

### Commits
- Siga Conventional Commits: `tipo(escopo): descricao`
- Tipos: feat, fix, docs, style, refactor, test, chore

## Estrutura do Projeto

```
backend/
├── apps/
│   ├── api_interrupcoes/    # API 1 - Interrupcoes
│   ├── api_demanda/         # API 2 - Demanda
│   ├── api_demandas_diversas/ # API 3 - Demandas Diversas
│   └── api_tempo_real/      # API 4 - Tempo Real
├── shared/
│   ├── domain/              # Entidades, Value Objects, Repositories (Protocol)
│   ├── application/         # Use Cases
│   └── infrastructure/      # Implementacoes concretas
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

## Comandos Uteis

```bash
# Testes
pytest                    # Todos os testes
pytest -m unit           # Apenas unitarios
pytest --cov             # Com cobertura

# Qualidade
ruff check backend/      # Lint
ruff format backend/     # Format
mypy backend/            # Type check
```

## Documentacao

- @docs/development/01-clean-architecture.md
- @docs/development/02-solid-principles.md
- @docs/development/03-domain-driven-design.md
- @docs/development/04-tdd-test-driven-development.md
- @docs/development/05-clean-code.md

## Regras Modulares

Consulte `.claude/rules/` para regras especificas por contexto.
