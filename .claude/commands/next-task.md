---
description: Busca a proxima task disponivel e executa o fluxo completo de 15 passos
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, TodoWrite
---

# Next Task - Fluxo Completo de Desenvolvimento RADAR

Este comando busca a proxima task disponivel e executa o fluxo profissional de 15 passos.

## FLUXO OBRIGATORIO DE 15 PASSOS

### PREPARACAO (Passos 1-3)

#### Passo 1: Identificar Proxima Task

```bash
# IMPORTANTE: Escolher projeto para buscar proxima task
# Projetos disponiveis:
# - api-interrupcoes (RAD-100 a RAD-130)
# - mapa-interrupcoes (RAD-200 a RAD-230)

# Se usuario especificou projeto via argumento:
PROJECT="${1:-api-interrupcoes}"

# Ler EXECUTION_STATUS.md do projeto
cat docs/tasks/$PROJECT/EXECUTION_STATUS.md

# Encontrar primeira task "PENDENTE" seguindo ordem de execucao
grep "PENDENTE" docs/tasks/$PROJECT/EXECUTION_STATUS.md

# Verificar dependencias no INDEX.md
cat docs/tasks/$PROJECT/INDEX.md
```

**Detectar projeto automaticamente:**
- Se branch atual contem `rad-1` -> api-interrupcoes
- Se branch atual contem `rad-2` -> mapa-interrupcoes

Se dependencia nao esta CONCLUIDO -> PARAR e informar

#### Passo 2: Ler Documentacao

```bash
# Ler arquivo da task do projeto
cat docs/tasks/$PROJECT/RAD-XXX.md

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

#### Passo 3: Selecionar Subagente Correto

| Tipo de Task | Subagente | Keywords |
|--------------|-----------|----------|
| Domain (Entities, VOs) | backend-architect | entity, value object, domain |
| Oracle/DBLink | database-optimizer | oracle, repository, dblink, cache |
| Use Cases | backend-architect | use case, service, aggregator |
| FastAPI/Routes | backend-architect | fastapi, route, endpoint, schema |
| Testes | test-engineer | test, pytest, coverage |
| Seguranca | security-auditor | auth, rate limit, logging |
| Frontend (React/Leaflet) | backend-architect | react, component, leaflet, frontend |
| Deploy (NGINX/Docker) | backend-architect | nginx, docker, deploy |

---

### DESENVOLVIMENTO TDD (Passos 4-8)

#### Passo 4: Criar Branch

```bash
# Garantir que esta em main atualizado
git checkout main
git pull origin main

# Criar branch seguindo padrao
git checkout -b feature/rad-XXX-descricao-curta
```

Convencoes:
- `feat/` ou `feature/` - Nova funcionalidade
- `fix/` - Correcao de bug
- `test/` - Adicao de testes
- `refactor/` - Refatoracao

#### Passo 5: TDD RED - Escrever Testes que Falham

```bash
# 1. Criar arquivo de teste conforme especificado na task
# 2. Escrever testes baseados nos Criterios de Aceite
# 3. Executar testes - DEVEM FALHAR

pytest tests/unit/domain/test_XXX.py -v

# Se passarem -> testes estao errados
```

#### Passo 6: TDD GREEN - Implementar Codigo Minimo

```bash
# 1. Implementar APENAS o necessario para passar os testes
# 2. Nao adicionar features extras
# 3. Nao otimizar prematuramente

pytest tests/unit/domain/test_XXX.py -v

# DEVEM PASSAR
```

#### Passo 7: TDD REFACTOR - Melhorar Codigo

```bash
# 1. Refatorar mantendo testes passando
# 2. Remover duplicacao
# 3. Melhorar nomes e legibilidade

pytest tests/unit/domain/test_XXX.py -v

# DEVEM CONTINUAR PASSANDO
```

#### Passo 8: Verificar Coverage

```bash
# Executar com coverage
pytest tests/unit/ --cov=backend --cov-report=term-missing

# Coverage minimo: 80%
# Domain layer: 90%+
```

---

### QUALIDADE (Passos 9-12)

#### Passo 9: Code Review Automatico

Executar /review-task para review com agentes especialistas.

Categorias avaliadas:
- Clean Architecture (20%)
- SOLID Principles (15%)
- Type Safety (15%)
- Security (20%)
- Performance (10%)
- Testing (15%)
- Documentation (5%)

Score minimo: 85/100

#### Passo 10: Validacao de Seguranca

Checklist:
- [ ] API Key validada em endpoints
- [ ] Queries parametrizadas (sem concatenacao)
- [ ] Validacao de entrada (Pydantic)
- [ ] Erros no formato ANEEL
- [ ] Dados sensiveis nao expostos em logs

#### Passo 11: Validacao de Arquitetura

```bash
# Verificar Clean Architecture
# Domain NAO importa de Infrastructure
grep -r "from.*infrastructure" backend/shared/domain/

# Application NAO importa de API
grep -r "from.*api" backend/shared/application/
```

#### Passo 12: Executar Suite Completa

```bash
# Executar TODOS os testes
pytest tests/ --tb=short -q

# Linting
ruff check backend/

# Type checking
mypy backend/
```

---

### ENTREGA (Passos 13-15)

#### Passo 13: Atualizar EXECUTION_STATUS.md

Editar `docs/tasks/$PROJECT/EXECUTION_STATUS.md`:
- Mudar status da task para "CONCLUIDO"
- Atualizar data de conclusao

**Identificar projeto:**
- RAD-1XX -> `docs/tasks/api-interrupcoes/EXECUTION_STATUS.md`
- RAD-2XX -> `docs/tasks/mapa-interrupcoes/EXECUTION_STATUS.md`

#### Passo 14: Criar Commit

```bash
git add .
git commit -m "feat(api-interrupcoes): implementa RAD-XXX

- Descricao das mudancas
- Testes TDD implementados
- Coverage: XX%

[code-review-approved]
Task: RAD-XXX
Review Score: XX/100

Generated with Claude Code

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### Passo 15: Push e Pull Request

```bash
# Push
git push -u origin feature/rad-XXX-descricao

# Criar PR (se necessario)
gh pr create \
  --base main \
  --title "feat(api-interrupcoes): RAD-XXX - Titulo" \
  --body "## Summary
- Implementa RAD-XXX: {titulo}

## Test Plan
- [x] Testes unitarios passando
- [x] Coverage >= 80%
- [x] Code review >= 85/100

## Checklist
- [x] Clean Architecture respeitada
- [x] TDD seguido
- [x] Conventional Commits"
```

---

## REGRAS ABSOLUTAS

1. **NUNCA pular passos** - Todos os 15 passos sao obrigatorios
2. **NUNCA implementar sem testes** - TDD e obrigatorio
3. **NUNCA commitar sem validacoes** - ruff, mypy, pytest devem passar
4. **SEMPRE fazer review** - Score >= 85 obrigatorio
5. **SEMPRE atualizar status** - EXECUTION_STATUS.md em dia

## EXECUCAO

Ao executar este comando, voce DEVE:

1. Usar TodoWrite para criar lista com os 15 passos
2. Marcar cada passo como in_progress quando iniciar
3. Marcar cada passo como completed quando finalizar
4. NUNCA pular para o proximo passo sem completar o atual
5. Informar claramente cada transicao de passo
