"""AuditLogger para auditoria de requisicoes - RAD-124."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog


@dataclass
class AuditEvent:
    """Evento de auditoria."""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = ""
    request_id: str = ""
    client_ip: str = ""
    api_key_prefix: str = ""
    method: str = ""
    path: str = ""
    status_code: int = 0
    duration_ms: float = 0
    extra: dict[str, Any] = field(default_factory=dict)


class AuditLogger:
    """Logger especializado para auditoria."""

    def __init__(self) -> None:
        self._logger = structlog.get_logger("audit")

    def log_request(
        self,
        request_id: str,
        client_ip: str,
        api_key: str | None,
        method: str,
        path: str,
    ) -> None:
        """
        Registra inicio de requisicao.

        Args:
            request_id: ID unico da requisicao
            client_ip: IP do cliente
            api_key: API Key (sera mascarada)
            method: Metodo HTTP
            path: Path da requisicao
        """
        self._logger.info(
            "request_started",
            request_id=request_id,
            client_ip=client_ip,
            api_key_prefix=self._mask_key(api_key),
            method=method,
            path=path,
        )

    def log_response(
        self,
        request_id: str,
        status_code: int,
        duration_ms: float,
        error: str | None = None,
    ) -> None:
        """
        Registra fim de requisicao.

        Args:
            request_id: ID unico da requisicao
            status_code: Codigo HTTP de resposta
            duration_ms: Tempo de processamento em ms
            error: Mensagem de erro (opcional)
        """
        log_method = self._logger.info if status_code < 400 else self._logger.warning

        log_method(
            "request_completed",
            request_id=request_id,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            error=error,
        )

    def log_auth_failure(
        self,
        request_id: str,
        client_ip: str,
        reason: str,
    ) -> None:
        """
        Registra falha de autenticacao.

        Args:
            request_id: ID unico da requisicao
            client_ip: IP do cliente
            reason: Motivo da falha
        """
        self._logger.warning(
            "auth_failure",
            request_id=request_id,
            client_ip=client_ip,
            reason=reason,
        )

    def log_rate_limit(
        self,
        request_id: str,
        client_ip: str,
        api_key: str | None,
    ) -> None:
        """
        Registra rate limit atingido.

        Args:
            request_id: ID unico da requisicao
            client_ip: IP do cliente
            api_key: API Key (sera mascarada)
        """
        self._logger.warning(
            "rate_limit_exceeded",
            request_id=request_id,
            client_ip=client_ip,
            api_key_prefix=self._mask_key(api_key),
        )

    def log_database_query(
        self,
        request_id: str,
        query_name: str,
        duration_ms: float,
        rows_returned: int,
    ) -> None:
        """
        Registra execucao de query.

        Args:
            request_id: ID unico da requisicao
            query_name: Nome identificador da query
            duration_ms: Tempo de execucao em ms
            rows_returned: Numero de linhas retornadas
        """
        self._logger.debug(
            "database_query",
            request_id=request_id,
            query_name=query_name,
            duration_ms=round(duration_ms, 2),
            rows_returned=rows_returned,
        )

    def log_cache_hit(self, request_id: str, key: str) -> None:
        """
        Registra cache hit.

        Args:
            request_id: ID unico da requisicao
            key: Chave do cache
        """
        self._logger.debug(
            "cache_hit",
            request_id=request_id,
            cache_key=key,
        )

    def log_cache_miss(self, request_id: str, key: str) -> None:
        """
        Registra cache miss.

        Args:
            request_id: ID unico da requisicao
            key: Chave do cache
        """
        self._logger.debug(
            "cache_miss",
            request_id=request_id,
            cache_key=key,
        )

    def _mask_key(self, api_key: str | None) -> str:
        """
        Mascara API Key para log.

        Args:
            api_key: API Key original

        Returns:
            API Key mascarada (primeiros 8 chars + ...)
        """
        if not api_key:
            return "none"
        if len(api_key) <= 8:
            return "***"
        return api_key[:8] + "..."


# Singleton
_audit_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """
    Retorna singleton do audit logger.

    Returns:
        Instancia unica de AuditLogger
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
