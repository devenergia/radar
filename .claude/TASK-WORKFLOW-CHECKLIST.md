# Checklist de Workflow para Tasks RADAR

**Projeto:** Sistema de Monitoramento de Indicadores ANEEL
**Versao:** 1.1.0
**Ultima Atualizacao:** 2025-12-19

---

## Visao Geral

Este documento define o checklist obrigatorio para execucao de tasks no Projeto RADAR. Todo desenvolvimento DEVE seguir este workflow para garantir qualidade, rastreabilidade e consistencia.

### Projetos Suportados

| Projeto | Tasks | Base Legal | Status |
|---------|-------|------------|--------|
| **API Interrupcoes** | RAD-100 a RAD-130 | Oficio Circular 14/2025-SFE/ANEEL | Em Desenvolvimento |
| **Mapa Interrupcoes** | RAD-200 a RAD-230 | REN 1.137/2025 Art. 106-107 | Planejado |

**Identificacao automatica de projeto:**
- RAD-1XX (100-199) -> `docs/tasks/api-interrupcoes/`
- RAD-2XX (200-299) -> `docs/tasks/mapa-interrupcoes/`

---

## Workflow em 15 Passos

### Fase 1: Preparacao (Passos 1-3)

#### [ ] Passo 1: Identificar Proxima Task

```bash
# Identificar projeto (automatico baseado no Task ID)
# RAD-1XX -> api-interrupcoes
# RAD-2XX -> mapa-interrupcoes

PROJECT="api-interrupcoes"  # ou "mapa-interrupcoes"

# Verificar task pendente
cat docs/tasks/$PROJECT/EXECUTION_STATUS.md | grep "PENDENTE"

# OU consultar INDEX para ver dependencias
cat docs/tasks/$PROJECT/INDEX.md
```

**Criterios de selecao:**
- Task com status `PENDENTE`
- Todas as dependencias estao `CONCLUIDO`
- Nao ha bloqueios externos

**Ordem de execucao - API Interrupcoes (RAD-1XX):**
| Fase | Tasks | Foco |
|------|-------|------|
| 1 - Domain | RAD-100 a RAD-104 | Entities, VOs, Services |
| 2 - Application | RAD-105 a RAD-107 | Protocols, Use Cases |
| 3 - Infrastructure | RAD-108 a RAD-111 | Oracle, Cache, Repos |
| 4 - Interfaces | RAD-112 a RAD-116 | FastAPI, Routes, Schemas |
| 5 - Testes | RAD-117 a RAD-121 | Unit, Integration, E2E |
| 6 - Seguranca | RAD-122 a RAD-130 | Auth, Rate Limit, Logs |

**Ordem de execucao - Mapa Interrupcoes (RAD-2XX):**
| Fase | Tasks | Foco |
|------|-------|------|
| 1 - Domain | RAD-200 a RAD-204 | VOs, Entity, Services |
| 2 - Application | RAD-205 a RAD-207 | Protocols, Use Cases |
| 3 - Infrastructure | RAD-208 a RAD-211 | Oracle, MV, Scheduler, GeoJSON |
| 4 - API | RAD-212 a RAD-215 | Schemas, Endpoints |
| 5 - Frontend | RAD-216 a RAD-222 | React, Leaflet, Dashboard |
| 6 - Testes | RAD-223 a RAD-227 | Unit, Integration, E2E, WCAG |
| 7 - Deploy | RAD-228 a RAD-230 | NGINX, Monitoring, Docs |

#### [ ] Passo 2: Ler Especificacao Completa

```bash
# Ler arquivo da task do projeto correto
cat docs/tasks/$PROJECT/RAD-XXX.md
```

**Validar presenca de:**
- [ ] Objetivo claro
- [ ] Localizacao do arquivo
- [ ] Criterios de aceite
- [ ] Dependencias listadas
- [ ] Testes TDD especificados

#### [ ] Passo 3: Selecionar Subagente Correto

| Tipo de Task | Subagente | Keywords |
|--------------|-----------|----------|
| Domain (Entities, VOs) | backend-architect | entity, value object, domain |
| Oracle/DBLink | database-optimizer | oracle, repository, dblink |
| Use Cases | backend-architect | use case, service, aggregator |
| FastAPI/Routes | backend-architect | fastapi, route, endpoint, schema |
| Testes | test-engineer | test, pytest, coverage |
| Seguranca | security-auditor | auth, rate limit, logging |

