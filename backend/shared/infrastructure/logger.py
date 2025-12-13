"""Servico de logging estruturado."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Retorna um logger configurado.

    Args:
        name: Nome do logger (opcional)

    Returns:
        Logger estruturado
    """
    return structlog.get_logger(name)


def create_logger(
    level: str = "INFO",
    json_format: bool = True,
) -> structlog.stdlib.BoundLogger:
    """
    Cria e configura um novo logger.

    Args:
        level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Se True, usa formato JSON; se False, formato console

    Returns:
        Logger configurado
    """
    configure_logging(level, json_format)
    return structlog.get_logger()


def configure_logging(
    level: str = "INFO",
    json_format: bool = True,
) -> None:
    """
    Configura o sistema de logging.

    Args:
        level: Nivel de log
        json_format: Se True, usa formato JSON
    """
    # Processadores comuns
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_format:
        # Formato JSON para producao
        processors: list[Processor] = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Formato console para desenvolvimento
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configurar logging padrao do Python
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )


class LoggerMixin:
    """Mixin para adicionar logger a classes."""

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Retorna logger com nome da classe."""
        return structlog.get_logger(self.__class__.__name__)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **extra: Any,
) -> None:
    """
    Loga uma requisicao HTTP.

    Args:
        method: Metodo HTTP
        path: Caminho da requisicao
        status_code: Codigo de status da resposta
        duration_ms: Duracao em milissegundos
        **extra: Campos adicionais
    """
    logger = get_logger("http")
    logger.info(
        "request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration_ms, 2),
        **extra,
    )


def log_error(
    error: Exception,
    context: dict[str, Any] | None = None,
) -> None:
    """
    Loga um erro.

    Args:
        error: Excecao
        context: Contexto adicional
    """
    logger = get_logger("error")
    logger.error(
        "error",
        error_type=type(error).__name__,
        error_message=str(error),
        **(context or {}),
        exc_info=True,
    )
