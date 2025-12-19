---
description: Inicia uma task especifica seguindo o workflow RADAR
argument-hint: RAD-XXX
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, TodoWrite
---

# Start Task - Iniciar Task Especifica

Este comando inicia uma task especifica do projeto RADAR seguindo o workflow de 15 passos.

## Argumento

- `$ARGUMENTS` = Task ID no formato RAD-XXX (ex: RAD-100, RAD-115)

## Workflow de Inicio

### 1. Validar Task ID

```bash
# Verificar se task existe
ls docs/tasks/api-interrupcoes/RAD-*.md | grep "$ARGUMENTS"

# Se nao existir, informar usuario
```

### 2. Verificar Dependencias

```bash
# Ler EXECUTION_STATUS.md
cat docs/tasks/api-interrupcoes/EXECUTION_STATUS.md

# Verificar se dependencias estao CONCLUIDO
grep "CONCLUIDO" docs/tasks/api-interrupcoes/EXECUTION_STATUS.md
```

Se alguma dependencia nao estiver CONCLUIDA -> PARAR e informar.

### 3. Ler Especificacao da Task

```bash
# Ler arquivo da task
cat docs/tasks/api-interrupcoes/$ARGUMENTS.md
```

Validar presenca de:
- [ ] Objetivo claro
- [ ] Localizacao do arquivo a criar
- [ ] Criterios de aceite
- [ ] Testes TDD especificados
- [ ] Dependencias listadas

### 4. Selecionar Subagente Correto

| Tipo de Task | Subagente | Tasks |
|--------------|-----------|-------|
| Domain (Entities, VOs) | backend-architect | RAD-100 a RAD-104 |
| Infrastructure (Oracle, Cache) | database-optimizer | RAD-105 a RAD-111 |
| Interfaces (FastAPI, Routes) | backend-architect | RAD-112 a RAD-118 |
| Testes | test-engineer | RAD-119 a RAD-121 |
| Seguranca | security-auditor | RAD-122 a RAD-125 |

### 5. Criar Branch

```bash
# Garantir que esta em main atualizado
git checkout main
git pull origin main

# Criar branch seguindo padrao
git checkout -b feat/rad-xxx/descricao-curta
```

Nomenclatura: `{tipo}/{task-id}/{descricao-kebab-case}`

### 6. Atualizar Status

Atualizar EXECUTION_STATUS.md:
- Mudar status para "EM_ANDAMENTO"
- Registrar data de inicio

## Checklist Pre-Desenvolvimento

Antes de iniciar o desenvolvimento:

- [ ] Task ID valido e existente
- [ ] Dependencias verificadas e CONCLUIDAS
- [ ] Especificacao lida e compreendida
- [ ] Subagente correto selecionado
- [ ] Branch criada seguindo nomenclatura
- [ ] Status atualizado para EM_ANDAMENTO

## Proximos Passos

Apos iniciar a task, execute:
1. `/create-test` - Criar testes primeiro (RED phase)
2. Implementar codigo (GREEN phase)
3. Refatorar (REFACTOR phase)
4. `/review-code` - Code review
5. `/finish-task` - Finalizar

## Exemplo de Uso

```bash
/start-task RAD-100
# Inicia task RAD-100: Entity Interrupcao
# Cria branch feat/rad-100/entity-interrupcao
# Atualiza status para EM_ANDAMENTO
```