---

### Fase 2: Desenvolvimento TDD (Passos 4-8)

#### [ ] Passo 4: Criar Branch

```bash
# Formato: tipo/task-id/descricao-curta
git checkout -b feat/rad-xxx/descricao-curta

# Exemplos:
# feat/rad-100/entity-interrupcao
# feat/rad-105/oracle-connection
# feat/rad-112/fastapi-app
```

**Convencao de branches:**
- `feat/` - Nova funcionalidade
- `fix/` - Correcao de bug
- `refactor/` - Refatoracao sem mudanca de comportamento
- `test/` - Adicao ou correcao de testes
- `docs/` - Documentacao apenas

#### [ ] Passo 5: Escrever Testes PRIMEIRO (Red Phase)

```bash
# Criar arquivo de teste conforme especificado na task
# tests/unit/domain/value_objects/test_codigo_ibge.py

# Executar testes (devem FALHAR)
pytest tests/unit/domain/value_objects/test_codigo_ibge.py -v

# Confirmar falha
# Expected: FAILED (testes sem implementacao)
```

**Padrao AAA para testes:**
```python
class TestCodigoIBGE:
    def test_deve_criar_codigo_valido_para_boa_vista(self):
        # Arrange - Configurar dados
        codigo = "1400100"

        # Act - Executar acao
        result = CodigoIBGE.create(codigo)

        # Assert - Verificar resultado
        assert result.is_success
        assert result.value.valor == "1400100"
```

#### [ ] Passo 6: Implementar Codigo (Green Phase)

```bash
# Implementar APENAS o necessario para testes passarem
# Seguir Clean Architecture e SOLID

# Executar testes novamente
pytest tests/unit/domain/value_objects/test_codigo_ibge.py -v

# Confirmar sucesso
# Expected: PASSED
```

**Padroes obrigatorios:**
```python
# Usar Protocol (nao ABC)
from typing import Protocol

class InterrupcaoRepository(Protocol):
    async def buscar_ativas(self) -> list[Interrupcao]: ...

# Value Objects imutaveis
@dataclass(frozen=True)
class CodigoIBGE:
    valor: str

# Result Pattern
def buscar(self) -> Result[list[Interrupcao], DomainError]:
    ...
```

#### [ ] Passo 7: Refatorar (Refactor Phase)

**Checklist de refatoracao:**
- [ ] Nomes claros e descritivos
- [ ] Funcoes pequenas (< 20 linhas ideal)
- [ ] DRY - nao repetir codigo
- [ ] Type hints em 80%+ das funcoes
- [ ] Docstrings em metodos publicos
- [ ] Imports organizados (stdlib -> third-party -> local)

```bash
# Executar testes apos refatoracao
pytest tests/unit/domain/value_objects/test_codigo_ibge.py -v

# Confirmar que ainda passam
# Expected: PASSED (mesmo comportamento)
```

#### [ ] Passo 8: Verificar Coverage

```bash
# Executar com coverage
pytest tests/unit/ --cov=backend --cov-report=term-missing

# Verificar coverage >= 80%
# Se < 80%, adicionar mais testes
```

**Metas de coverage RADAR:**
| Camada | Minimo | Ideal |
|--------|--------|-------|
| Domain | 90% | 95% |
| Infrastructure | 80% | 85% |
| Use Cases | 85% | 90% |
| API | 80% | 85% |

---

### Fase 3: Validacao (Passos 9-12)

#### [ ] Passo 9: Code Review Automatico

```bash
# Executar skill code-review
# Score minimo: 85/100
# Sem critical issues
```

**Categorias avaliadas:**
| Categoria | Peso | Threshold Critical |
|-----------|------|-------------------|
| Clean Architecture | 20% | < 50% |
| SOLID Principles | 15% | - |
| Type Safety | 15% | - |
| Security | 20% | < 50% |
| Performance | 10% | - |
| Testing | 15% | - |
| Documentation | 5% | - |

#### [ ] Passo 10: Validacao de Seguranca

**Checklist de seguranca:**
- [ ] API Key validada em endpoints
- [ ] Queries parametrizadas (sem concatenacao)
- [ ] Validacao de entrada (Pydantic)
- [ ] Erros no formato ANEEL (idcStatusRequisicao)
- [ ] Dados sensiveis nao expostos em logs

#### [ ] Passo 11: Validacao de Arquitetura

