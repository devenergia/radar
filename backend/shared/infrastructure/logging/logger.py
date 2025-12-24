"""Servico de logging estruturado - RAD-124."""

from __future__ import annotations

import logging
import sys

import structlog
from structlog.types import Processor


def setup_logging(
    level: str = "INFO",
    json_format: bool = True,
    service_name: str = "api-interrupcoes",
) -> None:
    """
    Configura logging estruturado.

    Args:
        level: Nivel minimo de log (DEBUG, INFO, WARNING, ERROR)
        json_format: True para JSON, False para console colorido
        service_name: Nome do servico para identificacao
    """
    # Configurar logging padrao
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
        force=True,
    )

    # Processadores comuns
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    # Processadores especificos do formato
    if json_format:
        processors: list[Processor] = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Adicionar contexto global
    structlog.contextvars.bind_contextvars(
        service=service_name,
    )


def configure_logging(
    level: str = "INFO",
    json_format: bool = True,
) -> None:
    """
    Configura o sistema de logging (funcao legacy).

    Args:
        level: Nivel de log
        json_format: Se True, usa formato JSON
    """
    setup_logging(level=level, json_format=json_format)


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """
    Retorna logger configurado.

    Args:
        name: Nome do logger (opcional)

    Returns:
        Logger estruturado
    """
    logger: structlog.BoundLogger = structlog.get_logger(name)
    return logger
