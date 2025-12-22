# Estrategia de Branches - Projeto RADAR

## Visao Geral

O projeto RADAR utiliza uma estrategia de branches baseada em GitFlow simplificado,
com foco em estabilidade para producao e agilidade no desenvolvimento.

```
prd (producao)
 │
 └── hm (homologacao)
      │
      ├── feat/RAD-XXX/descricao
      ├── fix/RAD-XXX/descricao
      └── docs/descricao
```

## Branches Permanentes

### `prd` - Producao
- **Proposito**: Codigo em producao, estavel e testado
- **Protecao**: Requer PR aprovado + testes passando
- **Deploy**: Automatico para ambiente de producao
- **Merge de**: Apenas `hm` (via PR)

### `hm` - Homologacao
- **Proposito**: Ambiente de testes e validacao pre-producao
- **Protecao**: Requer PR aprovado
- **Deploy**: Automatico para ambiente de homologacao
- **Merge de**: Feature branches (via PR)
- **Base para**: Todas as feature branches

## Branches Temporarias

### `feat/RAD-XXX/descricao`
- **Proposito**: Desenvolvimento de novas funcionalidades
- **Origem**: Criada a partir de `hm`
- **Destino**: Merge para `hm` (via PR)
- **Nomenclatura**: `feat/RAD-104/protocol-interrupcao-repository`

### `fix/RAD-XXX/descricao`
- **Proposito**: Correcao de bugs
- **Origem**: Criada a partir de `hm`
- **Destino**: Merge para `hm` (via PR)
- **Nomenclatura**: `fix/RAD-150/corrigir-calculo-agregacao`

### `docs/descricao`
- **Proposito**: Atualizacoes de documentacao
- **Origem**: Criada a partir de `hm`
- **Destino**: Merge para `hm` (via PR)
- **Nomenclatura**: `docs/update-task-status`

### `hotfix/descricao`
- **Proposito**: Correcoes urgentes em producao
- **Origem**: Criada a partir de `prd`
- **Destino**: Merge para `prd` E `hm` (via PRs)
- **Nomenclatura**: `hotfix/fix-critical-bug`

## Fluxo de Trabalho

### 1. Desenvolvimento de Feature

```bash
# Criar branch a partir de hm
git checkout hm
git pull origin hm
git checkout -b feat/RAD-104/protocol-interrupcao-repository

# Desenvolver e commitar
git add .
git commit -m "feat(domain): add InterrupcaoRepository protocol"

# Push e criar PR
git push -u origin feat/RAD-104/protocol-interrupcao-repository
gh pr create --base hm --title "feat: RAD-104 Protocol InterrupcaoRepository"
```

### 2. Promocao para Producao

```bash
# Apos validacao em homologacao
git checkout prd
git pull origin prd
gh pr create --base prd --head hm --title "release: v1.0.0"
```

### 3. Hotfix em Producao

```bash
# Criar hotfix a partir de prd
git checkout prd
git checkout -b hotfix/fix-critical-bug

# Corrigir e commitar
git commit -m "fix: corrigir bug critico"

# PR para prd
gh pr create --base prd --title "hotfix: corrigir bug critico"

# Apos merge em prd, fazer backport para hm
git checkout hm
git cherry-pick <commit-hash>
git push origin hm
```

## Regras de Protecao

### Branch `prd`
- [ ] Requer pull request
- [ ] Requer pelo menos 1 aprovacao
- [ ] Requer status checks passando (CI/CD)
- [ ] Nao permitir push direto
- [ ] Nao permitir force push

### Branch `hm`
- [ ] Requer pull request
- [ ] Requer status checks passando
- [ ] Nao permitir push direto

## Nomenclatura de Commits

Seguir Conventional Commits:

```
tipo(escopo): descricao

Tipos:
- feat: nova funcionalidade
- fix: correcao de bug
- docs: documentacao
- style: formatacao
- refactor: refatoracao
- test: testes
- chore: manutencao
```

## Diagrama de Fluxo

```
            hotfix/xxx
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
   prd ◄────────────────  hm ◄─────┬─────┬─────┐
    │                     │        │     │     │
    │                     │      feat   fix   docs
    │                     │        │     │     │
    └─────────────────────┴────────┴─────┴─────┘
```

## Comandos Uteis

```bash
# Listar branches
git branch -a

# Atualizar hm local
git checkout hm && git pull origin hm

# Criar feature branch
git checkout -b feat/RAD-XXX/descricao hm

# Ver diferenca entre branches
git log hm..prd --oneline

# Verificar status do PR
gh pr status
```
