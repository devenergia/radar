---
name: test-runner
description: Executa testes automatizados (pytest) com geracao de coverage reports e output formatado para o Projeto RADAR
allowed-tools: Read, Bash, Grep, Glob
---

# Skill: test-runner

## Descricao

Executa testes automatizados usando pytest com geracao de coverage reports e output formatado para o Projeto RADAR.

## Funcionalidades

- Deteccao automatica de escopo (unit/integration/e2e)
- Filtragem por padrao (ex: `test_interrupcao*`)
- Geracao de coverage reports (HTML + terminal)
- Execucao paralela (pytest-xdist)
- Output formatado e legivel
- Deteccao de testes falhados com detalhes

## Input

```typescript
{
  scope: "unit" | "integration" | "e2e" | "all";
  pattern?: string;        // "test_interrupcao*", "test_ibge*"
  coverage?: boolean;      // true (default)
  parallel?: boolean;      // false (default)
  verbose?: boolean;       // true (default)
  failFast?: boolean;      // false (default) - para na primeira falha
  markers?: string;        // "unit", "integration", "e2e"
  path?: string;           // "backend/tests/unit/domain/" (opcional)
}
```

## Output

```typescript
{
  status: "success" | "failure" | "error";
  totalTests: number;      // 45
  passed: number;          // 42
  failed: number;          // 2
  skipped: number;         // 1
  errors: number;          // 0
  coverage?: {
    statements: number;    // 87.5
    branches: number;      // 82.3
    functions: number;     // 90.1
    lines: number;         // 87.5
  };
  duration: number;        // 12.5 (segundos)
  failedTests?: string[];  // ["test_ibge.py::test_invalid_code", ...]
  coverageReport?: string; // Relatorio textual
  htmlReportPath?: string; // "htmlcov/index.html"
  message: string;         // Mensagem descritiva
  error?: string;          // Se status = "error"
}
```

## Estrutura de Testes RADAR

```
backend/tests/
  unit/
    domain/
      entities/
        test_interrupcao.py
      value_objects/
        test_codigo_ibge.py
        test_tipo_interrupcao.py
      services/
        test_interrupcao_aggregator.py
    repositories/
      test_oracle_interrupcao_repository.py
      test_oracle_universo_repository.py
    use_cases/
      test_get_interrupcoes_ativas.py
    middleware/
      test_middleware.py
    dependencies/
      test_dependencies.py
  integration/
    test_oracle_connection.py
    test_cache_service.py
  e2e/
    test_api_interrupcoes.py
```

## Implementacao

### Passo 1: Detectar Ambiente

```bash
# Verificar se estamos no diretorio correto
if [ ! -d "backend/tests" ]; then
  echo "ERROR: Diretorio backend/tests nao encontrado"
  exit 1
fi

# Verificar pytest instalado
if ! command -v pytest &> /dev/null; then
  echo "ERROR: pytest nao encontrado. Execute: pip install pytest pytest-cov"
  exit 1
fi

echo "Ambiente verificado: backend/tests"
```

### Passo 2: Construir Comando pytest

```bash
# Base command
cmd="pytest"

# Scope mapping
case "$scope" in
  "unit")
    cmd="$cmd backend/tests/unit"
    ;;
  "integration")
    cmd="$cmd backend/tests/integration"
    ;;
  "e2e")
    cmd="$cmd backend/tests/e2e"
    ;;
  "all")
    cmd="$cmd backend/tests"
    ;;
esac

# Pattern
if [ -n "$pattern" ]; then
  cmd="$cmd -k $pattern"
fi

# Coverage
if [ "$coverage" == "true" ]; then
  cmd="$cmd --cov=backend --cov-report=html --cov-report=term-missing"
fi

# Verbose
if [ "$verbose" == "true" ]; then
  cmd="$cmd -v"
fi

# Parallel
if [ "$parallel" == "true" ]; then
  cmd="$cmd -n auto"
fi

# Fail fast
if [ "$failFast" == "true" ]; then
  cmd="$cmd -x"
fi

# Markers
if [ -n "$markers" ]; then
  cmd="$cmd -m $markers"
fi

# Formato de output
cmd="$cmd --tb=short --no-cov-on-fail"

echo "Comando pytest: $cmd"
```

### Passo 3: Executar Testes

```bash
# Executar comando
startTime=$(date +%s)
output=$(eval "$cmd" 2>&1)
exitCode=$?
endTime=$(date +%s)
duration=$((endTime - startTime))

echo "$output"
```

### Passo 4: Parsear Output

