"""Camada de dominio - Entidades, Value Objects e Regras de Negocio."""

from backend.shared.domain.result import Result
from backend.shared.domain.value_objects.codigo_ibge import CodigoIBGE
from backend.shared.domain.value_objects.tipo_interrupcao import TipoInterrupcao
from backend.shared.domain.entities.interrupcao import Interrupcao
from backend.shared.domain.errors import (
    DomainError,
    ValidationError,
    DatabaseConnectionError,
    DatabaseQueryError,
    EntityNotFoundError,
    UnauthorizedError,
)

__all__ = [
    "Result",
    "CodigoIBGE",
    "TipoInterrupcao",
    "Interrupcao",
    "DomainError",
    "ValidationError",
    "DatabaseConnectionError",
    "DatabaseQueryError",
    "EntityNotFoundError",
    "UnauthorizedError",
]
