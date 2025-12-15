# ADR-010: Tratamento de Erros

## Status

Aceito

## Data

2025-12-12

## Contexto

A API RADAR precisa de uma estratégia consistente de tratamento de erros que:

1. Retorne o formato de erro especificado pela ANEEL
2. Não exponha detalhes técnicos sensíveis
3. Facilite debugging e logging
4. Seja consistente em toda a aplicação

## Decisão

### Hierarquia de Erros de Domínio

```python
# app/shared/errors/domain_errors.py

from abc import ABC
from typing import Optional

class DomainError(Exception, ABC):
    """Erro base de domínio"""
    code: str = "DOMAIN_ERROR"
    status_code: int = 500
    is_operational: bool = True

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# Erros de Negócio (esperados, operacionais)
class ValidationError(DomainError):
    """Erro de validação de dados"""
    code = "VALIDATION_ERROR"
    status_code = 400


class NotFoundError(DomainError):
    """Recurso não encontrado"""
    code = "NOT_FOUND"
    status_code = 404


class UnauthorizedError(DomainError):
    """Não autenticado"""
    code = "UNAUTHORIZED"
    status_code = 401


class ForbiddenError(DomainError):
    """Sem permissão"""
    code = "FORBIDDEN"
    status_code = 403


# Erros de Infraestrutura
class DatabaseError(DomainError):
    """Erro de banco de dados"""
    code = "DATABASE_ERROR"
    status_code = 500

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class ExternalServiceError(DomainError):
    """Erro em serviço externo"""
    code = "EXTERNAL_SERVICE_ERROR"
    status_code = 502
```

### Error Handler Global

```python
# app/infrastructure/http/middlewares/error_handler.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.shared.errors.domain_errors import DomainError
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Handler para erros de domínio"""

    # Log do erro com contexto
    logger.error(
        "domain_error",
        error_code=exc.code,
        error_message=exc.message,
        url=str(request.url),
        method=request.method,
    )

    # Retornar resposta no formato ANEEL
    return JSONResponse(
        status_code=status.HTTP_200_OK,  # ANEEL sempre espera 200
        content={
            "idcStatusRequisicao": 2,
            "emailIndisponibilidade": settings.EMAIL_INDISPONIBILIDADE,
            "mensagem": exc.message,
            "interrupcaoFornecimento": []
        }
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handler para erros de validação do FastAPI/Pydantic"""

    # Extrair primeiro erro de validação
    error_msg = "Erro de validação"
    if exc.errors():
        first_error = exc.errors()[0]
        field = " -> ".join(str(loc) for loc in first_error["loc"])
        error_msg = f"Erro de validação no campo '{field}': {first_error['msg']}"

    logger.warning(
        "validation_error",
        error_message=error_msg,
        errors=exc.errors(),
        url=str(request.url),
        method=request.method,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "idcStatusRequisicao": 2,
            "emailIndisponibilidade": settings.EMAIL_INDISPONIBILIDADE,
            "mensagem": error_msg,
            "interrupcaoFornecimento": []
        }
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler para erros não esperados"""

    # Log completo do erro com stack trace
    logger.exception(
        "unexpected_error",
        error_type=type(exc).__name__,
        error_message=str(exc),
        url=str(request.url),
        method=request.method,
    )

    # Não expor detalhes técnicos ao cliente
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "idcStatusRequisicao": 2,
            "emailIndisponibilidade": settings.EMAIL_INDISPONIBILIDADE,
            "mensagem": "Erro interno do servidor. Tente novamente mais tarde.",
            "interrupcaoFornecimento": []
        }
    )
```

### Registro dos Handlers

```python
# app/main.py

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.shared.errors.domain_errors import DomainError
from app.infrastructure.http.middlewares.error_handler import (
    domain_error_handler,
    validation_error_handler,
    generic_error_handler
)

app = FastAPI()

# Registrar exception handlers
app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, generic_error_handler)
```

### Padrão de Resposta de Erro (ANEEL)

**Importante**: A ANEEL espera HTTP 200 OK mesmo em erros, com o status no campo `idcStatusRequisicao`.

```json
{
  "idcStatusRequisicao": 2,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "Erro de conexão com banco de dados",
  "interrupcaoFornecimento": []
}
```

### Exceções ao Padrão (HTTP Status Codes)

Apenas para erros de autenticação/autorização usamos HTTP status diferente de 200:

| Cenário | HTTP Status | idcStatusRequisicao |
|---------|-------------|---------------------|
| Sucesso | 200 | 1 |
| Erro de negócio | 200 | 2 |
| Erro de banco | 200 | 2 |
| API Key ausente | 401 | 2 |
| API Key inválida | 401 | 2 |
| IP não autorizado | 403 | 2 |

### Tratamento em Use Cases

