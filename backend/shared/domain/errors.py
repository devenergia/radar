"""Erros de dominio."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class DomainError(Exception):
    """Classe base para todos os erros de dominio."""

    def __init__(
        self,
        message: str,
        code: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.context = context or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }


class ValidationError(DomainError):
    """Erro de validacao."""

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            context={"field": field} if field else None,
        )


class DatabaseConnectionError(DomainError):
    """Erro de conexao com banco de dados."""

    def __init__(
        self,
        original_error: Exception,
        database: str | None = None,
    ) -> None:
        super().__init__(
            message="Falha na conexao com banco de dados",
            code="DB_CONNECTION_ERROR",
            context={
                "original_message": str(original_error),
                "database": database,
            },
        )


class DatabaseQueryError(DomainError):
    """Erro de query no banco de dados."""

    def __init__(
        self,
        original_error: Exception,
        query: str | None = None,
    ) -> None:
        super().__init__(
            message="Falha ao executar query no banco de dados",
            code="DB_QUERY_ERROR",
            context={
                "original_message": str(original_error),
                "query": query[:200] if query else None,  # Limitar por seguranca
            },
        )


class EntityNotFoundError(DomainError):
    """Erro de entidade nao encontrada."""

    def __init__(self, entity_name: str, identifier: Any) -> None:
        super().__init__(
            message=f"{entity_name} nao encontrado",
            code="ENTITY_NOT_FOUND",
            context={
                "entity": entity_name,
                "identifier": identifier,
            },
        )


class UnauthorizedError(DomainError):
    """Erro de autenticacao."""

    def __init__(self, message: str = "Acesso nao autorizado") -> None:
        super().__init__(message=message, code="UNAUTHORIZED")


class NotFoundError(DomainError):
    """Erro de recurso nao encontrado."""

    def __init__(self, resource: str) -> None:
        super().__init__(
            message=f"Recurso nao encontrado: {resource}",
            code="NOT_FOUND",
            context={"resource": resource},
        )


class TimeoutError(DomainError):
    """Erro de timeout."""

    def __init__(self, operation: str, timeout_ms: int) -> None:
        super().__init__(
            message=f"Timeout ao executar operacao: {operation}",
            code="TIMEOUT",
            context={
                "operation": operation,
                "timeout_ms": timeout_ms,
            },
        )


class ExternalServiceError(DomainError):
    """Erro de servico externo indisponivel."""

    def __init__(
        self,
        service: str,
        original_error: Exception | None = None,
    ) -> None:
        super().__init__(
            message=f"Servico externo indisponivel: {service}",
            code="EXTERNAL_SERVICE_ERROR",
            context={
                "service": service,
                "original_message": str(original_error) if original_error else None,
            },
        )
