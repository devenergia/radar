---
description: Cria um commit seguindo Conventional Commits
argument-hint: [tipo] [escopo] [descricao]
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(git commit:*), Bash(git log:*)
---

# Criar Commit - Conventional Commits

Crie um commit seguindo o padrao Conventional Commits do projeto RADAR.

## Argumentos
- `$1` = tipo (feat, fix, docs, style, refactor, test, chore)
- `$2` = escopo (api, domain, infra, tests, etc)
- `$3+` = descricao

## Formato do Commit

```
tipo(escopo): descricao curta

Corpo opcional com mais detalhes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Tipos Permitidos

| Tipo | Uso |
|------|-----|
| `feat` | Nova funcionalidade |
| `fix` | Correcao de bug |
| `docs` | Documentacao |
| `style` | Formatacao (sem mudanca de codigo) |
| `refactor` | Refatoracao |
| `test` | Adicao/correcao de testes |
| `chore` | Manutencao, configs |

## Escopos Comuns

- `api` - APIs HTTP
- `domain` - Camada de dominio
- `infra` - Infraestrutura
- `tests` - Testes
- `deps` - Dependencias
- `config` - Configuracoes

## Processo

1. Verificar status atual:
```bash
git status
git diff --staged
```

2. Adicionar arquivos (se necessario):
```bash
git add <arquivos>
```

3. Criar commit:
```bash
git commit -m "$(cat <<'EOF'
$1($2): $3

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

## Exemplos

```bash
# Nova feature
feat(api): adicionar endpoint de interrupcoes ativas

# Bug fix
fix(cache): corrigir TTL do cache de interrupcoes

# Testes
test(domain): adicionar testes para CodigoIBGE

# Documentacao
docs(readme): atualizar instrucoes de instalacao
```

## Validacoes Pre-Commit

Antes de commitar, verifique:
- [ ] `ruff check backend/` - Sem erros de lint
- [ ] `pytest -m unit` - Testes unitarios passando
- [ ] `mypy backend/` - Sem erros de tipo