```bash
# Extrair metricas do output pytest
totalTests=$(echo "$output" | grep -oP '\d+(?= passed)' || echo "0")
passed=$(echo "$output" | grep -oP '\d+(?= passed)' || echo "0")
failed=$(echo "$output" | grep -oP '\d+(?= failed)' || echo "0")
skipped=$(echo "$output" | grep -oP '\d+(?= skipped)' || echo "0")
errors=$(echo "$output" | grep -oP '\d+(?= error)' || echo "0")

# Coverage (se habilitado)
if [ "$coverage" == "true" ]; then
  coverageLines=$(echo "$output" | grep "TOTAL" | awk '{print $NF}' | sed 's/%//')
  htmlReportPath="htmlcov/index.html"
fi

# Testes falhados
if [ "$failed" -gt 0 ]; then
  failedTests=$(echo "$output" | grep "FAILED" | awk '{print $1}')
fi
```

### Passo 5: Determinar Status

```bash
# Determinar status final
if [ $exitCode -eq 0 ]; then
  status="success"
  message="Todos os testes passaram! ($passed/$totalTests)"
elif [ "$failed" -gt 0 ]; then
  status="failure"
  message="$failed testes falharam de $totalTests"
else
  status="error"
  message="Erro ao executar testes"
fi
```

## Exemplos de Uso

### Exemplo 1: Rodar testes unitarios de domain

```bash
/test-runner --scope unit --path backend/tests/unit/domain --coverage
```

**Output:**
```json
{
  "status": "success",
  "totalTests": 24,
  "passed": 24,
  "failed": 0,
  "skipped": 0,
  "errors": 0,
  "coverage": {
    "lines": 92.5
  },
  "duration": 3.2,
  "htmlReportPath": "htmlcov/index.html",
  "message": "Todos os testes passaram! (24/24)"
}
```

### Exemplo 2: Rodar testes de um modulo especifico

```bash
/test-runner --scope unit --pattern "test_codigo_ibge*" --verbose
```

**Output:**
```json
{
  "status": "success",
  "totalTests": 8,
  "passed": 8,
  "failed": 0,
  "coverage": {
    "lines": 95.0
  },
  "duration": 1.5,
  "message": "Todos os testes passaram! (8/8)"
}
```

### Exemplo 3: Rodar todos os testes com fail-fast

```bash
/test-runner --scope all --failFast --coverage
```

**Output (com falhas):**
```json
{
  "status": "failure",
  "totalTests": 45,
  "passed": 42,
  "failed": 3,
  "coverage": {
    "lines": 85.0
  },
  "duration": 12.5,
  "failedTests": [
    "tests/unit/domain/test_interrupcao.py::test_invalid_ucs",
    "tests/integration/test_cache.py::test_cache_expiration"
  ],
  "message": "3 testes falharam de 45"
}
```

## Metas de Coverage RADAR

| Tipo | Minimo | Ideal |
|------|--------|-------|
| Domain (Entities, VOs) | 90% | 95% |
| Infrastructure | 80% | 85% |
| Use Cases | 85% | 90% |
| API/Routes | 80% | 85% |
| Global | 80% | 85% |

## Markers Pytest RADAR

```python
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: Testes unitarios (sem I/O externo)",
    "integration: Testes de integracao (com banco/cache)",
    "e2e: Testes end-to-end (API completa)",
    "slow: Testes lentos (> 1s)",
]
```

### Uso de Markers

```bash
# Apenas testes unitarios
/test-runner --scope all --markers "unit"

# Excluir testes lentos
/test-runner --scope all --markers "not slow"
```

## Integracao com tdd-development

```bash
# tdd-development chama test-runner automaticamente

# Red Phase (testes devem falhar)
/test-runner --scope unit --pattern "test_$taskId*"
# Expected: status=failure

# Green Phase (testes devem passar)
/test-runner --scope unit --pattern "test_$taskId*" --coverage
# Expected: status=success, coverage >= 80%
```

## Troubleshooting

### Erro: "pytest nao encontrado"
**Solucao:**
```bash
pip install pytest pytest-cov pytest-asyncio
```

### Erro: "Coverage abaixo do minimo"
**Solucao:**
```bash
# Ver arquivos com baixa coverage
pytest --cov=backend --cov-report=term-missing

# Adicionar testes para branches nao cobertas
```

### Testes falhando com AsyncIO
**Solucao:**
```python
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

## Performance

- **Tempo medio (unit - 50 testes)**: 3-5s
- **Tempo medio (integration - 20 testes)**: 8-12s
- **Tempo medio (all - 100 testes)**: 15-25s
- **Com parallel (-n auto)**: ~40% mais rapido

## Versao

- **Atual:** 1.0.0
- **Ultima atualizacao:** 2025-12-19
- **Projeto:** RADAR - Sistema de Monitoramento ANEEL