**Clean Architecture RADAR:**
```
backend/
  shared/
    domain/           <- NAO importa infrastructure
      entities/
      value_objects/
      services/
    infrastructure/   <- Implementa interfaces do domain
      database/
      cache/
  apps/
    api_interrupcoes/
      routes.py       <- Thin, delega para use_cases
      use_cases/
      repositories/
```

**Direcao de dependencias:**
```
Interfaces (Routes)
      |
      v
Application (Use Cases)
      |
      v
Domain (Entities, VOs, Protocols)
      ^
      |
Infrastructure (Repositories, Cache)
```

#### [ ] Passo 12: Executar Suite Completa

```bash
# Executar TODOS os testes
pytest tests/ --tb=short -q

# Verificar que nenhum teste existente quebrou
# Expected: ALL PASSED

# Verificar linting
ruff check backend/

# Verificar types
mypy backend/
```

---

### Fase 4: Finalizacao (Passos 13-15)

#### [ ] Passo 13: Atualizar Documentacao

**Identificar projeto:**
- RAD-1XX -> `docs/tasks/api-interrupcoes/EXECUTION_STATUS.md`
- RAD-2XX -> `docs/tasks/mapa-interrupcoes/EXECUTION_STATUS.md`

**Arquivos a atualizar:**
- [ ] `docs/tasks/$PROJECT/EXECUTION_STATUS.md` - Status da task
- [ ] Docstrings no codigo
- [ ] OpenAPI descriptions (se API)

```markdown
# Template de atualizacao EXECUTION_STATUS.md
| RAD-XXX | Titulo | `[X]` CONCLUIDO | Data | - |
```

#### [ ] Passo 14: Criar Commit

```bash
# OBRIGATORIO: Code review aprovado antes do commit
# Formato Conventional Commits

git add .
git commit -m "feat(api-interrupcoes): implementa RAD-XXX

- Descricao das mudancas
- ...

[code-review-approved]
Task: RAD-XXX
Coverage: XX%
Review Score: XX/100

Generated with Claude Code

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

**Tipos de commit:**
- `feat` - Nova funcionalidade
- `fix` - Correcao de bug
- `refactor` - Refatoracao
- `test` - Testes
- `docs` - Documentacao
- `chore` - Manutencao

#### [ ] Passo 15: Criar Pull Request (se necessario)

```bash
# Push da branch
git push -u origin feat/rad-xxx/descricao

# Criar PR
gh pr create --title "feat(api-interrupcoes): implementa RAD-XXX" --body "..."
```

**Template de PR:**
```markdown
## Summary
- Implementa RAD-XXX: [Titulo]
- [Descricao das mudancas]

## Test Plan
- [ ] Testes unitarios passam
- [ ] Coverage >= 80%
- [ ] Code review >= 85/100

## Checklist
- [ ] Criterios de aceite atendidos
- [ ] Documentacao atualizada
- [ ] Sem breaking changes
```

---

## Comandos Rapidos

| Comando | Descricao |
|---------|-----------|
| `/tdd-development RAD-XXX` | Workflow TDD completo |
| `/test-runner --scope unit` | Executar testes unitarios |
| `/code-review RAD-XXX` | Code review automatico |
| `/commit-formatter RAD-XXX` | Criar commit formatado |
| `/branch-manager --action create` | Criar branch |

---

## Regras de Ouro

1. **NUNCA pular testes** - Escrever ANTES da implementacao (TDD)
2. **NUNCA commit sem code review** - Score >= 85 obrigatorio
3. **NUNCA ignorar dependencias** - Verificar EXECUTION_STATUS antes de iniciar
4. **SEMPRE atualizar status** - EXECUTION_STATUS.md em dia
5. **SEMPRE usar Protocol** - Nao usar ABC para interfaces

---

## Troubleshooting

### Task travada
- Verificar dependencias nao concluidas
- Consultar INDEX.md para ordem correta

### Coverage baixo
- Adicionar testes de edge cases
- Testar caminhos de erro
- Mockar dependencias externas

### Code review falhou
- Verificar critical issues primeiro
- Corrigir violacoes de Clean Architecture
- Adicionar type hints/docstrings

### Testes falhando
```bash
# Ver detalhes da falha
pytest tests/unit/test_xxx.py -v --tb=long

# Executar teste especifico
pytest tests/unit/test_xxx.py::test_nome -v
```

---

**Documento mantido por:** Claude Code
**Referencia:** docs/development/*.md, EXECUTION_STATUS.md
