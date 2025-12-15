---
description: Executa testes com diferentes opcoes
argument-hint: [tipo] - unit|integration|e2e|all|coverage
allowed-tools: Bash(pytest:*), Bash(python:*)
---

# Executar Testes

Execute os testes do projeto RADAR baseado no tipo especificado.

## Opcoes

- `unit` - Apenas testes unitarios (rapidos)
- `integration` - Apenas testes de integracao
- `e2e` - Apenas testes end-to-end
- `all` - Todos os testes
- `coverage` - Todos os testes com relatorio de cobertura

## Comandos por Tipo

### Testes Unitarios
```bash
pytest -m unit -v
```

### Testes de Integracao
```bash
pytest -m integration -v
```

### Testes E2E
```bash
pytest -m e2e -v
```

### Todos os Testes
```bash
pytest -v
```

### Com Cobertura
```bash
pytest --cov=backend --cov-report=html --cov-report=term-missing --cov-fail-under=80
```

## Opcoes Adicionais Uteis

```bash
# Verbose com output
pytest -v -s

# Parar no primeiro erro
pytest -x

# Ultimos falhos primeiro
pytest --lf

# Rodar testes em paralelo
pytest -n auto

# Filtrar por nome
pytest -k "test_deve_criar"

# Arquivo especifico
pytest backend/tests/unit/domain/value_objects/test_codigo_ibge.py
```

## Estrutura de Testes Esperada

```
backend/tests/
├── unit/                    # pytest -m unit
│   ├── domain/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   └── services/
│   └── application/
├── integration/             # pytest -m integration
│   ├── repositories/
│   └── use_cases/
├── e2e/                     # pytest -m e2e
│   └── api/
├── fixtures/
├── helpers/
└── conftest.py
```

## Verificacao de Qualidade Completa

Para validacao completa antes de commit/PR:

```bash
# 1. Lint
ruff check backend/

# 2. Format check
ruff format --check backend/

# 3. Type check
mypy backend/

# 4. Testes com cobertura
pytest --cov=backend --cov-fail-under=80
```

## Interpretando Resultados

### Cobertura Minima
- **80%** de cobertura de linhas (obrigatorio)
- **80%** de cobertura de branches (recomendado)

### Metricas de Qualidade
```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
backend/shared/domain/entities          100     10    90%
backend/shared/domain/value_objects      80      5    94%
backend/apps/api/application            150     20    87%
-----------------------------------------------------------
TOTAL                                   330     35    89%
```
