---
paths: backend/**/*.py
---

# Clean Architecture Rules

## Regra de Dependencia

A dependencia SEMPRE aponta para dentro (camadas internas):

```
interfaces -> application -> domain <- infrastructure
```

## Validacoes Obrigatorias

### Domain Layer (`backend/**/domain/**`)
- NAO pode importar de `application`, `infrastructure`, ou `interfaces`
- Contem: Entities, Value Objects, Domain Services, Repository Protocols
- Use `from typing import Protocol` para interfaces

### Application Layer (`backend/**/application/**`)
- NAO pode importar de `infrastructure` ou `interfaces`
- PODE importar de `domain`
- Contem: Use Cases, DTOs de aplicacao

### Infrastructure Layer (`backend/**/infrastructure/**`)
- PODE importar de `domain` e `application`
- NAO pode importar de `interfaces`
- Contem: Implementacoes de Repository, Cache, External Services

### Interfaces Layer (`backend/**/interfaces/**` ou `backend/**/routes/**`)
- PODE importar de todas as camadas
- Contem: HTTP Routes, Controllers, Request/Response schemas

## Exemplos de Import Correto

```python
# Em domain/repositories/interrupcao_repository.py
from typing import Protocol
from ..entities.interrupcao import Interrupcao  # OK: mesmo layer

# Em application/use_cases/get_interrupcoes.py
from shared.domain.entities.interrupcao import Interrupcao  # OK: domain
from shared.domain.repositories.interrupcao_repository import InterrupcaoRepository  # OK

# Em infrastructure/repositories/oracle_interrupcao_repository.py
from shared.domain.entities.interrupcao import Interrupcao  # OK
from shared.domain.repositories.interrupcao_repository import InterrupcaoRepository  # OK
```

## Exemplos de Import INCORRETO (NUNCA faca)

```python
# ERRADO em domain/
from infrastructure.database import Session  # VIOLACAO!
from fastapi import Depends  # VIOLACAO! FastAPI e framework

# ERRADO em application/
from infrastructure.cache import RedisCache  # VIOLACAO!
```

## Dependency Injection

Use FastAPI `Depends()` apenas na camada de interfaces:

```python
# interfaces/routes/interrupcoes.py
from fastapi import APIRouter, Depends
from application.use_cases.get_interrupcoes import GetInterrupcoesUseCase

router = APIRouter()

@router.get("/interrupcoes")
async def get_interrupcoes(
    use_case: GetInterrupcoesUseCase = Depends(get_use_case)
):
    return await use_case.execute()
```
