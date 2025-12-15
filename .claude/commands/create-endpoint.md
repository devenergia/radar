---
description: Cria um endpoint FastAPI completo com todas as camadas
argument-hint: [nome_endpoint] [metodo] [api]
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Criar Endpoint FastAPI

Crie um endpoint completo seguindo Clean Architecture para o projeto RADAR.

## Argumentos
- `$1` = nome do endpoint (ex: `get_interrupcoes_ativas`)
- `$2` = metodo HTTP (GET, POST, PUT, DELETE)
- `$3` = API (api_interrupcoes, api_demanda, etc)

## Arquivos a Criar

### 1. Schema Pydantic (Request/Response)
**Localizacao**: `backend/apps/$3/interfaces/schemas/$1_schema.py`

```python
from pydantic import BaseModel, Field


class $1Response(BaseModel):
    """Response schema para $1."""

    idcStatusRequisicao: int = Field(default=1)
    desStatusRequisicao: str = Field(default="Sucesso")
    dados: list[ItemSchema]

    class Config:
        from_attributes = True


class ItemSchema(BaseModel):
    """Schema de item individual."""

    id: int
    campo: str
```

### 2. Route/Controller
**Localizacao**: `backend/apps/$3/interfaces/routes/$1_route.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas.$1_schema import $1Response
from ...application.use_cases.$1_use_case import $1UseCase
from ...dependencies import get_$1_use_case, verify_api_key

router = APIRouter()


@router.$2(
    "/$1",
    response_model=$1Response,
    status_code=status.HTTP_200_OK,
    summary="Descricao do endpoint",
    tags=["$3"],
)
async def $1(
    use_case: $1UseCase = Depends(get_$1_use_case),
    api_key: str = Depends(verify_api_key),
) -> $1Response:
    """
    Endpoint para [descricao].

    - **Autenticacao**: Requer x-api-key header
    - **Retorno**: Lista de [itens]
    """
    result = await use_case.execute()

    if result.is_failure:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.error,
        )

    return $1Response.from_entities(result.value)
```

### 3. Use Case
**Localizacao**: `backend/apps/$3/application/use_cases/$1_use_case.py`

(Siga o padrao do comando /create-usecase)

### 4. Dependency Injection
**Adicionar em**: `backend/apps/$3/dependencies.py`

```python
async def get_$1_use_case(
    repository: SomeRepository = Depends(get_repository),
    cache: CacheService = Depends(get_cache),
) -> $1UseCase:
    return $1UseCase(repository, cache)
```

### 5. Registrar Router
**Adicionar em**: `backend/apps/$3/main.py`

```python
from .interfaces.routes.$1_route import router as $1_router

app.include_router($1_router, prefix="/api/v1")
```

### 6. Teste E2E
**Localizacao**: `backend/tests/e2e/api/test_$1.py`

```python
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.e2e
class Test$1:
    async def test_deve_retornar_200_com_api_key_valida(
        self,
        client: AsyncClient,
        api_key: str,
    ):
        response = await client.$2(
            "/$1",
            headers={"x-api-key": api_key},
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["idcStatusRequisicao"] == 1

    async def test_deve_retornar_401_sem_api_key(
        self,
        client: AsyncClient,
    ):
        response = await client.$2("/$1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

## Padrao de Resposta ANEEL

Para endpoints ANEEL, use o formato padrao:

```python
{
    "idcStatusRequisicao": 1,
    "desStatusRequisicao": "Sucesso",
    "listaAlgo": [...]
}
```

## Referencias
- @docs/development/01-clean-architecture.md
- @.claude/rules/python-fastapi.md
