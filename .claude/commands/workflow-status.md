---
description: Mostra o status atual do workflow de desenvolvimento
allowed-tools: Bash, Read, Glob
---

# Workflow Status - Status do Workflow

Mostra o status atual do workflow de desenvolvimento RADAR.

## Informacoes Exibidas

### 1. Task Atual

```bash
# Verificar branch atual
git branch --show-current

# Extrair task ID da branch
# feat/rad-100/entity-interrupcao -> RAD-100
```

### 2. Status do EXECUTION_STATUS

```bash
cat docs/tasks/api-interrupcoes/EXECUTION_STATUS.md
```

Mostrar:
- Tasks CONCLUIDAS
- Task EM_ANDAMENTO (se houver)
- Proximas tasks PENDENTES

### 3. Progresso do Projeto

```
Fase 1 - Domain:        [X] RAD-100  [ ] RAD-101  [ ] RAD-102  [ ] RAD-103  [ ] RAD-104
Fase 2 - Infra:         [ ] RAD-105  [ ] RAD-106  [ ] RAD-107  [ ] RAD-108  [ ] RAD-109  [ ] RAD-110  [ ] RAD-111
Fase 3 - Interfaces:    [ ] RAD-112  [ ] RAD-113  [ ] RAD-114  [ ] RAD-115  [ ] RAD-116  [ ] RAD-117  [ ] RAD-118
Fase 4 - Testes:        [ ] RAD-119  [ ] RAD-120  [ ] RAD-121
Fase 5 - Seguranca:     [ ] RAD-122  [ ] RAD-123  [ ] RAD-124  [ ] RAD-125
```

### 4. Estado do Git

```bash
# Status do repositorio
git status --short

# Arquivos modificados
git diff --stat

# Ultimo commit
git log -1 --oneline
```

### 5. Metricas de Qualidade

```bash
# Coverage atual
pytest tests/ --cov=backend --cov-report=term 2>/dev/null | tail -5

# Erros de lint
ruff check backend/ 2>&1 | tail -3

# Erros de tipo
mypy backend/ 2>&1 | tail -3
```

## Formato de Saida

```markdown
## Workflow Status - Projeto RADAR

### Task Atual
- **Task ID**: RAD-100
- **Branch**: feat/rad-100/entity-interrupcao
- **Status**: EM_ANDAMENTO
- **Iniciada em**: 2025-12-19

### Passo Atual do Workflow
- [x] Passo 1: Identificar Task
- [x] Passo 2: Ler Especificacao
- [x] Passo 3: Selecionar Subagente
- [x] Passo 4: Criar Branch
- [x] Passo 5: Escrever Testes (RED)
- [ ] Passo 6: Implementar Codigo (GREEN)
- [ ] Passo 7: Refatorar
- [ ] Passo 8: Verificar Coverage
- [ ] Passo 9: Code Review
- [ ] Passo 10: Validacao Seguranca
- [ ] Passo 11: Validacao Arquitetura
- [ ] Passo 12: Suite Completa
- [ ] Passo 13: Atualizar Status
- [ ] Passo 14: Criar Commit
- [ ] Passo 15: Push/PR

### Progresso Geral
- **Total Tasks**: 26
- **Concluidas**: X
- **Em Andamento**: 1
- **Pendentes**: Y

### Git Status
- Arquivos modificados: X
- Arquivos staged: Y
- Branch: feat/rad-100/entity-interrupcao
- Commits a frente de main: Z

### Metricas
- Coverage: XX%
- Lint errors: X
- Type errors: Y
```

## Exemplo de Uso

```bash
/workflow-status
# Mostra status completo do workflow atual
```

## Comandos Relacionados

| Comando | Descricao |
|---------|-----------|
| `/next-task` | Busca proxima task |
| `/start-task RAD-XXX` | Inicia task especifica |
| `/review-task RAD-XXX` | Executa review |
| `/finish-task RAD-XXX` | Finaliza task |
| `/quality-check` | Verifica qualidade |
