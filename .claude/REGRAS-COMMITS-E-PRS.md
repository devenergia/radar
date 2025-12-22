# Regras de Commits e Pull Requests - Projeto RADAR

## Visao Geral

Este documento define as regras obrigatorias para commits e PRs no Projeto RADAR.
Seguimos Conventional Commits e templates padronizados para garantir rastreabilidade.

---

## Conventional Commits

### Formato

```
<tipo>(<escopo>): <descricao curta>

<corpo opcional>

<rodape>
```

### Tipos Permitidos

| Tipo | Uso | Exemplo |
|------|-----|---------|
| `feat` | Nova funcionalidade | `feat(domain): implementa entity Interrupcao` |
| `fix` | Correcao de bug | `fix(cache): corrige TTL do cache` |
| `docs` | Documentacao | `docs(readme): atualiza instrucoes de instalacao` |
| `style` | Formatacao (sem mudanca de codigo) | `style(api): formata imports` |
| `refactor` | Refatoracao | `refactor(domain): extrai validacoes` |
| `test` | Testes | `test(unit): adiciona testes CodigoIBGE` |
| `chore` | Manutencao | `chore(deps): atualiza dependencias` |
| `perf` | Performance | `perf(query): otimiza busca de interrupcoes` |

### Escopos Comuns

| Escopo | Descricao |
|--------|-----------|
| `api-interrupcoes` | API 1 - Interrupcoes |
| `domain` | Camada de dominio |
| `infra` | Infraestrutura |
| `tests` | Testes |
| `config` | Configuracoes |
| `deps` | Dependencias |
| `cache` | Sistema de cache |
| `security` | Seguranca |

### Regras da Descricao

1. Comece com letra minuscula
2. Nao termine com ponto
3. Use imperativo ("adiciona", nao "adicionado")
4. Maximo 72 caracteres
5. Seja especifico

```bash
# BOM
feat(domain): implementa value object CodigoIBGE

# RUIM
feat: coisas novas
feat(domain): Implementei o CodigoIBGE.
```

---

## Template de Commit

### Commit Simples

```bash
git commit -m "feat(domain): implementa entity Interrupcao"
```

### Commit com Corpo

```bash
git commit -m "$(cat <<'EOF'
feat(api-interrupcoes): implementa endpoint interrupcoes ativas

- Adiciona rota GET /quantitativointerrupcoesativas
- Implementa validacao de API Key
- Formato de resposta padrao ANEEL

Task: RAD-115
Coverage: 85%

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

### Commit de Task RADAR

Template obrigatorio para tasks RAD-XXX:

```bash
git commit -m "$(cat <<'EOF'
feat(api-interrupcoes): implementa RAD-XXX

- [Mudanca principal 1]
- [Mudanca principal 2]
- Testes TDD implementados
- Coverage: XX%

[code-review-approved]
Task: RAD-XXX
Review Score: XX/100

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Branches

### Nomenclatura

Formato: `{tipo}/{task-id}/{descricao-kebab-case}`

```bash
# Exemplos
feat/rad-100/entity-interrupcao
feat/rad-105/oracle-connection
feat/rad-115/endpoint-interrupcoes
fix/rad-120/cache-ttl
test/rad-119/unit-tests
```

### Tipos de Branch

| Tipo | Uso |
|------|-----|
| `feat` ou `feature` | Nova funcionalidade |
| `fix` | Correcao de bug |
| `test` | Adicao de testes |
| `refactor` | Refatoracao |
| `docs` | Documentacao |
| `hotfix` | Correcao urgente em producao |

### Comandos

```bash
# Criar branch
git checkout main
git pull origin main
git checkout -b feat/rad-100/entity-interrupcao

# Push com upstream
git push -u origin feat/rad-100/entity-interrupcao
```

---

## Pull Requests

### Template de PR

