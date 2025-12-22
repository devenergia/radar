---
name: tdd-development
description: Orquestra workflow TDD completo com selecao automatica de subagentes especializados para desenvolvimento das tasks RAD-XXX
allowed-tools: Read, Write, Edit, Bash, Task, Grep, Glob, TodoWrite
---

# Skill: tdd-development

## Descricao

Orquestra o workflow completo de desenvolvimento TDD (Test-Driven Development) para o Projeto RADAR, com selecao automatica de subagentes especializados.

**Esta e a skill MAIS IMPORTANTE do sistema** - ela integra todas as outras skills e automatiza o ciclo completo de desenvolvimento.

## Workflow TDD

```
1. Criar branch (se autoBranch=true)
   |
2. Selecionar subagente correto
   |
3. Desenvolver testes PRIMEIRO (se type=test ou both)
   |
4. Rodar testes (test-runner) - RED phase
   |
5. Desenvolver implementacao (se type=implementation ou both)
   |
6. Rodar testes novamente (test-runner) - GREEN phase
   |
7. Validar coverage >= minCoverage
   |
8. Code Review Automatico (code-review skill)
   |
9. Validar reviewScore >= minReviewScore
   |
10. Commitar com flag [code-review-approved]
   |
11. Retornar metricas completas
```

## Input

```typescript
{
  taskId: string;              // "RAD-100" (obrigatorio)
  type: "test" | "implementation" | "both";  // Tipo de desenvolvimento
  autoCommit?: boolean;        // true (default) - commitar se testes passarem
  autoBranch?: boolean;        // false (default) - criar branch automaticamente
  minCoverage?: number;        // 80 (default) - coverage minimo exigido
  dryRun?: boolean;            // false (default) - simular sem mudancas
  taskDescription?: string;    // Contexto adicional para subagente
}
```

## Output

```typescript
{
  status: "success" | "failure" | "error" | "partial";
  taskId: string;
  filesModified: string[];     // Arquivos criados/modificados
  testsRun: {
    total: number;
    passed: number;
    failed: number;
    coverage: number;
  };
  commitHash?: string;         // Se autoCommit=true
  branchName?: string;         // Se autoBranch=true
  subagentUsed: string;        // Nome do subagente usado
  duration: number;            // Tempo total em segundos
  steps: [{
    step: string;              // Nome do passo
    status: string;            // "success" | "failure"
    duration: number;          // Tempo do passo
    output: string;            // Output do passo
  }];
  message: string;
  error?: string;
}
```

## Implementacao

### Passo 1: Validar Input

```bash
# Validar taskId
if [[ ! $taskId =~ ^RAD-[0-9]{3}$ ]]; then
  echo "ERROR: taskId invalido. Use RAD-XXX (ex: RAD-100)"
  exit 1
fi

# Validar type
if [[ ! "$type" =~ ^(test|implementation|both)$ ]]; then
  echo "ERROR: type deve ser 'test', 'implementation' ou 'both'"
  exit 1
fi

# Validar minCoverage
if [ "$minCoverage" -lt 0 ] || [ "$minCoverage" -gt 100 ]; then
  echo "ERROR: minCoverage deve estar entre 0 e 100"
  exit 1
fi
```

### Passo 2: Selecionar Subagente

```bash
# Ler descricao da task
taskDescription=$(cat docs/tasks/api-interrupcoes/$taskId.md | head -n 30)

echo "Selecionando subagente para $taskId"
echo "Descricao: $taskDescription"

# Logica de selecao baseada na Fase da task
subagent=""

# Keywords para backend-architect (Domain, Infrastructure)
if echo "$taskDescription" | grep -qiE "entity|value object|repository|use case|oracle"; then
  subagent="backend-architect"

# Keywords para test-engineer (Testes)
elif echo "$taskDescription" | grep -qiE "test|tdd|coverage|pytest|unitario"; then
  subagent="test-engineer"

# Keywords para security-auditor (Seguranca)
elif echo "$taskDescription" | grep -qiE "security|auth|api.key|rate.limit|logging"; then
  subagent="security-auditor"

# Keywords para database-optimizer (Oracle/DBLink)
elif echo "$taskDescription" | grep -qiE "migration|dblink|oracle|query|sql"; then
  subagent="database-optimizer"

# Default: backend-architect
else
  subagent="backend-architect"
fi

echo "Subagente selecionado: $subagent"
```

