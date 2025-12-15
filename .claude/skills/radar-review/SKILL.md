---
name: radar-review
description: Revisa codigo contra os padroes do projeto RADAR. Use quando o usuario pedir para revisar codigo, fazer code review, verificar qualidade, validar arquitetura, ou checar se o codigo segue Clean Architecture, SOLID, DDD, TDD, ou Clean Code.
allowed-tools: Read, Glob, Grep, Bash
---

# Code Review - Projeto RADAR

## Quando Usar

Esta skill e ativada automaticamente quando:
- Usuario pede para "revisar" ou "review" codigo
- Usuario quer verificar qualidade do codigo
- Menciona "validar arquitetura" ou "checar padroes"
- Pede para verificar SOLID, Clean Code, DDD, TDD

## Checklist Completo de Review

### 1. Clean Architecture

#### Verificacoes
- [ ] Estrutura de camadas correta (domain > application > infrastructure > interfaces)
- [ ] Regra de dependencia respeitada (camadas internas nao importam externas)
- [ ] Dependency Injection usado corretamente

#### Comandos de Verificacao
```bash
# Imports proibidos em domain
grep -r "from.*infrastructure" backend/shared/domain/
grep -r "from fastapi" backend/shared/domain/
grep -r "from sqlalchemy" backend/shared/domain/

# Imports proibidos em application
grep -r "from.*infrastructure" backend/apps/*/application/
```

#### Violacoes Comuns
```python
# ERRADO em domain/
from infrastructure.database import Session  # VIOLACAO!
from fastapi import Depends  # VIOLACAO!

# ERRADO em application/
from infrastructure.cache import RedisCache  # VIOLACAO!
```

### 2. SOLID Principles

#### S - Single Responsibility
- [ ] Classe tem apenas UMA razao para mudar?
- [ ] Nome descreve claramente a responsabilidade?
- [ ] Menos de 200 linhas?

#### O - Open/Closed
- [ ] Pode ser estendido sem modificacao?
- [ ] Usa Protocol para interfaces?

#### L - Liskov Substitution
- [ ] Implementacoes respeitam contratos?
- [ ] Sem excecoes inesperadas?

#### I - Interface Segregation
- [ ] Protocols sao pequenos (< 7 metodos)?
- [ ] Clientes usam todos os metodos?

#### D - Dependency Inversion
- [ ] Depende de Protocols, nao implementacoes?
- [ ] Dependencias injetadas via construtor?

### 3. DDD (Domain-Driven Design)

#### Value Objects
- [ ] Usa `@dataclass(frozen=True)`?
- [ ] Validacao no `__post_init__`?
- [ ] Factory method `create()` retorna `Result`?

#### Entities
- [ ] `__eq__` e `__hash__` por ID?
- [ ] Atributos privados com `_`?
- [ ] Metodos de comportamento de negocio?

#### Repositories
- [ ] Protocol no dominio?
- [ ] Implementacao na infraestrutura?
- [ ] Retorna entidades (nao dicts)?

### 4. TDD (Test-Driven Development)

- [ ] Teste existe para o codigo?
- [ ] Cobertura >= 80%?
- [ ] Padrao AAA (Arrange-Act-Assert)?
- [ ] Nomenclatura: `test_deve_<comportamento>_quando_<condicao>`?

#### Verificar Cobertura
```bash
pytest --cov=backend --cov-report=term-missing
```

### 5. Clean Code

#### Nomes
- [ ] Nomes revelam intencao?
- [ ] Pronunciaveis e pesquisaveis?
- [ ] Classes = substantivos, Metodos = verbos?

#### Funcoes
- [ ] Pequenas (< 20 linhas)?
- [ ] Fazem apenas UMA coisa?
- [ ] Poucos argumentos (< 3)?

#### Comentarios
- [ ] Codigo se auto-documenta?
- [ ] Sem comentarios obvios ou desatualizados?

#### Formatacao
- [ ] Linhas < 100 caracteres?
- [ ] Agrupamento logico?

### 6. Python/FastAPI

#### Type Hints
- [ ] Todas as funcoes tem type hints?
- [ ] Retorno especificado?

#### Async
- [ ] Operacoes I/O sao async?
- [ ] Nao mistura sync e async?

#### Verificar com Ferramentas
```bash
# Lint
ruff check backend/

# Type check
mypy backend/

# Format
ruff format --check backend/
```

## Formato do Output

```markdown
## Code Review: [caminho/arquivo.py]

### Resumo

| Criterio | Status | Observacao |
|----------|--------|------------|
| Clean Architecture | OK/FALHA | ... |
| SOLID | OK/FALHA | ... |
| DDD | OK/FALHA/N/A | ... |
| TDD | OK/FALHA | ... |
| Clean Code | OK/FALHA | ... |
| Python/FastAPI | OK/FALHA | ... |

### Problemas Encontrados

#### Alta Severidade
1. **[Linha X]** Descricao do problema
   - Impacto: ...
   - Correcao: ...

#### Media Severidade
1. ...

#### Baixa Severidade
1. ...

### Pontos Positivos
- ...

### Sugestoes de Melhoria
1. ...

### Veredicto

- [ ] APROVADO - Codigo pode ser mergeado
- [ ] APROVADO COM RESSALVAS - Pequenos ajustes necessarios
- [ ] REPROVADO - Correcoes obrigatorias antes de merge
```

## Exemplos de Problemas Comuns

### Violacao de Clean Architecture
```python
# Em domain/entities/interrupcao.py
from sqlalchemy import Column  # PROBLEMA: Import de infra em domain
```

### Violacao de SRP
```python
class InterrupcaoService:
    async def buscar(self): ...
    async def salvar(self): ...
    async def enviar_email(self): ...  # PROBLEMA: Responsabilidade diferente
    async def gerar_relatorio(self): ...  # PROBLEMA: Outra responsabilidade
```

### Value Object Mutavel
```python
@dataclass  # PROBLEMA: Falta frozen=True
class CodigoIBGE:
    valor: str
```

### Falta de Type Hints
```python
def processar(dados):  # PROBLEMA: Sem type hints
    return dados
```

## Comandos Uteis para Review

```bash
# Verificar arquitetura
grep -r "from.*infrastructure" backend/shared/domain/

# Verificar testes
pytest --cov=backend --cov-fail-under=80

# Verificar lint
ruff check backend/

# Verificar tipos
mypy backend/

# Verificar formatacao
ruff format --check backend/
```
