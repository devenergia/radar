"""Testes E2E para API de Interrupcoes.

Testes end-to-end que validam o comportamento completo da API,
incluindo autenticacao, formato de resposta e endpoints.
"""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.e2e
class TestQuantitativoInterrupcoesAtivas:
    """Testes E2E para endpoint /quantitativointerrupcoesativas."""

    class TestAutenticacao:
        """Testes de autenticacao."""

        @pytest.mark.asyncio
        async def test_deve_retornar_401_sem_api_key(
            self,
            client: AsyncClient,
        ) -> None:
            """Requisicao sem x-api-key deve retornar 401."""
            # Act
            response = await client.get("/quantitativointerrupcoesativas")

            # Assert
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        @pytest.mark.asyncio
        async def test_deve_retornar_401_com_api_key_invalida(
            self,
            client: AsyncClient,
        ) -> None:
            """Requisicao com x-api-key invalida deve retornar 401."""
            # Act
            response = await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": "chave-invalida-xyz"},
            )

            # Assert
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        @pytest.mark.asyncio
        async def test_deve_retornar_200_com_api_key_valida(
            self,
            client: AsyncClient,
            api_key: str,
        ) -> None:
            """Requisicao com x-api-key valida deve retornar 200."""
            # Act
            response = await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": api_key},
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_erro_401_deve_ter_formato_aneel_v4(
            self,
            client: AsyncClient,
        ) -> None:
            """Erro 401 deve retornar formato ANEEL V4."""
            # Act
            response = await client.get("/quantitativointerrupcoesativas")

            # Assert
            data = response.json()
            detail = data.get("detail", data)
            assert detail["idcStatusRequisicao"] == 2
            assert "emailIndisponibilidade" in detail
            assert "interrupcaoFornecimento" in detail
            assert detail["interrupcaoFornecimento"] == []

    class TestFormatoResposta:
        """Testes do formato de resposta ANEEL."""

        @pytest.mark.asyncio
        async def test_deve_retornar_campos_obrigatorios_aneel_v4(
            self,
            client: AsyncClient,
            api_key: str,
        ) -> None:
            """Resposta deve ter campos obrigatorios ANEEL V4."""
            # Act
            response = await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": api_key},
            )

            # Assert
            data = response.json()
            # Campos obrigatorios ANEEL V4 (Oficio Circular 14/2025-SFE/ANEEL)
            assert "idcStatusRequisicao" in data
            assert "emailIndisponibilidade" in data
            assert "mensagem" in data
            assert "interrupcaoFornecimento" in data

        @pytest.mark.asyncio
        async def test_status_sucesso_deve_ser_1(
            self,
            client: AsyncClient,
            api_key: str,
        ) -> None:
            """idcStatusRequisicao deve ser 1 para sucesso."""
            # Act
            response = await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": api_key},
            )

            # Assert
            data = response.json()
            assert data["idcStatusRequisicao"] == 1

        @pytest.mark.asyncio
        async def test_email_deve_estar_configurado(
            self,
            client: AsyncClient,
            api_key: str,
        ) -> None:
            """emailIndisponibilidade deve ter valor configurado."""
            # Act
            response = await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": api_key},
            )

            # Assert
            data = response.json()
            assert data["emailIndisponibilidade"] != ""
            assert "@" in data["emailIndisponibilidade"]

        @pytest.mark.asyncio
        async def test_mensagem_deve_ser_vazia_para_sucesso(
            self,
            client: AsyncClient,
            api_key: str,
        ) -> None:
            """mensagem deve ser vazia quando sucesso."""
            # Act
            response = await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": api_key},
            )

            # Assert
            data = response.json()
            assert data["mensagem"] == ""

        @pytest.mark.asyncio
        async def test_interrupcaoFornecimento_deve_ser_lista(
            self,
            client: AsyncClient,
            api_key: str,
        ) -> None:
            """interrupcaoFornecimento deve ser uma lista (ANEEL V4)."""
            # Act
            response = await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": api_key},
            )

            # Assert
            data = response.json()
            assert isinstance(data["interrupcaoFornecimento"], list)


@pytest.mark.e2e
class TestHealthCheck:
    """Testes E2E para endpoint /health."""

    @pytest.mark.asyncio
    async def test_health_deve_retornar_200(
        self,
        client: AsyncClient,
    ) -> None:
        """Health check deve retornar 200."""
        # Act
        response = await client.get("/health")

        # Assert
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_health_deve_retornar_status_healthy(
        self,
        client: AsyncClient,
    ) -> None:
        """Health check deve retornar status healthy."""
        # Act
        response = await client.get("/health")

        # Assert
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_nao_requer_autenticacao(
        self,
        client: AsyncClient,
    ) -> None:
        """Health check nao deve requerer x-api-key."""
        # Act - Sem header x-api-key
        response = await client.get("/health")

        # Assert
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_health_deve_ter_version(
        self,
        client: AsyncClient,
    ) -> None:
        """Health check deve retornar versao."""
        # Act
        response = await client.get("/health")

        # Assert
        data = response.json()
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_deve_ter_checks(
        self,
        client: AsyncClient,
    ) -> None:
        """Health check deve retornar detalhes dos checks."""
        # Act
        response = await client.get("/health")

        # Assert
        data = response.json()
        assert "checks" in data
        assert "database" in data["checks"]
        assert "cache" in data["checks"]


@pytest.mark.e2e
class TestRoot:
    """Testes E2E para endpoint raiz /."""

    @pytest.mark.asyncio
    async def test_root_deve_retornar_200(
        self,
        client: AsyncClient,
    ) -> None:
        """Endpoint raiz deve retornar 200."""
        # Act
        response = await client.get("/")

        # Assert
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_root_deve_retornar_info_api(
        self,
        client: AsyncClient,
    ) -> None:
        """Endpoint raiz deve retornar informacoes da API."""
        # Act
        response = await client.get("/")

        # Assert
        data = response.json()
        assert "api" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_root_nao_requer_autenticacao(
        self,
        client: AsyncClient,
    ) -> None:
        """Endpoint raiz nao deve requerer x-api-key."""
        # Act - Sem header x-api-key
        response = await client.get("/")

        # Assert
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.e2e
class TestEndpointNaoExistente:
    """Testes para endpoints que nao existem."""

    @pytest.mark.asyncio
    async def test_endpoint_inexistente_retorna_404(
        self,
        client: AsyncClient,
    ) -> None:
        """Endpoint inexistente deve retornar 404."""
        # Act
        response = await client.get("/endpoint-que-nao-existe")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
