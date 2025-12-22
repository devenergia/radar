---
description: Busca a proxima task disponivel e executa o fluxo completo de 15 passos
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, TodoWrite
---

# Next Task - Fluxo Completo de Desenvolvimento RADAR

Este comando busca a proxima task disponivel e executa o fluxo profissional de 15 passos.

## FLUXO OBRIGATORIO DE 15 PASSOS

---

### PREPARACAO (Passos 1-4)

#### Passo 1: Identificar Proxima Task

```bash
# Projeto: api-interrupcoes (RAD-100 a RAD-130)
# Ler EXECUTION_STATUS.md
cat docs/tasks/api-interrupcoes/EXECUTION_STATUS.md

# Encontrar primeira task "PENDENTE"
grep "PENDENTE" docs/tasks/api-interrupcoes/EXECUTION_STATUS.md

# Verificar dependencias no INDEX.md
cat docs/tasks/api-interrupcoes/INDEX.md
```

Se dependencia nao esta CONCLUIDO -> PARAR e informar

#### Passo 2: Ler Documentacao da Task

```bash
# Ler arquivo da task
cat docs/tasks/api-interrupcoes/RAD-XXX.md

# Ler guias de desenvolvimento
cat docs/development/01-clean-architecture.md
cat docs/development/04-tdd-test-driven-development.md
```

Validar presenca de:
- [ ] Objetivo claro
- [ ] Localizacao do arquivo
- [ ] Testes TDD especificados
- [ ] Criterios de aceite
- [ ] Dependencias listadas

#### Passo 3: Criar Issue no GitHub

```bash
gh issue create \
  --title "feat(api-interrupcoes): RAD-XXX - {Titulo}" \
  --body "## Descricao
{descricao_da_task}

## Criterios de Aceite
{lista_de_ACs}

## Arquivos Afetados
{lista_arquivos}

## Dependencias
{deps_ou_nenhuma}

---
Task: RAD-XXX"
```

#### Passo 4: Criar Branch

```bash
# Garantir que esta em hm atualizado
git checkout hm
git pull origin hm

# Criar branch seguindo padrao
git checkout -b feat/rad-XXX/descricao-curta
```

---

### DESENVOLVIMENTO TDD (Passos 5-8)

#### Passo 5: TDD RED - Escrever Testes que Falham

```bash
# 1. Criar arquivo de teste conforme especificado na task
# 2. Escrever testes baseados nos Criterios de Aceite
# 3. Executar testes - DEVEM FALHAR

"D:/Projeto Radar/venv/Scripts/pytest.exe" backend/tests/unit/... -v

# Se passarem -> testes estao errados
```

#### Passo 6: TDD GREEN - Implementar Codigo Minimo

```bash
# 1. Implementar APENAS o necessario para passar os testes
# 2. Nao adicionar features extras
# 3. Nao otimizar prematuramente

"D:/Projeto Radar/venv/Scripts/pytest.exe" backend/tests/unit/... -v

# DEVEM PASSAR
```

#### Passo 7: TDD REFACTOR - Melhorar Codigo

```bash
# 1. Refatorar mantendo testes passando
# 2. Remover duplicacao
# 3. Melhorar nomes e legibilidade

"D:/Projeto Radar/venv/Scripts/pytest.exe" backend/tests/unit/... -v

# DEVEM CONTINUAR PASSANDO
```

#### Passo 8: Verificar Coverage

```bash
"D:/Projeto Radar/venv/Scripts/pytest.exe" backend/tests/unit/... \
  --cov=backend.shared.domain... --cov-report=term-missing

# Coverage minimo: 80%
# Domain layer: 90%+
```

---

### QUALIDADE (Passos 9-10)

#### Passo 9: Validacoes de Codigo

```bash
# Linting
"D:/Projeto Radar/venv/Scripts/ruff.exe" check backend/shared/...

# Type checking
"D:/Projeto Radar/venv/Scripts/mypy.exe" backend/shared/... --ignore-missing-imports

# Clean Architecture
grep -r "from.*infrastructure" backend/shared/domain/ || echo "OK"
```

#### Passo 10: Executar Suite Completa

```bash
# Executar TODOS os testes unitarios
"D:/Projeto Radar/venv/Scripts/pytest.exe" backend/tests/unit/ -q --tb=short

# Todos devem passar
```

---

### ENTREGA (Passos 11-12)

#### Passo 11: Atualizar EXECUTION_STATUS.md

Editar `docs/tasks/api-interrupcoes/EXECUTION_STATUS.md`:
- Mudar status da task para "CONCLUIDO"
- Atualizar data de conclusao
- Adicionar entrada no Historico

#### Passo 12: Criar Commit

```bash
git add .
git commit -m "feat(domain): descricao RAD-XXX

- Detalhe das mudancas
- Testes TDD implementados
- Coverage: XX%

Task: RAD-XXX"
```

---

### FINALIZACAO (Passos 13-15)

#### Passo 13: Push e Pull Request

```bash
# Push
git push -u origin feat/rad-XXX/descricao-curta

# Criar PR para hm
gh pr create \
  --base hm \
  --title "feat(domain): RAD-XXX - Titulo" \
  --body "## Summary
- Implementa RAD-XXX: {titulo}

## Test Plan
- [x] Testes unitarios passando
- [x] Coverage >= 80%
- [x] Ruff/MyPy OK

## Checklist
- [x] Clean Architecture respeitada
- [x] TDD seguido
- [x] Conventional Commits

Task: RAD-XXX
Closes #{issue_number}"
```

#### Passo 14: Merge e Cleanup

```bash
# Aguardar aprovacao/merge do PR
# Apos merge:

# Voltar para hm
git checkout hm

# Atualizar hm com merge
git pull origin hm

# Limpar referencias remotas
git fetch --prune

# Remover branch local
git branch -d feat/rad-XXX/descricao-curta
```

#### Passo 15: Fechar Issue

```bash
# Fechar issue relacionada
gh issue close {ISSUE_NUMBER} --comment "Implementado no PR #{PR_NUMBER}"

# Verificar status
gh issue view {ISSUE_NUMBER} --json state
```

---

## REGRAS ABSOLUTAS

1. **NUNCA pular passos** - Todos os 15 passos sao obrigatorios
2. **NUNCA implementar sem testes** - TDD e obrigatorio
3. **NUNCA commitar sem validacoes** - ruff, mypy, pytest devem passar
4. **SEMPRE criar Issue antes da branch** - Passo 3 obrigatorio
5. **SEMPRE atualizar status** - EXECUTION_STATUS.md em dia
6. **SEMPRE usar venv do projeto** - D:/Projeto Radar/venv/Scripts/

---

## EXECUCAO

Ao executar este comando, voce DEVE:

1. Usar TodoWrite para criar lista com os 15 passos
2. Marcar cada passo como in_progress quando iniciar
3. Marcar cada passo como completed quando finalizar
4. NUNCA pular para o proximo passo sem completar o atual
5. Informar claramente cada transicao de passo com formato:

```
---
## RAD-XXX - Passo N: Nome do Passo

**Objetivo:** Descricao do que sera feito

[execucao]

**Resultado:** OK/ERRO
---
```
