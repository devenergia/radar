# ADR-004: FastAPI como Framework HTTP

## Status

Aceito

## Data

2025-12-12 (Atualizado: 2025-12-15)

## Contexto

Precisamos de um framework HTTP para expor a API REST do RADAR. Requisitos:

1. Alta performance (tempo de resposta < 5 segundos exigido pela ANEEL)
2. Validacao automatica de entrada/saida
3. Geracao automatica de OpenAPI/Swagger
4. Suporte nativo a async/await
5. Injecao de dependencias integrada
6. Comunidade ativa e manutencao continua

## Decisao

Utilizaremos **FastAPI** como framework HTTP principal.

### Versao

- FastAPI: ^0.109.0
- Uvicorn: ^0.27.0 (ASGI server)
- Pydantic: ^2.5.0 (validacao)

### Dependencias Principais

```python
# pyproject.toml
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
    "structlog>=24.1.0",
    "httpx>=0.26.0",
]
```

### Estrutura de Aplicacao

```python
# Organizacao das rotas e middlewares
backend/
├── apps/
│   └── api_interrupcoes/
│       ├── main.py           # App factory
│       ├── routes.py         # Endpoints
│       ├── schemas.py        # Pydantic models
│       ├── dependencies.py   # Injecao de dependencias
│       ├── middleware.py     # Error handler, logging
│       └── use_cases/        # Logica de aplicacao
```

### Exemplo de Implementacao

```python
from fastapi import FastAPI, Depends, Query, Header
from pydantic import BaseModel, Field

app = FastAPI(
    title="RADAR API - Interrupcoes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

class InterrupcaoResponse(BaseModel):
    """Schema de resposta conforme padrao ANEEL."""

    idcStatusRequisicao: int = Field(ge=1, le=2)
    desStatusRequisicao: str
    emailIndisponibilidade: str
    mensagem: str
    listaInterrupcoes: list[InterrupcaoItem]

    model_config = {"populate_by_name": True}


@app.get(
    "/quantitativointerrupcoesativas",
    response_model=InterrupcaoResponse,
    summary="Consulta interrupcoes ativas",
    tags=["Interrupcoes"],
)
async def get_interrupcoes(
    dthRecuperacao: str = Query(
        ...,
        pattern=r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$",
        description="Data/hora no formato DD/MM/YYYY HH:MM",
    ),
    x_api_key: str = Header(..., alias="x-api-key"),
    use_case: GetInterrupcoesUseCase = Depends(get_use_case),
) -> InterrupcaoResponse:
    """Retorna o quantitativo de interrupcoes ativas."""
    result = await use_case.execute(dthRecuperacao)
    return result.to_response()
```

### Injecao de Dependencias

```python
from fastapi import Depends
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()

def get_repository(
    settings: Settings = Depends(get_settings),
) -> InterrupcaoRepository:
    return OracleInterrupcaoRepository(settings.db_connection_string)

def get_use_case(
    repository: InterrupcaoRepository = Depends(get_repository),
) -> GetInterrupcoesUseCase:
    return GetInterrupcoesUseCase(repository)
```

## Consequencias

### Positivas

- **Performance**: Um dos frameworks Python mais rapidos (Starlette + Uvicorn)
- **Validacao**: Pydantic valida entrada/saida automaticamente
- **OpenAPI**: Documentacao Swagger/ReDoc gerada automaticamente
- **Async**: Suporte nativo a async/await para alta concorrencia
- **Type Hints**: Validacao baseada em type hints do Python
- **DI**: Sistema de injecao de dependencias integrado
- **Testabilidade**: Facil de testar com TestClient e pytest

### Negativas

- **Ecossistema Menor**: Menos plugins que Django/Flask
- **Pydantic v2**: Migracao de v1 para v2 pode ser complexa
- **ASGI Only**: Requer servidor ASGI (Uvicorn, Hypercorn)

### Neutras

- Curva de aprendizado para Pydantic e async/await
- Necessidade de entender o ciclo de vida de dependencias

## Alternativas Consideradas

### Alternativa 1: Django REST Framework

Framework full-stack com ORM integrado.

**Rejeitado porque**: Overhead desnecessario, nao e async nativo, mais lento para APIs simples.

### Alternativa 2: Flask

Microframework leve e flexivel.

**Rejeitado porque**: Sem validacao integrada, sem suporte async nativo, requer muitas extensoes.

### Alternativa 3: Starlette

Framework ASGI minimalista (base do FastAPI).

**Rejeitado porque**: Muito baixo nivel, requer implementar validacao manualmente, sem geracao de OpenAPI.

### Alternativa 4: aiohttp

Framework async para HTTP client/server.

**Rejeitado porque**: API menos intuitiva, sem validacao integrada, ecossistema menor.

## Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn ASGI Server](https://www.uvicorn.org/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
