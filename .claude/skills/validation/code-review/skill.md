---
name: code-review
description: Executa code review automatico com validacao de Clean Architecture, SOLID, Type Safety, Security, Performance, Testing e Documentation para o Projeto RADAR
allowed-tools: Read, Grep, Glob, Bash, TodoWrite
---

# Skill: code-review

## Descricao

Executa code review automatico com 7 categorias de validacao, calculando score total e determinando se o codigo esta aprovado para commit no Projeto RADAR.

**Esta skill e critica para o sistema de orquestracao** - integra-se com `tdd-development` para garantir que apenas codigo de qualidade seja commitado.

## Workflow de Code Review

```
1. Ler arquivos modificados (git diff --staged ou filesChanged)
   |
2. Para cada categoria:
   - Clean Architecture (20%)
   - SOLID Principles (15%)
   - Type Safety (15%)
   - Security (20%)
   - Performance (10%)
   - Testing (15%)
   - Documentation (5%)
   |
3. Calcular score total (media ponderada)
   |
4. Identificar issues criticos
   |
5. Determinar aprovacao: (score >= minScore) && (0 critical issues)
   |
6. Retornar JSON com metricas completas
```

## Input

```typescript
{
  taskId: string;              // "RAD-100" (obrigatorio)
  filesChanged?: string[];     // ["backend/shared/domain/entities/interrupcao.py", ...]
  minScore?: number;           // 85 (default)
  verbose?: boolean;           // false (default)
  categories?: string[];       // ["clean_architecture", ...] ou todas
}
```

## Output

```typescript
{
  status: "success" | "failure" | "error";
  taskId: string;
  score: number;               // 0-100
  approved: boolean;           // true se >= minScore e sem critical issues
  categories: [{
    name: string;
    score: number;             // 0-100
    weight: number;            // Peso na media (%)
    status: "pass" | "fail";
    issues: string[];
    recommendations: string[];
  }];
  criticalIssues: string[];
  warnings: string[];
  filesReviewed: string[];
  summary: string;
  message: string;
  error?: string;
}
```

## Categorias de Validacao

### 1. Clean Architecture (20%)

**Validacoes:**
- Domain layer nao importa de Infrastructure
- Domain layer nao importa FastAPI/SQLAlchemy
- Application layer depende apenas de Domain
- API layer e thin (delegacao para Use Cases)

**Penalidades:**
- -20: Domain importa Infrastructure
- -15: Domain importa FastAPI
- -15: Application importa API
- -10: Logica de negocio em rotas

### 2. SOLID Principles (15%)

**Validacoes:**
- SRP: Classes com <= 10 metodos
- DIP: Uso de Protocol (nao ABC)
- ISP: Interfaces pequenas (< 10 metodos)
- Dependency Injection via Depends()

**Penalidades:**
- -10: Classe com > 10 metodos (SRP)
- -15: Dependencia concreta em __init__ (DIP)
- -10: Interface com > 10 metodos (ISP)

### 3. Type Safety (15%)

**Validacoes:**
- Type hints em 80%+ das funcoes
- Uso de Optional[] para nullables
- Evitar Any

**Penalidades:**
- -20: Type coverage < 80%
- -10: None sem Optional
- -5: Uso de Any

### 4. Security (20%)

**Validacoes CRITICAS:**
- SQL Injection (string concatenation)
- Hardcoded secrets
- Eval/exec usage
- Input validation (Pydantic)

**Penalidades:**
- -30: CRITICAL - SQL Injection
- -25: CRITICAL - Hardcoded secret
- -20: CRITICAL - Eval/exec
- -15: Falta de validacao de entrada

### 5. Performance (10%)

**Validacoes:**
- N+1 queries (loop com query)
- Indices em modelos
- Unbounded queries (.all() sem .limit())

**Penalidades:**
- -20: N+1 query potencial
- -10: Modelo sem indices
- -10: Query sem limit

### 6. Testing (15%)

**Validacoes:**
- Arquivos de teste para implementacoes
- Assertions nos testes
- Docstrings nos testes

**Penalidades:**
- -30: Implementacao sem testes
- -20: Testes sem assertions
- -10: Testes sem docstrings