```markdown
## Summary
- Implementa RAD-XXX: [Titulo da Task]
- [Descricao das principais mudancas]

## Changes
- [Lista detalhada de mudancas]

## Task Reference
- Task: RAD-XXX
- Link: docs/tasks/api-interrupcoes/RAD-XXX.md

## Test Plan
- [x] Testes unitarios passando
- [x] Testes de integracao passando (se aplicavel)
- [x] Coverage >= 80%
- [x] Code review score >= 85/100

## Checklist
- [x] TDD seguido (testes escritos primeiro)
- [x] Clean Architecture respeitada
- [x] SOLID principles aplicados
- [x] Type hints presentes (80%+)
- [x] Docstrings em metodos publicos
- [x] Conventional Commits usado
- [x] EXECUTION_STATUS.md atualizado

## Review Metrics
| Metrica | Valor |
|---------|-------|
| Coverage | XX% |
| Review Score | XX/100 |
| Critical Issues | 0 |
| Lint Errors | 0 |
| Type Errors | 0 |

## Breaking Changes
- [ ] Nenhum breaking change

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Comando gh pr create

```bash
gh pr create \
  --base main \
  --title "feat(api-interrupcoes): RAD-XXX - [Titulo]" \
  --body "$(cat <<'EOF'
## Summary
- Implementa RAD-XXX: [Titulo]

## Test Plan
- [x] Testes passando
- [x] Coverage >= 80%
- [x] Review >= 85/100

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Pre-Commit Checklist

Antes de commitar, verificar:

```bash
# 1. Testes passando
pytest tests/ -q

# 2. Linting
ruff check backend/

# 3. Types
mypy backend/

# 4. Coverage
pytest tests/ --cov=backend --cov-fail-under=80

# 5. Status
git status
git diff --staged
```

### Comando Rapido

```bash
# Verificacao completa
pytest tests/ -q && ruff check backend/ && mypy backend/
```

---

## Fluxo de Trabalho

```
1. Criar branch
   git checkout -b feat/rad-xxx/descricao

2. Desenvolver com TDD
   - Escrever teste (RED)
   - Implementar (GREEN)
   - Refatorar (REFACTOR)

3. Verificar qualidade
   pytest && ruff check && mypy

4. Commitar
   git add .
   git commit (com template)

5. Push
   git push -u origin feat/rad-xxx/descricao

6. Criar PR
   gh pr create (com template)

7. Review e Merge
```

---

## Regras Absolutas

1. **NUNCA** commitar sem testes
2. **NUNCA** commitar com erros de lint/mypy
3. **NUNCA** force push em main/master
4. **NUNCA** commitar secrets/credentials
5. **SEMPRE** usar Conventional Commits
6. **SEMPRE** incluir Task ID no commit
7. **SEMPRE** atualizar EXECUTION_STATUS.md
8. **SEMPRE** incluir metricas (coverage, score)

---

## Exemplos Completos

### Commit de Feature

```bash
git commit -m "$(cat <<'EOF'
feat(domain): implementa entity Interrupcao

- Adiciona entidade Interrupcao com validacoes
- Implementa metodos is_ativa() e is_programada()
- Value Objects CodigoIBGE e TipoInterrupcao

[code-review-approved]
Task: RAD-100
Coverage: 92%
Review Score: 88/100

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

### Commit de Fix

```bash
git commit -m "$(cat <<'EOF'
fix(cache): corrige TTL do cache de interrupcoes

O cache estava expirando antes do tempo esperado
devido a um erro no calculo de segundos.

- Corrige calculo de TTL para 300 segundos
- Adiciona teste para validar expiracao

Task: RAD-108
Coverage: 85%

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

### Commit de Teste

```bash
git commit -m "$(cat <<'EOF'
test(unit): adiciona testes para CodigoIBGE

- Testa criacao de codigo valido
- Testa rejeicao de codigo invalido
- Testa validacao de codigo de Roraima
- Coverage do Value Object: 100%

Task: RAD-119
Coverage: 95%

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Slash Commands Relacionados

| Comando | Descricao |
|---------|-----------|
| `/commit` | Cria commit formatado |
| `/create-pr` | Cria PR com template |
| `/finish-task` | Finaliza task com commit e PR |

---

**Documento mantido por:** Claude Code
**Versao:** 1.0.0
**Ultima Atualizacao:** 2025-12-19
