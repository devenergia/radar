---
description: Cria um Pull Request seguindo template RADAR
argument-hint: [titulo opcional]
allowed-tools: Bash(git:*), Bash(gh:*)
---

# Create PR - Criar Pull Request

Cria um Pull Request seguindo os padroes do projeto RADAR.

## Pre-Requisitos

Antes de criar PR:
- [ ] Todos os testes passando
- [ ] Coverage >= 80%
- [ ] Code review >= 85/100
- [ ] Commit criado
- [ ] Branch pushed para remote

## Verificacoes Pre-PR

```bash
# Verificar status
git status

# Verificar commits pendentes
git log origin/main..HEAD --oneline

# Verificar se branch esta atualizada
git fetch origin
git status -uno
```

## Template do PR

```bash
gh pr create \
  --base main \
  --title "feat(api-interrupcoes): [TITULO]" \
  --body "$(cat <<'EOF'
## Summary
[1-3 bullet points descrevendo as mudancas]

## Task Reference
- Task: RAD-XXX
- Link: docs/tasks/api-interrupcoes/RAD-XXX.md

## Changes
- [Lista detalhada de mudancas]

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

## Review Metrics
| Metrica | Valor |
|---------|-------|
| Coverage | XX% |
| Review Score | XX/100 |
| Critical Issues | 0 |
| Lint Errors | 0 |
| Type Errors | 0 |

## Screenshots (se aplicavel)
[Adicionar screenshots de endpoints/responses]

## Breaking Changes
- [ ] Nenhum breaking change
- [ ] Lista de breaking changes...

## Dependencies
- [ ] Nenhuma nova dependencia
- [ ] Lista de novas dependencias...

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Titulos de PR por Tipo

| Tipo de Task | Prefixo | Exemplo |
|--------------|---------|---------|
| Domain | feat(domain) | `feat(domain): implementa entity Interrupcao` |
| Infrastructure | feat(infra) | `feat(infra): configura conexao Oracle DBLink` |
| API | feat(api) | `feat(api): adiciona endpoint interrupcoes ativas` |
| Testes | test | `test(unit): adiciona testes para CodigoIBGE` |
| Seguranca | feat(security) | `feat(security): implementa autenticacao API Key` |
| Bug Fix | fix | `fix(cache): corrige TTL do cache` |
| Refactor | refactor | `refactor(domain): extrai validacoes` |

## Labels Recomendados

```bash
gh pr edit --add-label "enhancement"
gh pr edit --add-label "api-interrupcoes"
gh pr edit --add-label "ready-for-review"
```

## Reviewers

```bash
# Adicionar reviewers (se configurado)
gh pr edit --add-reviewer @team-lead
```

## Apos Criar PR

1. Verificar se CI passou
2. Aguardar review
3. Responder comentarios
4. Fazer merge apos aprovacao

## Exemplo de Uso

```bash
# Criar PR com titulo automatico
/create-pr

# Criar PR com titulo especifico
/create-pr "implementa validacao de CodigoIBGE"
```

## Comandos Relacionados

| Comando | Descricao |
|---------|-----------|
| `/finish-task` | Finaliza task antes do PR |
| `/commit` | Cria commit formatado |
| `/review-task` | Executa review antes do PR |
