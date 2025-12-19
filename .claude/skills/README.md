# Skills - Projeto RADAR

## Visao Geral

Este diretorio contem as skills automatizadas para desenvolvimento do Projeto RADAR.
Skills sao workflows reutilizaveis que Claude Code pode invocar para tarefas comuns.

## Estrutura de Diretorios

```
skills/
  orchestration/           # Skills de orquestracao (workflows complexos)
    tdd-development/       # Workflow TDD completo
      skill.json           # Configuracao da skill
      skill.md             # Documentacao detalhada
  validation/              # Skills de validacao
    code-review/           # Code review automatico
    test-runner/           # Execucao de testes pytest
  utilities/               # Skills utilitarias
    branch-manager/        # Gerenciamento de branches Git
    commit-formatter/      # Formatacao de commits
```

## Skills Disponiveis

### Orchestration

#### tdd-development
**Descricao:** Orquestra workflow TDD completo com selecao automatica de subagentes.

**Uso:**
```bash
/tdd-development RAD-100 --type both --autoCommit
```

**Parametros:**
- `taskId`: Task ID no formato RAD-XXX (obrigatorio)
- `type`: test | implementation | both
- `autoCommit`: Commitar se testes passarem (default: true)
- `minCoverage`: Coverage minimo exigido (default: 80)

### Validation

#### code-review
**Descricao:** Executa code review automatico com 7 categorias de validacao.

**Uso:**
```bash
/code-review RAD-100 --minScore 85
```

**Categorias:**
| Categoria | Peso | Critical |
|-----------|------|----------|
| Clean Architecture | 20% | < 50% |
| SOLID Principles | 15% | - |
| Type Safety | 15% | - |
| Security | 20% | < 50% |
| Performance | 10% | - |
| Testing | 15% | - |
| Documentation | 5% | - |

#### test-runner
**Descricao:** Executa testes pytest com geracao de coverage reports.

**Uso:**
```bash
/test-runner --scope unit --coverage
```

**Parametros:**
- `scope`: unit | integration | e2e | all
- `pattern`: Padrao para filtrar testes
- `coverage`: Gerar relatorio (default: true)
- `failFast`: Parar na primeira falha

### Utilities

#### branch-manager
**Descricao:** Gerencia branches Git seguindo nomenclatura RADAR.

**Uso:**
```bash
/branch-manager --action create --taskId RAD-100 --description entity-interrupcao
```

**Nomenclatura:** `{type}/{taskId}-{description}`
- Exemplo: `feature/RAD-100-entity-interrupcao`

#### commit-formatter
**Descricao:** Formata commits seguindo Conventional Commits.

**Uso:**
```bash
/commit-formatter --taskId RAD-100 --type feat --scope domain --message "implementa entidade Interrupcao"
```

**Formato:** `{type}({scope}): {message}`
- Exemplo: `feat(domain): implementa entidade Interrupcao`

## Workflow de Desenvolvimento

```
1. Identificar task (RAD-XXX)
   |
2. Criar branch (/branch-manager --action create)
   |
3. Desenvolver com TDD (/tdd-development --type both)
   |   |-- Escrever testes (Red Phase)
   |   |-- Rodar testes (/test-runner) - devem falhar
   |   |-- Implementar codigo (Green Phase)
   |   |-- Rodar testes - devem passar
   |   |-- Refatorar (Refactor Phase)
   |
4. Code Review (/code-review --minScore 85)
   |
5. Commit (/commit-formatter)
   |
6. Pull Request
```

## Metas de Qualidade

### Coverage Minimo
| Camada | Minimo | Ideal |
|--------|--------|-------|
| Domain | 90% | 95% |
| Infrastructure | 80% | 85% |
| Use Cases | 85% | 90% |
| API | 80% | 85% |

### Code Review Score
- **Minimo para commit:** 85/100
- **Zero critical issues** (Security < 50% ou Clean Architecture < 50%)

## Subagentes Disponiveis

| Subagente | Foco | Tasks |
|-----------|------|-------|
| backend-architect | Domain, Use Cases, API | RAD-100 a RAD-104, RAD-112 a RAD-118 |
| database-optimizer | Oracle, DBLink, Cache | RAD-105 a RAD-111 |
| test-engineer | Testes, Coverage | RAD-119 a RAD-121 |
| security-auditor | Auth, Rate Limit, Logs | RAD-122 a RAD-125 |

## Versao

- **Skills Version:** 1.0.0
- **Projeto:** RADAR - Sistema de Monitoramento ANEEL
- **Ultima Atualizacao:** 2025-12-19
