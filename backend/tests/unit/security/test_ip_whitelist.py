"""Testes unitarios para IP Whitelist ANEEL.

Seguindo TDD - estes testes sao escritos PRIMEIRO.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.shared.infrastructure.config import Settings


@pytest.mark.unit
class TestIpWhitelistConfig:
    """Testes para configuracao de whitelist de IP."""

    class TestAneelBlock:
        """Testes para bloco de IPs ANEEL (200.198.220.128/25)."""

        def test_deve_permitir_primeiro_ip_do_bloco_aneel(self) -> None:
            """IP 200.198.220.128 (primeiro do bloco) deve ser permitido."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            config = IpWhitelistConfig()

            assert config.is_allowed("200.198.220.128") is True

        def test_deve_permitir_ultimo_ip_do_bloco_aneel(self) -> None:
            """IP 200.198.220.255 (ultimo do bloco) deve ser permitido."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            config = IpWhitelistConfig()

            assert config.is_allowed("200.198.220.255") is True

        def test_deve_permitir_ip_meio_do_bloco_aneel(self) -> None:
            """IP 200.198.220.150 (meio do bloco) deve ser permitido."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            config = IpWhitelistConfig()

            assert config.is_allowed("200.198.220.150") is True

        def test_deve_permitir_ip_200_aneel(self) -> None:
            """IP 200.198.220.200 deve ser permitido."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            config = IpWhitelistConfig()

            assert config.is_allowed("200.198.220.200") is True

    class TestIpsNaoAutorizados:
        """Testes para IPs fora do bloco ANEEL."""

        def test_deve_rejeitar_ip_antes_do_bloco_aneel(self) -> None:
            """IP 200.198.220.127 (antes do bloco) deve ser rejeitado."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            config = IpWhitelistConfig()

            assert config.is_allowed("200.198.220.127") is False

        def test_deve_rejeitar_ip_de_outro_bloco(self) -> None:
            """IP 200.198.221.1 (outro bloco) deve ser rejeitado."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            config = IpWhitelistConfig()

            assert config.is_allowed("200.198.221.1") is False

        def test_deve_rejeitar_ip_privado(self) -> None:
            """IP privado 192.168.1.1 deve ser rejeitado."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            config = IpWhitelistConfig()

            assert config.is_allowed("192.168.1.1") is False

        def test_deve_rejeitar_ip_publico_aleatorio(self) -> None:
            """IP publico 8.8.8.8 (Google) deve ser rejeitado."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            config = IpWhitelistConfig()

            assert config.is_allowed("8.8.8.8") is False

    class TestIpsInvalidos:
        """Testes para IPs invalidos."""

        def test_deve_rejeitar_ip_formato_invalido(self) -> None:
            """String invalida deve ser rejeitada."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            config = IpWhitelistConfig()

            assert config.is_allowed("invalid") is False

        def test_deve_rejeitar_string_vazia(self) -> None:
            """String vazia deve ser rejeitada."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            config = IpWhitelistConfig()

            assert config.is_allowed("") is False

        def test_deve_rejeitar_ip_com_octetos_invalidos(self) -> None:
            """IP com octetos > 255 deve ser rejeitado."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            config = IpWhitelistConfig()

            assert config.is_allowed("256.256.256.256") is False

        def test_deve_rejeitar_ip_unknown(self) -> None:
            """String 'unknown' deve ser rejeitada."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            config = IpWhitelistConfig()

            assert config.is_allowed("unknown") is False

    class TestIpsExtras:
        """Testes para IPs extras configurados via Settings."""

        def test_deve_permitir_ip_de_rede_extra(self) -> None:
            """IP de rede extra configurada deve ser permitido."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            settings = MagicMock(spec=Settings)
            settings.ip_whitelist_extra = "192.168.0.0/16"
            config = IpWhitelistConfig(settings)

            assert config.is_allowed("192.168.1.100") is True

        def test_deve_permitir_ip_de_multiplas_redes_extras(self) -> None:
            """IPs de multiplas redes extras devem ser permitidos."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            settings = MagicMock(spec=Settings)
            settings.ip_whitelist_extra = "192.168.0.0/16,10.0.0.0/8"
            config = IpWhitelistConfig(settings)

            assert config.is_allowed("192.168.1.100") is True
            assert config.is_allowed("10.20.30.40") is True

        def test_deve_manter_bloco_aneel_com_redes_extras(self) -> None:
            """Bloco ANEEL deve continuar funcionando com redes extras."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            settings = MagicMock(spec=Settings)
            settings.ip_whitelist_extra = "192.168.0.0/16"
            config = IpWhitelistConfig(settings)

            # Bloco ANEEL ainda deve funcionar
            assert config.is_allowed("200.198.220.150") is True

        def test_deve_funcionar_sem_redes_extras(self) -> None:
            """Deve funcionar normalmente sem redes extras."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistConfig,
            )

            settings = MagicMock(spec=Settings)
            settings.ip_whitelist_extra = None
            config = IpWhitelistConfig(settings)

            # Bloco ANEEL deve funcionar
            assert config.is_allowed("200.198.220.150") is True
            # IP privado deve ser rejeitado
            assert config.is_allowed("192.168.1.1") is False


@pytest.mark.unit
class TestIpWhitelistMiddleware:
    """Testes para middleware de whitelist de IP."""

    @pytest.fixture
    def middleware_with_localhost(self) -> MagicMock:
        """Middleware configurado para aceitar localhost."""
        from backend.apps.api_interrupcoes.security.ip_whitelist import (
            IpWhitelistMiddleware,
        )

        app = MagicMock()
        settings = MagicMock(spec=Settings)
        settings.ip_whitelist_extra = "127.0.0.0/8"
        return IpWhitelistMiddleware(app, settings)

    class TestGetClientIp:
        """Testes para extracao de IP do cliente."""

        def test_deve_extrair_ip_de_x_forwarded_for(self) -> None:
            """Deve usar primeiro IP do X-Forwarded-For."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistMiddleware,
            )

            app = MagicMock()
            settings = MagicMock(spec=Settings)
            settings.ip_whitelist_extra = "127.0.0.0/8"
            middleware = IpWhitelistMiddleware(app, settings)

            request = MagicMock()
            request.headers = {
                "X-Forwarded-For": "200.198.220.150, 10.0.0.1, 192.168.1.1"
            }
            request.client = MagicMock(host="127.0.0.1")

            ip = middleware._get_client_ip(request)

            assert ip == "200.198.220.150"

        def test_deve_extrair_ip_de_x_real_ip(self) -> None:
            """Deve usar X-Real-IP se X-Forwarded-For ausente."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistMiddleware,
            )

            app = MagicMock()
            settings = MagicMock(spec=Settings)
            settings.ip_whitelist_extra = None
            middleware = IpWhitelistMiddleware(app, settings)

            request = MagicMock()
            request.headers = {"X-Real-IP": "200.198.220.150"}
            request.client = MagicMock(host="127.0.0.1")

            ip = middleware._get_client_ip(request)

            assert ip == "200.198.220.150"

        def test_deve_usar_client_host_como_fallback(self) -> None:
            """Deve usar request.client.host se headers ausentes."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistMiddleware,
            )

            app = MagicMock()
            settings = MagicMock(spec=Settings)
            settings.ip_whitelist_extra = None
            middleware = IpWhitelistMiddleware(app, settings)

            request = MagicMock()
            request.headers = {}
            request.client = MagicMock(host="200.198.220.150")

            ip = middleware._get_client_ip(request)

            assert ip == "200.198.220.150"

        def test_deve_retornar_unknown_sem_client(self) -> None:
            """Deve retornar 'unknown' se nao conseguir obter IP."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistMiddleware,
            )

            app = MagicMock()
            settings = MagicMock(spec=Settings)
            settings.ip_whitelist_extra = None
            middleware = IpWhitelistMiddleware(app, settings)

            request = MagicMock()
            request.headers = {}
            request.client = None

            ip = middleware._get_client_ip(request)

            assert ip == "unknown"

    class TestForbiddenResponse:
        """Testes para resposta 403 no formato ANEEL."""

        def test_resposta_403_deve_ter_status_code_correto(self) -> None:
            """Resposta deve ter status code 403."""
            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistMiddleware,
            )

            app = MagicMock()
            settings = MagicMock(spec=Settings)
            settings.ip_whitelist_extra = None
            middleware = IpWhitelistMiddleware(app, settings)

            response = middleware._forbidden_response("192.168.1.1")

            assert response.status_code == 403

        def test_resposta_403_deve_ter_formato_aneel(self) -> None:
            """Resposta deve ter campos no formato ANEEL."""
            import json

            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistMiddleware,
            )

            app = MagicMock()
            settings = MagicMock(spec=Settings)
            settings.ip_whitelist_extra = None
            middleware = IpWhitelistMiddleware(app, settings)

            response = middleware._forbidden_response("192.168.1.1")
            body = json.loads(response.body.decode())

            assert body["idcStatusRequisicao"] == 2
            assert body["desStatusRequisicao"] == "Acesso negado"
            assert "IP de origem nao autorizado" in body["mensagem"]
            assert "interrupcaoFornecimento" in body

        def test_resposta_403_deve_ter_email_indisponibilidade(self) -> None:
            """Resposta deve ter email de contato."""
            import json

            from backend.apps.api_interrupcoes.security.ip_whitelist import (
                IpWhitelistMiddleware,
            )

            app = MagicMock()
            settings = MagicMock(spec=Settings)
            settings.ip_whitelist_extra = None
            middleware = IpWhitelistMiddleware(app, settings)

            response = middleware._forbidden_response("192.168.1.1")
            body = json.loads(response.body.decode())

            assert "emailIndisponibilidade" in body
            assert "radar@roraimaenergia.com.br" in body["emailIndisponibilidade"]


@pytest.mark.unit
class TestIpWhitelistBypass:
    """Testes para bypass de endpoints publicos."""

    @pytest.mark.asyncio
    async def test_deve_permitir_health_sem_validacao(self) -> None:
        """Endpoint /health deve ignorar whitelist."""
        from backend.apps.api_interrupcoes.security.ip_whitelist import (
            IpWhitelistMiddleware,
        )

        app = MagicMock()
        settings = MagicMock(spec=Settings)
        settings.ip_whitelist_extra = None
        middleware = IpWhitelistMiddleware(app, settings)

        request = MagicMock()
        request.url.path = "/health"
        request.client = MagicMock(host="192.168.1.1")  # IP nao autorizado
        request.headers = {}

        call_next = AsyncMock(return_value="response")

        await middleware.dispatch(request, call_next)

        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_deve_permitir_docs_sem_validacao(self) -> None:
        """Endpoint /docs deve ignorar whitelist."""
        from backend.apps.api_interrupcoes.security.ip_whitelist import (
            IpWhitelistMiddleware,
        )

        app = MagicMock()
        settings = MagicMock(spec=Settings)
        settings.ip_whitelist_extra = None
        middleware = IpWhitelistMiddleware(app, settings)

        request = MagicMock()
        request.url.path = "/docs"
        request.client = MagicMock(host="192.168.1.1")
        request.headers = {}

        call_next = AsyncMock(return_value="response")

        await middleware.dispatch(request, call_next)

        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_deve_permitir_redoc_sem_validacao(self) -> None:
        """Endpoint /redoc deve ignorar whitelist."""
        from backend.apps.api_interrupcoes.security.ip_whitelist import (
            IpWhitelistMiddleware,
        )

        app = MagicMock()
        settings = MagicMock(spec=Settings)
        settings.ip_whitelist_extra = None
        middleware = IpWhitelistMiddleware(app, settings)

        request = MagicMock()
        request.url.path = "/redoc"
        request.client = MagicMock(host="192.168.1.1")
        request.headers = {}

        call_next = AsyncMock(return_value="response")

        await middleware.dispatch(request, call_next)

        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_deve_permitir_openapi_json_sem_validacao(self) -> None:
        """Endpoint /openapi.json deve ignorar whitelist."""
        from backend.apps.api_interrupcoes.security.ip_whitelist import (
            IpWhitelistMiddleware,
        )

        app = MagicMock()
        settings = MagicMock(spec=Settings)
        settings.ip_whitelist_extra = None
        middleware = IpWhitelistMiddleware(app, settings)

        request = MagicMock()
        request.url.path = "/openapi.json"
        request.client = MagicMock(host="192.168.1.1")
        request.headers = {}

        call_next = AsyncMock(return_value="response")

        await middleware.dispatch(request, call_next)

        call_next.assert_called_once_with(request)


@pytest.mark.unit
class TestIpWhitelistDispatch:
    """Testes para dispatch do middleware."""

    @pytest.mark.asyncio
    async def test_deve_bloquear_ip_nao_autorizado(self) -> None:
        """IP nao autorizado deve receber 403."""
        from backend.apps.api_interrupcoes.security.ip_whitelist import (
            IpWhitelistMiddleware,
        )

        app = MagicMock()
        settings = MagicMock(spec=Settings)
        settings.ip_whitelist_extra = None
        middleware = IpWhitelistMiddleware(app, settings)

        request = MagicMock()
        request.url.path = "/api/v1/quantitativointerrupcoesativas"
        request.client = MagicMock(host="192.168.1.1")  # IP nao autorizado
        request.headers = {}

        call_next = AsyncMock(return_value="response")

        result = await middleware.dispatch(request, call_next)

        assert result.status_code == 403
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_deve_permitir_ip_aneel(self) -> None:
        """IP do bloco ANEEL deve passar."""
        from backend.apps.api_interrupcoes.security.ip_whitelist import (
            IpWhitelistMiddleware,
        )

        app = MagicMock()
        settings = MagicMock(spec=Settings)
        settings.ip_whitelist_extra = None
        middleware = IpWhitelistMiddleware(app, settings)

        request = MagicMock()
        request.url.path = "/api/v1/quantitativointerrupcoesativas"
        request.client = MagicMock(host="200.198.220.150")  # IP ANEEL
        request.headers = {}

        call_next = AsyncMock(return_value="response")

        result = await middleware.dispatch(request, call_next)

        call_next.assert_called_once_with(request)
        assert result == "response"


@pytest.mark.unit
class TestVerifyIpWhitelistDependency:
    """Testes para dependency de validacao de IP."""

    @pytest.mark.asyncio
    async def test_deve_retornar_ip_quando_valido(self) -> None:
        """Deve retornar IP quando autorizado."""
        from unittest.mock import patch

        from backend.apps.api_interrupcoes.security.ip_whitelist import (
            verify_ip_whitelist,
        )

        request = MagicMock()
        request.headers = {"X-Forwarded-For": "200.198.220.150"}
        request.client = None

        with patch(
            "backend.apps.api_interrupcoes.security.ip_whitelist.IpWhitelistConfig"
        ) as mock_config:
            mock_config.return_value.is_allowed.return_value = True
            ip = await verify_ip_whitelist(request)
            assert ip == "200.198.220.150"

    @pytest.mark.asyncio
    async def test_deve_lancar_403_quando_ip_invalido(self) -> None:
        """Deve lancar HTTPException 403 quando IP nao autorizado."""
        from unittest.mock import patch

        from fastapi import HTTPException

        from backend.apps.api_interrupcoes.security.ip_whitelist import (
            verify_ip_whitelist,
        )

        request = MagicMock()
        request.headers = {"X-Forwarded-For": "192.168.1.1"}
        request.client = None

        with patch(
            "backend.apps.api_interrupcoes.security.ip_whitelist.IpWhitelistConfig"
        ) as mock_config:
            mock_config.return_value.is_allowed.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                await verify_ip_whitelist(request)

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_resposta_erro_deve_ter_formato_aneel(self) -> None:
        """Erro deve ter formato ANEEL com campos obrigatorios."""
        from unittest.mock import patch

        from fastapi import HTTPException

        from backend.apps.api_interrupcoes.security.ip_whitelist import (
            verify_ip_whitelist,
        )

        request = MagicMock()
        request.headers = {"X-Forwarded-For": "192.168.1.1"}
        request.client = None

        with patch(
            "backend.apps.api_interrupcoes.security.ip_whitelist.IpWhitelistConfig"
        ) as mock_config:
            mock_config.return_value.is_allowed.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                await verify_ip_whitelist(request)

            detail = exc_info.value.detail
            assert detail["idcStatusRequisicao"] == 2
            assert "IP de origem nao autorizado" in detail["mensagem"]


@pytest.mark.unit
class TestIpWhitelistConstantes:
    """Testes para constantes da whitelist."""

    def test_cidr_aneel_deve_ser_correto(self) -> None:
        """CIDR do bloco ANEEL deve ser 200.198.220.128/25."""
        from backend.apps.api_interrupcoes.security.ip_whitelist import (
            IpWhitelistConfig,
        )

        assert IpWhitelistConfig.ANEEL_CIDR == "200.198.220.128/25"
