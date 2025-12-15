---
paths: backend/**/*.py
---

# Python & FastAPI Rules

## Type Hints

### Obrigatorio
- TODAS as funcoes devem ter type hints
- Use `-> None` para funcoes que nao retornam
- Use `| None` ao inves de `Optional`

```python
# CORRETO
async def buscar_ativas(self) -> list[Interrupcao]:
    ...

def processar(dados: list[dict]) -> Result[list[InterrupcaoAgregada]]:
    ...

# INCORRETO
def buscar_ativas(self):  # Falta type hint
    ...
```

## Async/Await

### Regras
- Use `async def` para operacoes I/O
- Repositories sao SEMPRE async
- Use Cases sao SEMPRE async
- NAO misture sync e async

```python
# CORRETO
async def buscar_ativas(self) -> list[Interrupcao]:
    result = await self._session.execute(text(query))
    return self._map(result.fetchall())

# INCORRETO - Sync em contexto async
def buscar_ativas(self) -> list[Interrupcao]:
    result = self._session.execute(text(query))  # Blocking!
```

## Pydantic Schemas

### Request/Response
```python
from pydantic import BaseModel, Field

class InterrupcaoResponse(BaseModel):
    id: int
    tipo: str
    municipio: str = Field(..., pattern=r"^\d{7}$")

    class Config:
        from_attributes = True
```

### Validacao
```python
from pydantic import BaseModel, field_validator

class CodigoIBGERequest(BaseModel):
    codigo: str

    @field_validator("codigo")
    @classmethod
    def validate_codigo(cls, v: str) -> str:
        if len(v) != 7 or not v.isdigit():
            raise ValueError("Codigo deve ter 7 digitos")
        return v
```

## FastAPI Routes

### Estrutura
```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/api/v1", tags=["interrupcoes"])

@router.get(
    "/quantitativointerrupcoesativas",
    response_model=InterrupcoesResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista interrupcoes ativas agregadas",
)
async def get_interrupcoes_ativas(
    use_case: GetInterrupcoesUseCase = Depends(get_use_case),
    api_key: str = Depends(verify_api_key),
) -> InterrupcoesResponse:
    result = await use_case.execute()
    if result.is_failure:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.error,
        )
    return InterrupcoesResponse.from_entities(result.value)
```

## Dependency Injection

### Factory Functions
```python
from functools import lru_cache
from fastapi import Depends

@lru_cache
def get_settings() -> Settings:
    return Settings()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_repository(
    session: AsyncSession = Depends(get_session),
) -> OracleInterrupcaoRepository:
    return OracleInterrupcaoRepository(session)

async def get_use_case(
    repository: InterrupcaoRepository = Depends(get_repository),
    cache: CacheService = Depends(get_cache),
) -> GetInterrupcoesUseCase:
    return GetInterrupcoesUseCase(repository, cache)
```

## SQLAlchemy

### Queries Async
```python
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

class OracleInterrupcaoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def buscar_ativas(self) -> list[Interrupcao]:
        query = """
            SELECT ae.num_1, ae.NUM_CUST, spt.PLAN_ID
            FROM INSERVICE.AGENCY_EVENT@DBLINK_INSERVICE ae
            LEFT JOIN INSERVICE.SWITCH_PLAN_TASKS@DBLINK_INSERVICE spt
                ON spt.OUTAGE_NUM = ae.num_1
            WHERE ae.is_open = 'T'
        """
        result = await self._session.execute(text(query))
        return [self._map_to_entity(row) for row in result.fetchall()]
```

## Logging

### Use structlog
```python
import structlog

logger = structlog.get_logger(__name__)

async def execute(self) -> Result[list[InterrupcaoAgregada]]:
    logger.info("buscando_interrupcoes_ativas")
    try:
        dados = await self._repository.buscar_ativas()
        logger.info("interrupcoes_encontradas", quantidade=len(dados))
        return Result.ok(dados)
    except Exception as e:
        logger.error("erro_buscar_interrupcoes", error=str(e))
        return Result.fail(str(e))
```

## Exception Handlers

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

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
```

## Configuracao com Pydantic Settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    cache_ttl_seconds: int = 300
    debug: bool = False

    class Config:
        env_file = ".env"
        env_prefix = "RADAR_"
```
