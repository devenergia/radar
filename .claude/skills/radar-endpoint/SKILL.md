---
name: radar-endpoint
description: Cria endpoints FastAPI completos para o projeto RADAR. Use quando o usuario pedir para criar uma rota, endpoint, API, controller, ou implementar um servico HTTP REST com autenticacao, validacao Pydantic, e formato de resposta ANEEL.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Criacao de Endpoints FastAPI - Projeto RADAR

## Quando Usar

Esta skill e ativada automaticamente quando:
- Usuario pede para criar um "endpoint" ou "rota"
- Usuario quer implementar uma API REST
- Menciona FastAPI, HTTP, GET, POST
- Precisa de validacao de request/response

## Arquivos a Criar

### 1. Schema Pydantic

**Localizacao**: `backend/apps/<api>/interfaces/schemas/<nome>_schema.py`

```python
from pydantic import BaseModel, Field


class InterrupcaoItemSchema(BaseModel):
    """Schema de item individual de interrupcao."""

    ideConjuntoUnidadeConsumidora: int = Field(
        ...,
        description="Identificador do conjunto",
    )
    ideMunicipio: str = Field(
        ...,
        pattern=r"^\d{7}$",
        description="Codigo IBGE do municipio",
    )
    qtdUCsAtendidas: int = Field(
        ...,
        ge=0,
        description="Quantidade de UCs atendidas",
    )
    qtdOcorrenciaProgramada: int = Field(
        ...,
        ge=0,
        description="UCs com interrupcao programada",
    )
    qtdOcorrenciaNaoProgramada: int = Field(
        ...,
        ge=0,
        description="UCs com interrupcao nao programada",
    )

    class Config:
        from_attributes = True


class InterrupcoesResponse(BaseModel):
    """Response padrao ANEEL para interrupcoes."""

    idcStatusRequisicao: int = Field(
        default=1,
        description="1 = Sucesso, 0 = Erro",
    )
    desStatusRequisicao: str = Field(
        default="Sucesso",
        description="Descricao do status",
    )
    listaInterrupcoes: list[InterrupcaoItemSchema] = Field(
        default_factory=list,
        description="Lista de interrupcoes agregadas",
    )

    @classmethod
    def from_entities(
        cls,
        agregadas: list,
    ) -> "InterrupcoesResponse":
        """Converte entities para response."""
        return cls(
            listaInterrupcoes=[
                InterrupcaoItemSchema(
                    ideConjuntoUnidadeConsumidora=a.id_conjunto,
                    ideMunicipio=a.municipio.valor,
                    qtdUCsAtendidas=a.qtd_ucs_atendidas,
                    qtdOcorrenciaProgramada=a.qtd_programada,
                    qtdOcorrenciaNaoProgramada=a.qtd_nao_programada,
                )
                for a in agregadas
            ]
        )

    @classmethod
    def error(cls, message: str) -> "InterrupcoesResponse":
        """Cria response de erro."""
        return cls(
            idcStatusRequisicao=0,
            desStatusRequisicao=message,
            listaInterrupcoes=[],
        )
```

### 2. Route/Controller

**Localizacao**: `backend/apps/<api>/interfaces/routes/<nome>_route.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
import structlog

from ..schemas.interrupcoes_schema import InterrupcoesResponse
from ...application.use_cases.get_interrupcoes_ativas import GetInterrupcoesAtivasUseCase
from ...dependencies import get_interrupcoes_use_case, verify_api_key

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["interrupcoes"])


@router.get(
    "/quantitativointerrupcoesativas",
    response_model=InterrupcoesResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista interrupcoes ativas agregadas",
    description="""
    Retorna o quantitativo de interrupcoes ativas agregadas por
    municipio e conjunto eletrico, no formato padrao ANEEL.

    **Autenticacao**: Requer header `x-api-key`
    """,
    responses={
        200: {"description": "Lista de interrupcoes"},
        401: {"description": "API key invalida ou ausente"},
        500: {"description": "Erro interno do servidor"},
    },
)
async def get_quantitativo_interrupcoes_ativas(
    use_case: GetInterrupcoesAtivasUseCase = Depends(get_interrupcoes_use_case),
    api_key: str = Depends(verify_api_key),
) -> InterrupcoesResponse:
    """
    Endpoint para quantitativo de interrupcoes ativas.

    Retorna dados agregados por municipio e conjunto,
    separando interrupcoes programadas e nao programadas.
    """
    logger.info("requisicao_interrupcoes_ativas")

    result = await use_case.execute()

    if result.is_failure:
        logger.error("erro_interrupcoes", error=result.error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.error,
        )

    logger.info(
        "interrupcoes_retornadas",
        quantidade=len(result.value),
    )

    return InterrupcoesResponse.from_entities(result.value)
```

### 3. Autenticacao

**Localizacao**: `backend/apps/<api>/dependencies.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from .config import get_settings, Settings

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Depends(api_key_header),
    settings: Settings = Depends(get_settings),
) -> str:
    """Verifica se a API key e valida."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key ausente",
        )

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key invalida",
        )

    return api_key
```

### 4. Registrar Router

**Adicionar em**: `backend/apps/<api>/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .interfaces.routes.interrupcoes_route import router as interrupcoes_router
from .exception_handlers import register_exception_handlers

def create_app() -> FastAPI:
    app = FastAPI(
        title="API Interrupcoes - Projeto RADAR",
        description="API de monitoramento de interrupcoes ANEEL",
        version="1.0.0",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    register_exception_handlers(app)

    # Routes
    app.include_router(interrupcoes_router, prefix="/api/v1")

    return app
```

### 5. Exception Handlers

**Localizacao**: `backend/apps/<api>/exception_handlers.py`

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from shared.domain.errors import DomainError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=400,
            content={
                "idcStatusRequisicao": 0,
                "desStatusRequisicao": exc.message,
                "codigo": exc.code,
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "idcStatusRequisicao": 0,
                "desStatusRequisicao": "Erro interno do servidor",
            },
        )
```

## Formato de Resposta ANEEL

Todos os endpoints devem seguir o padrao:

```json
{
    "idcStatusRequisicao": 1,
    "desStatusRequisicao": "Sucesso",
    "listaAlgo": [...]
}
```

Para erros:
```json
{
    "idcStatusRequisicao": 0,
    "desStatusRequisicao": "Descricao do erro"
}
```

## Teste E2E

**Localizacao**: `backend/tests/e2e/api/test_<nome>.py`

```python
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.e2e
class TestNomeEndpoint:
    async def test_deve_retornar_200_com_api_key_valida(
        self,
        client: AsyncClient,
        api_key: str,
    ):
        response = await client.get(
            "/api/v1/endpoint",
            headers={"x-api-key": api_key},
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["idcStatusRequisicao"] == 1

    async def test_deve_retornar_401_sem_api_key(
        self,
        client: AsyncClient,
    ):
        response = await client.get("/api/v1/endpoint")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

## Checklist

- [ ] Schema Pydantic com validacoes
- [ ] Route com decorators completos
- [ ] Autenticacao via API key
- [ ] Logging estruturado
- [ ] Exception handlers
- [ ] Teste E2E
- [ ] Documentacao OpenAPI (summary, description)