```python
# app/application/use_cases/get_interrupcoes_ativas.py

from typing import List
from app.domain.entities import InterrupcaoAgregada
from app.domain.repositories import InterrupcaoRepository
from app.shared.errors.domain_errors import DatabaseError
from app.core.logging import get_logger
import oracledb

logger = get_logger(__name__)

class GetInterrupcoesAtivasUseCase:
    """Caso de uso para buscar interrupções ativas"""

    def __init__(self, repository: InterrupcaoRepository):
        self.repository = repository

    async def execute(self, params: dict) -> List[InterrupcaoAgregada]:
        """Executa o caso de uso"""
        try:
            logger.debug("Buscando interrupções ativas", params=params)
            interrupcoes = await self.repository.find_ativas(params)
            logger.info("Interrupções encontradas", count=len(interrupcoes))
            return interrupcoes

        except oracledb.DatabaseError as e:
            # Transformar erro de infraestrutura em erro de domínio
            logger.error(
                "Erro ao consultar banco de dados",
                error=str(e),
                error_code=e.args[0].code if e.args else None
            )
            raise DatabaseError(
                "Erro ao consultar interrupções ativas",
                original_error=e
            )
        except Exception as e:
            logger.exception("Erro inesperado no use case")
            raise
```

### Result Pattern (Opcional)

Para fluxos que preferem não usar exceções:

```python
# app/shared/utils/result.py

from typing import TypeVar, Generic, Optional
from dataclasses import dataclass
from app.shared.errors.domain_errors import DomainError

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    """
    Pattern Result para representar sucesso ou falha
    sem usar exceções
    """
    is_success: bool
    value: Optional[T] = None
    error: Optional[DomainError] = None

    @staticmethod
    def ok(value: T) -> "Result[T]":
        """Cria um resultado de sucesso"""
        return Result(is_success=True, value=value)

    @staticmethod
    def fail(error: DomainError) -> "Result[T]":
        """Cria um resultado de falha"""
        return Result(is_success=False, error=error)

    def get_or_raise(self) -> T:
        """Retorna o valor ou levanta a exceção"""
        if not self.is_success:
            raise self.error
        return self.value


# Exemplo de uso
async def get_data() -> Result[list]:
    try:
        data = await fetch_data()
        return Result.ok(data)
    except DatabaseError as e:
        return Result.fail(e)
```

### Tratamento em Controllers

```python
# app/infrastructure/http/controllers/interrupcao_controller.py

from fastapi import APIRouter, Depends
from app.application.use_cases import GetInterrupcoesAtivasUseCase
from app.domain.schemas.interrupcao import InterrupcoesAtivasResponse
from app.application.mappers import ResponseMapper
from app.core.config import settings

router = APIRouter()

@router.get(
    "/quantitativointerrupcoesativas",
    response_model=InterrupcoesAtivasResponse,
    response_model_by_alias=True
)
async def get_interrupcoes_ativas(
    use_case: GetInterrupcoesAtivasUseCase = Depends()
):
    """
    Endpoint para buscar interrupções ativas.

    Erros são tratados pelo error handler global,
    então não precisamos de try/except aqui.
    """
    interrupcoes = await use_case.execute({})

    return ResponseMapper.to_interrupcoes_ativas_response(
        interrupcoes,
        settings.EMAIL_INDISPONIBILIDADE
    )
```

## Consequências

### Positivas

- **Consistência**: Todos os erros seguem mesmo formato
- **Segurança**: Detalhes técnicos não vazam para clientes
- **Debugging**: Stack traces completos nos logs
- **Conformidade ANEEL**: Formato de erro esperado
- **Manutenibilidade**: Tratamento centralizado de erros
- **Type Safety**: Erros tipados com hierarquia clara

### Negativas

- **Verbosidade**: Mais código para tratar erros
- **Confusão HTTP**: 200 OK mesmo em erros pode confundir
- **Curva de Aprendizado**: Desenvolvedores precisam conhecer hierarquia de erros

### Neutras

- Necessidade de mapear erros de bibliotecas externas
- Testes devem cobrir cenários de erro

## Exemplo de Teste

```python
# tests/unit/test_error_handling.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.shared.errors.domain_errors import DatabaseError

client = TestClient(app)

def test_database_error_returns_aneel_format(mocker):
    """Testa que erro de banco retorna formato ANEEL"""
    # Arrange
    mocker.patch(
        "app.application.use_cases.GetInterrupcoesAtivasUseCase.execute",
        side_effect=DatabaseError("Conexão falhou")
    )

    # Act
    response = client.get("/quantitativointerrupcoesativas")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["idcStatusRequisicao"] == 2
    assert "mensagem" in data
    assert "interrupcaoFornecimento" in data
    assert data["interrupcaoFornecimento"] == []


def test_validation_error_returns_aneel_format():
    """Testa que erro de validação retorna formato ANEEL"""
    # Act
    response = client.get(
        "/quantitativointerrupcoesativas?invalid_param=abc"
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["idcStatusRequisicao"] == 2
```

## Referências

- ANEEL Ofício Circular 14/2025 - Seção de Erros
- [FastAPI Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Error Handling Best Practices](https://www.joyent.com/node-js/production/design/errors)
