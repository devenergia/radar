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

### 1. Validar Task ID e Identificar Projeto

```bash
# Identificar projeto baseado no Task ID:
# - RAD-1XX (100-199) -> api-interrupcoes
# - RAD-2XX (200-299) -> mapa-interrupcoes

# Extrair numero da task
TASK_NUM=$(echo "$ARGUMENTS" | grep -oP '\d+')

if [ "$TASK_NUM" -ge 100 ] && [ "$TASK_NUM" -lt 200 ]; then
    PROJECT="api-interrupcoes"
elif [ "$TASK_NUM" -ge 200 ] && [ "$TASK_NUM" -lt 300 ]; then
    PROJECT="mapa-interrupcoes"
else
    echo "Task ID invalido: $ARGUMENTS"
    exit 1
fi

# Verificar se task existe
ls docs/tasks/$PROJECT/RAD-*.md | grep "$ARGUMENTS"
```

### 2. Verificar Dependencias

```bash
# Ler EXECUTION_STATUS.md do projeto correto
cat docs/tasks/$PROJECT/EXECUTION_STATUS.md

# Verificar se dependencias estao CONCLUIDO
grep "CONCLUIDO" docs/tasks/$PROJECT/EXECUTION_STATUS.md
```

Se alguma dependencia nao estiver CONCLUIDA -> PARAR e informar.

### 3. Ler Especificacao da Task

```bash
# Ler arquivo da task do projeto correto
cat docs/tasks/$PROJECT/$ARGUMENTS.md
```

Validar presenca de:
- [ ] Objetivo claro
- [ ] Localizacao do arquivo a criar
- [ ] Criterios de aceite
- [ ] Testes TDD especificados
- [ ] Dependencias listadas

### 4. Selecionar Subagente Correto

**API Interrupcoes (RAD-1XX):**

| Tipo de Task | Subagente | Tasks |
|--------------|-----------|-------|
| Domain (Entities, VOs) | backend-architect | RAD-100 a RAD-104 |
| Infrastructure (Oracle, Cache) | database-optimizer | RAD-105 a RAD-111 |
| Interfaces (FastAPI, Routes) | backend-architect | RAD-112 a RAD-118 |
| Testes | test-engineer | RAD-119 a RAD-121 |
| Seguranca | security-auditor | RAD-122 a RAD-125 |

**Mapa Interrupcoes (RAD-2XX):**

| Tipo de Task | Subagente | Tasks |
|--------------|-----------|-------|
| Domain (VOs, Entity, Services) | backend-architect | RAD-200 a RAD-204 |
| Application (Protocols, Use Cases) | backend-architect | RAD-205 a RAD-207 |
| Infrastructure (Oracle, Scheduler) | database-optimizer | RAD-208 a RAD-211 |
| API (Schemas, Endpoints) | backend-architect | RAD-212 a RAD-215 |
| Frontend (React, Leaflet) | backend-architect | RAD-216 a RAD-222 |
| Testes | test-engineer | RAD-223 a RAD-227 |
| Deploy | backend-architect | RAD-228 a RAD-230 |

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
