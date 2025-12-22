---
description: Executa review completo de uma task com agentes especialistas
argument-hint: RAD-XXX
allowed-tools: Bash, Read, Glob, Grep
---

# Review Task - Review com Agentes Especialistas

Executa code review automatico com multiplos agentes especialistas.

## Argumento

- `$ARGUMENTS` = Task ID no formato RAD-XXX

## Processo de Review

### 1. Identificar Arquivos da Task

```bash
# Buscar arquivos modificados na branch atual
git diff main --name-only

# Ou buscar arquivos relacionados a task
grep -r "RAD-XXX" backend/ --include="*.py"
```

### 2. Executar Review por Categoria

O review avalia 7 categorias com pesos:

| Categoria | Peso | Threshold Critical |
|-----------|------|-------------------|
| Clean Architecture | 20% | < 50% |
| SOLID Principles | 15% | - |
| Type Safety | 15% | - |
| Security | 20% | < 50% |
| Performance | 10% | - |
| Testing | 15% | - |
| Documentation | 5% | - |

### 3. Checklist Clean Architecture (20%)

- [ ] Domain NAO importa de Infrastructure
- [ ] Application NAO importa de API
- [ ] Entidades sao puras (sem dependencias externas)
- [ ] Use Cases delegam para Domain Services
- [ ] Repositories usam Protocol (nao ABC)

```bash
# Verificar violacoes
grep -r "from.*infrastructure" backend/shared/domain/
grep -r "from.*api" backend/shared/application/
```

### 4. Checklist SOLID (15%)

- [ ] **SRP**: Classes tem uma unica responsabilidade
- [ ] **OCP**: Codigo aberto para extensao, fechado para modificacao
- [ ] **LSP**: Subtipos podem substituir seus tipos base
- [ ] **ISP**: Interfaces pequenas e especificas
- [ ] **DIP**: Dependencias injetadas via Protocol

### 5. Checklist Type Safety (15%)

- [ ] Type hints em 80%+ das funcoes
- [ ] Return types declarados
- [ ] mypy passa sem erros

```bash
mypy backend/ --strict
```

### 6. Checklist Security (20%)

- [ ] API Key validada em endpoints
- [ ] Queries parametrizadas (sem concatenacao)
- [ ] Validacao de entrada (Pydantic)
- [ ] Erros no formato ANEEL (sem stack traces)
- [ ] Dados sensiveis nao expostos em logs

### 7. Checklist Performance (10%)

- [ ] Queries otimizadas (sem N+1)
- [ ] Cache implementado quando necessario
- [ ] Conexoes pooled
- [ ] Async/await usado corretamente

### 8. Checklist Testing (15%)

- [ ] Testes escritos ANTES do codigo (TDD)
- [ ] Coverage >= 80%
- [ ] Testes unitarios para Value Objects
- [ ] Testes de integracao para Repositories
- [ ] Testes E2E para endpoints

```bash
pytest tests/ --cov=backend --cov-report=term-missing
```

### 9. Checklist Documentation (5%)

- [ ] Docstrings em metodos publicos
- [ ] Type hints documentam interfaces
- [ ] README atualizado se necessario

## Calculo do Score

```
Score Final = Σ (Categoria * Peso)

Exemplo:
- Clean Architecture: 90% * 0.20 = 18
- SOLID: 85% * 0.15 = 12.75
- Type Safety: 80% * 0.15 = 12
- Security: 95% * 0.20 = 19
- Performance: 75% * 0.10 = 7.5
- Testing: 90% * 0.15 = 13.5
- Documentation: 70% * 0.05 = 3.5

Score Final: 86.25/100
```

## Criterios de Aprovacao

- **Score >= 85**: APROVADO
- **Score 70-84**: APROVADO COM RESSALVAS (issues minor)
- **Score < 70**: REPROVADO (requer correcoes)
- **Critical Issue**: REPROVADO (Security < 50% ou Clean Architecture < 50%)

## Formato do Resultado

```markdown
## Review Task: RAD-XXX

### Score Final: XX/100

### Categorias:
| Categoria | Score | Status |
|-----------|-------|--------|
| Clean Architecture | XX% | OK/WARN/FAIL |
| SOLID | XX% | OK/WARN/FAIL |
| Type Safety | XX% | OK/WARN/FAIL |
| Security | XX% | OK/WARN/FAIL |
| Performance | XX% | OK/WARN/FAIL |
| Testing | XX% | OK/WARN/FAIL |
| Documentation | XX% | OK/WARN/FAIL |

### Issues Encontradas:
1. [SEVERITY] Descricao do issue
2. ...

### Recomendacoes:
1. ...
2. ...

### Veredicto: APROVADO/REPROVADO
```

## Exemplo de Uso

```bash
/review-task RAD-100
# Executa review completo da task RAD-100
# Retorna score e issues encontradas
```