### Passo 3: Desenvolver Testes (Red Phase)

```bash
if [[ "$type" == "test" || "$type" == "both" ]]; then
  echo "Passo 3: Desenvolvendo testes com $subagent"

  testPrompt="Desenvolva testes para a task $taskId seguindo TDD.

Descricao da task:
$taskDescription

Requisitos:
- Usar pytest com markers: @pytest.mark.unit, @pytest.mark.integration
- Coverage minimo: $minCoverage%
- Seguir padroes AAA (Arrange, Act, Assert)
- Testar casos de sucesso e falha
- Adicionar docstrings em todos os testes

Arquivos esperados:
- tests/unit/[modulo]/test_[funcionalidade].py
- tests/integration/[modulo]/test_[funcionalidade].py

Nao implementar a funcionalidade ainda, apenas os testes.
"

  # Invocar subagente via Task tool
  if [ "$dryRun" == "false" ]; then
    echo "Invocando subagente: $subagent"
    # Resultado esperado: arquivos de teste criados
  fi

  echo "Testes desenvolvidos"
fi
```

### Passo 4: Rodar Testes (Red Phase)

```bash
if [[ "$type" == "test" || "$type" == "both" ]]; then
  echo "Passo 4: Executando testes (esperado: falhar)"

  # Executar pytest
  pytest tests/unit -v --tb=short

  # No TDD, testes DEVEM falhar inicialmente
  if [[ "$testStatus" == "success" ]]; then
    echo "WARNING: Testes passaram sem implementacao (possivel falso positivo)"
  fi
fi
```

### Passo 5: Desenvolver Implementacao (Green Phase)

```bash
if [[ "$type" == "implementation" || "$type" == "both" ]]; then
  echo "Passo 5: Desenvolvendo implementacao com $subagent"

  implPrompt="Implemente a funcionalidade para a task $taskId.

Descricao da task:
$taskDescription

Requisitos:
- Fazer TODOS os testes passarem
- Seguir Clean Architecture (camadas bem definidas)
- Aplicar SOLID principles
- Usar Protocol para interfaces (nao ABC)
- Use @dataclass(frozen=True) para Value Objects
- Adicionar docstrings em todos os metodos
- Type hints completos

Coverage esperado: >= $minCoverage%
"

  # Invocar subagente via Task tool
  if [ "$dryRun" == "false" ]; then
    echo "Invocando subagente: $subagent"
    # Resultado esperado: arquivos de implementacao criados
  fi

  echo "Implementacao desenvolvida"
fi
```

### Passo 6: Rodar Testes (Green Phase)

```bash
if [[ "$type" == "implementation" || "$type" == "both" ]]; then
  echo "Passo 6: Executando testes (esperado: passar)"

  # Executar pytest com coverage
  pytest tests/ -v --cov=backend --cov-report=term-missing

  # Validar se testes passaram
  if [ "$testStatus" != "success" ]; then
    echo "ERROR: Testes falharam apos implementacao"
    exit 1
  fi

  # Validar coverage minimo
  if (( $(echo "$testCoverage < $minCoverage" | bc -l) )); then
    echo "ERROR: Coverage abaixo do minimo! Atual: $testCoverage%, Minimo: $minCoverage%"
    exit 1
  fi

  echo "Testes passando com coverage adequado ($testCoverage%)"
fi
```

### Passo 7: Code Review Automatico

