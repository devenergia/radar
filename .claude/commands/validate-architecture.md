---
description: Valida a arquitetura do projeto contra Clean Architecture
allowed-tools: Read, Glob, Grep, Bash
---

# Validar Clean Architecture

Execute uma validacao completa da arquitetura do projeto RADAR.

## Verificacoes a Executar

### 1. Estrutura de Diretorios
Verifique se a estrutura segue o padrao:
```
backend/
├── apps/
│   └── <api>/
│       ├── application/      # Use Cases
│       ├── infrastructure/   # Implementacoes
│       └── interfaces/       # Routes, Controllers
└── shared/
    └── domain/              # Entities, Value Objects, Protocols
```

### 2. Regra de Dependencia

Verifique que NAO existem imports proibidos:

```python
# Em domain/ - NAO pode importar de:
from infrastructure import ...  # PROIBIDO
from application import ...     # PROIBIDO
from interfaces import ...      # PROIBIDO
from fastapi import ...         # PROIBIDO
from sqlalchemy import ...      # PROIBIDO

# Em application/ - NAO pode importar de:
from infrastructure import ...  # PROIBIDO
from interfaces import ...      # PROIBIDO
```

### 3. Comandos de Verificacao

Execute os seguintes comandos para detectar violacoes:

```bash
# Verificar imports de infrastructure em domain
grep -r "from.*infrastructure" backend/shared/domain/ || echo "OK: Nenhum import de infrastructure em domain"

# Verificar imports de FastAPI em domain
grep -r "from fastapi" backend/shared/domain/ || echo "OK: Nenhum import de FastAPI em domain"

# Verificar imports de SQLAlchemy em domain
grep -r "from sqlalchemy" backend/shared/domain/ || echo "OK: Nenhum import de SQLAlchemy em domain"

# Verificar imports de infrastructure em application
grep -r "from.*infrastructure" backend/apps/*/application/ || echo "OK: Nenhum import de infrastructure em application"
```

### 4. Verificar Protocols

Verifique que interfaces estao definidas como Protocol no dominio:

```bash
# Listar todos os Protocols
grep -r "class.*Protocol" backend/shared/domain/
```

### 5. Verificar Dependency Injection

Verifique que Use Cases recebem dependencias via construtor:

```bash
# Verificar __init__ dos Use Cases
grep -A 10 "def __init__" backend/apps/*/application/use_cases/*.py
```

## Formato do Output

```markdown
## Validacao de Arquitetura - RADAR

### Resumo

| Verificacao | Status | Detalhes |
|-------------|--------|----------|
| Estrutura de Diretorios | OK/FALHA | ... |
| Regra de Dependencia (domain) | OK/FALHA | ... |
| Regra de Dependencia (application) | OK/FALHA | ... |
| Protocols no Dominio | OK/FALHA | ... |
| Dependency Injection | OK/FALHA | ... |

### Violacoes Encontradas

1. **Arquivo**: `caminho/arquivo.py`
   - **Linha**: X
   - **Violacao**: Import de infrastructure em domain
   - **Correcao**: Mover implementacao para infrastructure

### Recomendacoes

1. ...

### Veredicto

[ ] ARQUITETURA VALIDA
[ ] ARQUITETURA COM VIOLACOES - Correcoes necessarias
```

## Referencias
- @docs/development/01-clean-architecture.md
- @.claude/rules/clean-architecture.md
