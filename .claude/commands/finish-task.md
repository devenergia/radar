---
description: Finaliza uma task e cria commit/PR seguindo padroes RADAR
argument-hint: RAD-XXX
allowed-tools: Bash, Read, Write, Edit, Glob
---

# Finish Task - Finalizar Task

Finaliza uma task RADAR seguindo os passos 13-15 do workflow.

## Argumento

- `$ARGUMENTS` = Task ID no formato RAD-XXX

## Pre-Requisitos

Antes de finalizar, verificar:

1. [ ] Code review executado (`/review-task`)
2. [ ] Score >= 85/100
3. [ ] Todos os testes passando
4. [ ] Coverage >= 80%
5. [ ] ruff check sem erros
6. [ ] mypy sem erros

## Passo 13: Atualizar EXECUTION_STATUS.md

**Identificar projeto baseado no Task ID:**
```bash
# RAD-1XX (100-199) -> api-interrupcoes
# RAD-2XX (200-299) -> mapa-interrupcoes

TASK_NUM=$(echo "$ARGUMENTS" | grep -oP '\d+')
if [ "$TASK_NUM" -ge 100 ] && [ "$TASK_NUM" -lt 200 ]; then
    PROJECT="api-interrupcoes"
elif [ "$TASK_NUM" -ge 200 ] && [ "$TASK_NUM" -lt 300 ]; then
    PROJECT="mapa-interrupcoes"
fi
```

Editar `docs/tasks/$PROJECT/EXECUTION_STATUS.md`:

```markdown
| $ARGUMENTS | Titulo da Task | `[X]` CONCLUIDO | YYYY-MM-DD | - |
```

Atualizar:
- Status: CONCLUIDO
- Data de conclusao: Data atual

## Passo 14: Criar Commit

### Verificar Arquivos

```bash
git status
git diff --staged
```

### Formato do Commit

```bash
git add .
git commit -m "$(cat <<'EOF'
feat(api-interrupcoes): implementa $ARGUMENTS

- [Descricao das mudancas principais]
- Testes TDD implementados
- Coverage: XX%

[code-review-approved]
Task: $ARGUMENTS
Review Score: XX/100

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

### Tipos de Commit por Task

| Fase | Tipo | Exemplo |
|------|------|---------|
| Domain (RAD-100 a RAD-104) | feat | `feat(domain): implementa entity Interrupcao` |
| Infrastructure (RAD-105 a RAD-111) | feat | `feat(infra): configura conexao Oracle` |
| Interfaces (RAD-112 a RAD-118) | feat | `feat(api): adiciona endpoint interrupcoes` |
| Testes (RAD-119 a RAD-121) | test | `test(unit): adiciona testes CodigoIBGE` |
| Seguranca (RAD-122 a RAD-125) | feat | `feat(security): implementa rate limiting` |

## Passo 15: Push e Pull Request

### Push da Branch

```bash
git push -u origin feat/rad-xxx/descricao
```

### Criar Pull Request

```bash
gh pr create \
  --base main \
  --title "feat(api-interrupcoes): $ARGUMENTS - Titulo" \
  --body "$(cat <<'EOF'
## Summary
- Implementa $ARGUMENTS: [Titulo da Task]
- [Descricao das principais mudancas]

## Changes
- [Lista de mudancas]

## Test Plan
- [x] Testes unitarios passando
- [x] Coverage >= 80%
- [x] Code review >= 85/100

## Checklist
- [x] TDD seguido (testes primeiro)
- [x] Clean Architecture respeitada
- [x] SOLID principles aplicados
- [x] Type hints presentes
- [x] Conventional Commits

## Review Metrics
- Coverage: XX%
- Review Score: XX/100
- Critical Issues: 0

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Verificacoes Finais

```bash
# Verificar testes
pytest tests/ --tb=short -q

# Verificar linting
ruff check backend/

# Verificar types
mypy backend/

# Verificar status do git
git status
git log -1 --oneline
```

## Checklist Final

- [ ] EXECUTION_STATUS.md atualizado
- [ ] Commit criado com formato correto
- [ ] Push realizado
- [ ] PR criado (se aplicavel)
- [ ] Branch limpa

## Exemplo de Uso

```bash
/finish-task RAD-100
# Atualiza status para CONCLUIDO
# Cria commit com mensagem formatada
# Push da branch
# Cria PR com template
```

## Proxima Task

Apos finalizar, execute:
```bash
/next-task
# Busca a proxima task PENDENTE
```
