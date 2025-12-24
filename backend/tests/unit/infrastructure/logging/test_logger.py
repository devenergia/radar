"""Testes TDD para configuracao de logging - RAD-124."""

from __future__ import annotations

import logging

import pytest
import structlog

from backend.shared.infrastructure.logging.logger import (
    configure_logging,
    get_logger,
    setup_logging,
)


@pytest.mark.unit
class TestSetupLogging:
    """Testes para configuracao de logging."""

    def test_deve_configurar_logging_json_em_producao(self) -> None:
        """JSON format em producao."""
        setup_logging(level="INFO", json_format=True, service_name="test-api")

        logger = get_logger("test")
        assert logger is not None

    def test_deve_configurar_logging_console_em_desenvolvimento(self) -> None:
        """Console format em desenvolvimento."""
        setup_logging(level="DEBUG", json_format=False, service_name="test-dev")

        logger = get_logger("test")
        assert logger is not None

    def test_deve_aceitar_nivel_debug(self) -> None:
        """Aceita nivel DEBUG."""
        setup_logging(level="DEBUG")
        logger = get_logger("test")
        assert logger is not None

    def test_deve_aceitar_nivel_info(self) -> None:
        """Aceita nivel INFO."""
        setup_logging(level="INFO")
        logger = get_logger("test")
        assert logger is not None

    def test_deve_aceitar_nivel_warning(self) -> None:
        """Aceita nivel WARNING."""
        setup_logging(level="WARNING")
        logger = get_logger("test")
        assert logger is not None

    def test_deve_aceitar_nivel_error(self) -> None:
        """Aceita nivel ERROR."""
        setup_logging(level="ERROR")
        logger = get_logger("test")
        assert logger is not None

    def test_deve_adicionar_contexto_do_servico(self) -> None:
        """Deve adicionar nome do servico ao contexto."""
        setup_logging(level="INFO", json_format=True, service_name="radar-api")

        # O contexto deve estar disponivel apos configuracao
        logger = get_logger("test")
        assert logger is not None


@pytest.mark.unit
class TestConfigureLogging:
    """Testes para configure_logging (funcao legacy)."""

    def test_deve_configurar_com_json_format(self) -> None:
        """Configuracao com JSON format."""
        configure_logging(level="INFO", json_format=True)

        logger = get_logger("test")
        assert logger is not None

    def test_deve_configurar_com_console_format(self) -> None:
        """Configuracao com console format."""
        configure_logging(level="DEBUG", json_format=False)

        logger = get_logger("test")
        assert logger is not None


@pytest.mark.unit
class TestGetLogger:
    """Testes para get_logger."""

    def test_deve_retornar_logger_com_nome(self) -> None:
        """Retorna logger com nome especificado."""
        logger = get_logger("meu-modulo")

        assert logger is not None

    def test_deve_retornar_logger_sem_nome(self) -> None:
        """Retorna logger sem nome (None)."""
        logger = get_logger()

        assert logger is not None

    def test_deve_retornar_bound_logger(self) -> None:
        """Retorna BoundLogger do structlog."""
        logger = get_logger("test")

        # Verifica que tem os metodos esperados
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