### 7. Documentation (5%)

**Validacoes:**
- Module-level docstrings
- Class docstrings
- Method docstrings (70%+)

**Penalidades:**
- -15: Modulo sem docstring
- -10: Classe sem docstring
- -15: < 70% metodos documentados

## Thresholds

| Categoria | Peso | Critical Threshold |
|-----------|------|-------------------|
| Clean Architecture | 20% | < 50% |
| SOLID Principles | 15% | - |
| Type Safety | 15% | - |
| Security | 20% | < 50% |
| Performance | 10% | - |
| Testing | 15% | - |
| Documentation | 5% | - |

**Regra de Aprovacao:**
- Score total >= 85
- Zero critical issues (Security < 50% ou Clean Architecture < 50%)

## Checklist Especifico RADAR

### Clean Architecture RADAR
```
backend/
  shared/
    domain/         <- NAO pode importar de infrastructure
      entities/
      value_objects/
      services/
    infrastructure/ <- Implementa interfaces do domain
      database/
      cache/
  apps/
    api_interrupcoes/
      routes.py     <- Thin, delega para use_cases
      use_cases/    <- Orquestra repositories e services
      repositories/ <- Implementa protocols
```

### Padrao Protocol (DIP)
```python
# BOM - Protocol no domain
from typing import Protocol

class InterrupcaoRepository(Protocol):
    async def buscar_ativas(self) -> list[Interrupcao]: ...

# RUIM - ABC
from abc import ABC, abstractmethod

class InterrupcaoRepository(ABC):
    @abstractmethod
    async def buscar_ativas(self) -> list[Interrupcao]: ...
```

### Value Objects Imutaveis
```python
# BOM - frozen dataclass
@dataclass(frozen=True)
class CodigoIBGE:
    valor: str

# RUIM - dataclass mutavel
@dataclass
class CodigoIBGE:
    valor: str
```

## Exemplos de Uso

### Exemplo 1: Review com Aprovacao

```bash
/code-review RAD-100 --minScore 85
```

**Output:**
```json
{
  "status": "success",
  "taskId": "RAD-100",
  "score": 92,
  "approved": true,
  "categories": [
    {"name": "clean_architecture", "score": 95, "status": "pass"},
    {"name": "solid", "score": 90, "status": "pass"},
    {"name": "type_safety", "score": 88, "status": "pass"},
    {"name": "security", "score": 100, "status": "pass"},
    {"name": "performance", "score": 85, "status": "pass"},
    {"name": "testing", "score": 90, "status": "pass"},
    {"name": "documentation", "score": 80, "status": "pass"}
  ],
  "criticalIssues": [],
  "summary": "Code review APPROVED: 92/100 (min: 85)"
}
```

### Exemplo 2: Review com Reprovacao

```bash
/code-review RAD-105 --minScore 85
```

**Output:**
```json
{
  "status": "failure",
  "taskId": "RAD-105",
  "score": 68,
  "approved": false,
  "categories": [
    {"name": "security", "score": 40, "status": "fail", "issues": [
      "CRITICAL: Hardcoded password in config.py"
    ]}
  ],
  "criticalIssues": [
    "CRITICAL: Security score below 50% - must fix before commit"
  ],
  "summary": "Code review FAILED: Critical issues detected (score: 68)"
}
```

## Integracao com tdd-development

Este skill e invocado automaticamente por `tdd-development` antes de commitar:

```bash
# No tdd-development/skill.md, Passo 7:
reviewResult=$(claude-skill code-review \
  --taskId "$taskId" \
  --minScore 85)

reviewApproved=$(echo "$reviewResult" | jq -r '.approved')

if [ "$reviewApproved" != "true" ]; then
  echo "ERROR: Code review failed - blocking commit"
  exit 1
fi
```

## Performance

- **Tempo medio:** 5-10 segundos para 5-10 arquivos
- **Dependencias:** git, jq, grep

## Versao

- **Atual:** 1.0.0
- **Ultima atualizacao:** 2025-12-19
- **Projeto:** RADAR - Sistema de Monitoramento ANEEL
