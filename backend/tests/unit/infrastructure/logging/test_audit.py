"""Testes TDD para AuditLogger - RAD-124."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from backend.shared.infrastructure.logging.audit import (
    AuditLogger,
    get_audit_logger,
)


@pytest.mark.unit
class TestAuditLogger:
    """Testes para AuditLogger."""

    @pytest.fixture
    def audit(self) -> AuditLogger:
        """AuditLogger de teste."""
        return AuditLogger()

    class TestMaskKey:
        """Testes para mascaramento de API Key."""

        def test_deve_retornar_none_para_api_key_vazia(self) -> None:
            """API Key None retorna 'none'."""
            audit = AuditLogger()

            masked = audit._mask_key(None)

            assert masked == "none"

        def test_deve_mascarar_api_key_curta(self) -> None:
            """API Key curta e mascarada completamente."""
            audit = AuditLogger()

            masked = audit._mask_key("abc")

            assert masked == "***"

        def test_deve_mascarar_api_key_com_8_caracteres(self) -> None:
            """API Key com exatamente 8 caracteres e mascarada."""
            audit = AuditLogger()

            masked = audit._mask_key("12345678")

            assert masked == "***"

        def test_deve_mascarar_api_key_longa(self) -> None:
            """API Key longa mostra apenas prefixo."""
            audit = AuditLogger()

            masked = audit._mask_key("abcdef123456789")

            assert masked == "abcdef12..."
            assert "123456789" not in masked

        def test_deve_mascarar_api_key_vazia_string(self) -> None:
            """API Key vazia (string vazia) retorna 'none'."""
            audit = AuditLogger()

            masked = audit._mask_key("")

            assert masked == "none"

    class TestLogRequest:
        """Testes para log de inicio de requisicao."""

        def test_deve_incluir_campos_obrigatorios(self) -> None:
            """Log de request inclui campos necessarios."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_request(
                    request_id="abc123",
                    client_ip="192.168.1.1",
                    api_key="my-api-key-12345",
                    method="GET",
                    path="/api/v1/interrupcoes/quantitativointerrupcoesativas",
                )

                mock_logger.info.assert_called_once()
                call_args = mock_logger.info.call_args
                assert call_args[0][0] == "request_started"
                assert call_args[1]["request_id"] == "abc123"
                assert call_args[1]["client_ip"] == "192.168.1.1"
                assert call_args[1]["method"] == "GET"
                assert call_args[1]["path"] == "/api/v1/interrupcoes/quantitativointerrupcoesativas"
                assert call_args[1]["api_key_prefix"] == "my-api-k..."

        def test_deve_mascarar_api_key(self) -> None:
            """API Key deve ser mascarada no log."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_request(
                    request_id="abc123",
                    client_ip="192.168.1.1",
                    api_key="super-secret-api-key-1234567890",
                    method="GET",
                    path="/test",
                )

                call_args = mock_logger.info.call_args
                assert "super-secret-api-key" not in str(call_args)
                assert call_args[1]["api_key_prefix"] == "super-se..."

    class TestLogResponse:
        """Testes para log de fim de requisicao."""

        def test_deve_incluir_status_e_duracao(self) -> None:
            """Log de response inclui status e duracao."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_response(
                    request_id="abc123",
                    status_code=200,
                    duration_ms=45.5,
                )

                mock_logger.info.assert_called_once()
                call_args = mock_logger.info.call_args
                assert call_args[0][0] == "request_completed"
                assert call_args[1]["status_code"] == 200
                assert call_args[1]["duration_ms"] == 45.5

        def test_deve_usar_info_para_sucesso(self) -> None:
            """Log de sucesso usa nivel info."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_response(
                    request_id="abc123",
                    status_code=200,
                    duration_ms=50.0,
                )

                mock_logger.info.assert_called_once()
                mock_logger.warning.assert_not_called()

        def test_deve_usar_warning_para_erros_4xx(self) -> None:
            """Log de erro 4xx usa nivel warning."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_response(
                    request_id="abc123",
                    status_code=400,
                    duration_ms=100.0,
                )

                mock_logger.warning.assert_called_once()
                mock_logger.info.assert_not_called()

        def test_deve_usar_warning_para_erros_5xx(self) -> None:
            """Log de erro 5xx usa nivel warning."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_response(
                    request_id="abc123",
                    status_code=500,
                    duration_ms=100.0,
                    error="Internal error",
                )

                mock_logger.warning.assert_called_once()
                call_args = mock_logger.warning.call_args
                assert call_args[1]["error"] == "Internal error"

        def test_deve_arredondar_duracao(self) -> None:
            """Duracao deve ser arredondada para 2 casas decimais."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_response(
                    request_id="abc123",
                    status_code=200,
                    duration_ms=45.12345678,
                )

                call_args = mock_logger.info.call_args
                assert call_args[1]["duration_ms"] == 45.12

    class TestLogAuthFailure:
        """Testes para log de falha de autenticacao."""

        def test_deve_registrar_falha_com_warning(self) -> None:
            """Log de falha de autenticacao usa warning."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_auth_failure(
                    request_id="abc123",
                    client_ip="192.168.1.1",
                    reason="API Key invalida",
                )

                mock_logger.warning.assert_called_once()
                call_args = mock_logger.warning.call_args
                assert call_args[0][0] == "auth_failure"
                assert call_args[1]["reason"] == "API Key invalida"

        def test_deve_incluir_ip_do_cliente(self) -> None:
            """Log deve incluir IP do cliente."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_auth_failure(
                    request_id="abc123",
                    client_ip="10.0.0.1",
                    reason="Token expirado",
                )

                call_args = mock_logger.warning.call_args
                assert call_args[1]["client_ip"] == "10.0.0.1"

    class TestLogRateLimit:
        """Testes para log de rate limit excedido."""

        def test_deve_registrar_rate_limit_com_warning(self) -> None:
            """Log de rate limit usa warning."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_rate_limit(
                    request_id="abc123",
                    client_ip="192.168.1.1",
                    api_key="my-key-12345678",
                )

                mock_logger.warning.assert_called_once()
                call_args = mock_logger.warning.call_args
                assert call_args[0][0] == "rate_limit_exceeded"

        def test_deve_mascarar_api_key(self) -> None:
            """API Key deve ser mascarada no log de rate limit."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_rate_limit(
                    request_id="abc123",
                    client_ip="192.168.1.1",
                    api_key="super-secret-key-123",
                )

                call_args = mock_logger.warning.call_args
                assert call_args[1]["api_key_prefix"] == "super-se..."

    class TestLogDatabaseQuery:
        """Testes para log de query no banco."""

        def test_deve_registrar_query_com_debug(self) -> None:
            """Log de query usa nivel debug."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_database_query(
                    request_id="abc123",
                    query_name="buscar_ativas",
                    duration_ms=150.789,
                    rows_returned=42,
                )

                mock_logger.debug.assert_called_once()
                call_args = mock_logger.debug.call_args
                assert call_args[0][0] == "database_query"
                assert call_args[1]["query_name"] == "buscar_ativas"
                assert call_args[1]["duration_ms"] == 150.79
                assert call_args[1]["rows_returned"] == 42

    class TestLogCacheHit:
        """Testes para log de cache hit."""

        def test_deve_registrar_cache_hit_com_debug(self) -> None:
            """Log de cache hit usa nivel debug."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_cache_hit(
                    request_id="abc123",
                    key="interrupcoes:ativas",
                )

                mock_logger.debug.assert_called_once()
                call_args = mock_logger.debug.call_args
                assert call_args[0][0] == "cache_hit"
                assert call_args[1]["cache_key"] == "interrupcoes:ativas"

    class TestLogCacheMiss:
        """Testes para log de cache miss."""

        def test_deve_registrar_cache_miss_com_debug(self) -> None:
            """Log de cache miss usa nivel debug."""
            audit = AuditLogger()

            with patch.object(audit, "_logger") as mock_logger:
                audit.log_cache_miss(
                    request_id="abc123",
                    key="interrupcoes:ativas",
                )

                mock_logger.debug.assert_called_once()
                call_args = mock_logger.debug.call_args
                assert call_args[0][0] == "cache_miss"
                assert call_args[1]["cache_key"] == "interrupcoes:ativas"


@pytest.mark.unit
class TestGetAuditLogger:
    """Testes para singleton do AuditLogger."""

    def test_deve_retornar_instancia_de_audit_logger(self) -> None:
        """Deve retornar instancia de AuditLogger."""
        audit = get_audit_logger()

        assert isinstance(audit, AuditLogger)

    def test_deve_retornar_mesma_instancia(self) -> None:
        """Retorna singleton."""
        audit1 = get_audit_logger()
        audit2 = get_audit_logger()

        assert audit1 is audit2