```bash
if [ "$autoCommit" == "true" ] && [ "$testStatus" == "success" ] && [ "$dryRun" == "false" ]; then
  echo "Passo 7: Executando code review automatico"

  # Chamar code-review skill
  # Score minimo: 85/100
  # Sem critical issues

  reviewApproved=$(echo "$reviewResult" | jq -r '.approved')
  reviewScore=$(echo "$reviewResult" | jq -r '.score')

  echo "Review Score: $reviewScore/100"

  # Bloquear commit se reprovado
  if [ "$reviewApproved" != "true" ]; then
    echo "ERROR: Code review REPROVADO (score: $reviewScore/100)"
    exit 1
  fi

  echo "Code review APROVADO: $reviewScore/100"
fi
```

### Passo 8: Commitar

```bash
if [ "$autoCommit" == "true" ] && [ "$testStatus" == "success" ] && [ "$reviewApproved" == "true" ]; then
  echo "Passo 8: Criando commit"

  # Determinar tipo de commit baseado em type
  if [ "$type" == "test" ]; then
    commitType="test"
    commitMessage="adiciona testes para $taskId"
  elif [ "$type" == "implementation" ]; then
    commitType="feat"
    commitMessage="implementa $taskId"
  else
    commitType="feat"
    commitMessage="implementa $taskId com testes (TDD)"
  fi

  # Commit com flag [code-review-approved]
  git add .
  git commit -m "$commitType(api-interrupcoes): $commitMessage

[code-review-approved]
Score: $reviewScore/100
Coverage: $testCoverage%
Task: $taskId

Generated with Claude Code"

  echo "Commit criado"
fi
```

## Mapeamento de Subagentes para RADAR

### Por Fase da Task

| Fase | Tasks | Subagente | Foco |
|------|-------|-----------|------|
| Domain Layer | RAD-100 a RAD-104 | backend-architect | Entities, VOs, Domain Services |
| Infrastructure | RAD-105 a RAD-111 | database-optimizer, backend-architect | Oracle, Cache, Repositories |
| Interfaces | RAD-112 a RAD-118 | backend-architect | FastAPI, Routes, Schemas |
| Testes | RAD-119 a RAD-121 | test-engineer | Pytest, Coverage |
| Seguranca | RAD-122 a RAD-125 | security-auditor | Auth, Rate Limit, Logs |

### Keywords por Subagente

| Keywords | Subagente | Uso |
|----------|-----------|-----|
| entity, value object, domain | `backend-architect` | Camada de dominio |
| repository, oracle, dblink | `database-optimizer` | Acesso a dados |
| use case, service, aggregator | `backend-architect` | Logica de negocio |
| fastapi, route, endpoint, schema | `backend-architect` | API HTTP |
| test, pytest, coverage | `test-engineer` | Testes automatizados |
| security, auth, rate limit, log | `security-auditor` | Seguranca |

## Exemplos de Uso

### Exemplo 1: TDD Completo

```bash
# Desenvolve teste + implementacao + commit
/tdd-development RAD-100 --type both --autoCommit
```

### Exemplo 2: Apenas Testes (Red Phase)

```bash
# Desenvolve apenas testes (devem falhar)
/tdd-development RAD-101 --type test
```

### Exemplo 3: Apenas Implementacao (Green Phase)

```bash
# Implementa para testes ja existentes
/tdd-development RAD-101 --type implementation --autoCommit
```

## Integracao com Outras Skills

### Skills Chamadas

1. **test-runner** (2x no TDD completo)
   - Red phase: testes devem falhar
   - Green phase: testes devem passar

2. **code-review** (antes do commit)
   - Score minimo: 85/100
   - Zero critical issues

3. **commit-formatter** (se review aprovado)
   - Formato Conventional Commits
   - Flag [code-review-approved]

## Performance

- **Tempo medio (test-only)**: 15-20s
- **Tempo medio (impl-only)**: 25-35s
- **Tempo medio (TDD completo)**: 50-65s (incluindo code review)

## Versao

- **Atual**: 1.0.0
- **Ultima atualizacao**: 2025-12-19
- **Projeto**: RADAR - Sistema de Monitoramento ANEEL
