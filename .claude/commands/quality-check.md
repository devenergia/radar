---
description: Executa verificacao completa de qualidade do codigo
allowed-tools: Bash(pytest:*), Bash(ruff:*), Bash(mypy:*)
---

# Quality Check - Verificacao de Qualidade

Executa todas as verificacoes de qualidade do projeto RADAR.

## Verificacoes Executadas

### 1. Testes Unitarios

```bash
pytest tests/unit/ -v --tb=short
```

**Criterio**: Todos os testes devem passar.

### 2. Testes de Integracao

```bash
pytest tests/integration/ -v --tb=short -m integration
```

**Criterio**: Todos os testes devem passar.

### 3. Coverage

```bash
pytest tests/ --cov=backend --cov-report=term-missing --cov-fail-under=80
```

**Criterios**:
| Camada | Minimo | Ideal |
|--------|--------|-------|
| Domain | 90% | 95% |
| Infrastructure | 80% | 85% |
| Use Cases | 85% | 90% |
| API | 80% | 85% |

### 4. Linting (Ruff)

```bash
ruff check backend/
```

**Criterio**: Zero erros de linting.

### 5. Type Checking (MyPy)

```bash
mypy backend/ --strict
```

**Criterio**: Zero erros de tipo.

### 6. Verificacao de Arquitetura

```bash
# Domain nao importa de Infrastructure
grep -r "from.*infrastructure" backend/shared/domain/ && echo "VIOLACAO!" || echo "OK"

# Application nao importa de API
grep -r "from.*api" backend/shared/application/ && echo "VIOLACAO!" || echo "OK"
```

**Criterio**: Zero violacoes de Clean Architecture.

### 7. Verificacao de Seguranca

Checklist manual:
- [ ] API Key validada em endpoints
- [ ] Queries parametrizadas
- [ ] Validacao Pydantic
- [ ] Sem dados sensiveis em logs

## Formato do Resultado

```markdown
## Quality Check Report

### Status Geral: PASSED/FAILED

### Detalhes:

| Check | Status | Detalhes |
|-------|--------|----------|
| Unit Tests | PASS/FAIL | XX passed, XX failed |
| Integration Tests | PASS/FAIL | XX passed, XX failed |
| Coverage | PASS/FAIL | XX% (min: 80%) |
| Ruff | PASS/FAIL | XX issues |
| MyPy | PASS/FAIL | XX errors |
| Architecture | PASS/FAIL | XX violations |

### Issues Encontradas:
1. ...
2. ...

### Proximos Passos:
- [ ] Corrigir issues
- [ ] Executar /quality-check novamente
```

## Criterios de Aprovacao

Para aprovar o quality check:
- [ ] Todos os testes passando (unit + integration)
- [ ] Coverage >= 80%
- [ ] Zero erros de ruff
- [ ] Zero erros de mypy
- [ ] Zero violacoes de arquitetura

## Comandos Rapidos

```bash
# Check rapido (apenas testes unitarios)
pytest tests/unit/ -q

# Check completo
pytest tests/ --cov=backend && ruff check backend/ && mypy backend/

# Fix automatico de lint
ruff check backend/ --fix
```

## Exemplo de Uso

```bash
/quality-check
# Executa todas as verificacoes
# Retorna relatorio completo
```

## Integracao com Workflow

O quality-check deve ser executado:
1. Antes do code review (`/review-task`)
2. Antes de finalizar a task (`/finish-task`)
3. Antes de criar PR
