"""Testes E2E para Rate Limiting.

Testes end-to-end que validam o comportamento do rate limiting
conforme especificacao ANEEL (10 req/min).
"""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.e2e
class TestRateLimiting:
    """Testes E2E para rate limiting."""

    @pytest.mark.asyncio
    async def test_deve_permitir_10_requisicoes_por_minuto(
        self,
        client: AsyncClient,
        api_key: str,
    ) -> None:
        """10 requisicoes em 1 minuto devem ser permitidas."""
        for i in range(10):
            response = await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": api_key},
            )
            assert response.status_code == status.HTTP_200_OK, (
                f"Falhou na requisicao {i + 1}"
            )

    @pytest.mark.asyncio
    async def test_deve_bloquear_11a_requisicao(
        self,
        client: AsyncClient,
        api_key: str,
    ) -> None:
        """11a requisicao deve ser bloqueada com 429."""
        # Faz 10 requisicoes
        for _ in range(10):
            await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": api_key},
            )

        # 11a requisicao deve falhar
        response = await client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": api_key},
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @pytest.mark.asyncio
    async def test_resposta_429_deve_ter_formato_aneel(
        self,
        client: AsyncClient,
        api_key: str,
    ) -> None:
        """Resposta 429 deve seguir formato ANEEL."""
        # Excede limite
        for _ in range(11):
            response = await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": api_key},
            )

        # Verifica formato ANEEL
        data = response.json()
        assert data["idcStatusRequisicao"] == 2
        assert data["desStatusRequisicao"] == "Erro"
        assert "emailIndisponibilidade" in data
        assert "rate limit" in data["mensagem"].lower()

    @pytest.mark.asyncio
    async def test_deve_ter_header_retry_after(
        self,
        client: AsyncClient,
        api_key: str,
    ) -> None:
        """Resposta 429 deve incluir Retry-After."""
        # Excede limite
        for _ in range(11):
            response = await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": api_key},
            )

        assert "Retry-After" in response.headers
        # Retry-After deve ser um numero (segundos)
        retry_after = int(response.headers["Retry-After"])
        assert retry_after > 0

    @pytest.mark.asyncio
    async def test_health_check_nao_conta_para_rate_limit(
        self,
        client: AsyncClient,
        api_key: str,
    ) -> None:
        """Health check nao deve consumir quota."""
        # Faz muitos health checks
        for _ in range(20):
            await client.get("/health")

        # Ainda deve poder fazer requisicao normal
        response = await client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": api_key},
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_root_nao_conta_para_rate_limit(
        self,
        client: AsyncClient,
        api_key: str,
    ) -> None:
        """Endpoint raiz nao deve consumir quota."""
        # Faz muitas requisicoes ao root
        for _ in range(20):
            await client.get("/")

        # Ainda deve poder fazer requisicao normal
        response = await client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": api_key},
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_rate_limit_por_ip(
        self,
        client: AsyncClient,
        api_key: str,
    ) -> None:
        """Rate limit deve ser por IP."""
        # Faz 10 requisicoes
        for _ in range(10):
            await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": api_key},
            )

        # 11a deve falhar
        response = await client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": api_key},
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @pytest.mark.asyncio
    async def test_deve_incluir_headers_rate_limit(
        self,
        client: AsyncClient,
        api_key: str,
    ) -> None:
        """Resposta deve incluir headers de rate limit."""
        response = await client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": api_key},
        )

        # Headers esperados
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

        # Valores corretos
        limit = int(response.headers["X-RateLimit-Limit"])
        remaining = int(response.headers["X-RateLimit-Remaining"])
        assert limit == 10
        assert remaining == 9  # Apos primeira requisicao


@pytest.mark.e2e
class TestRateLimitingEdgeCases:
    """Testes de casos limite do rate limiting."""

    @pytest.mark.asyncio
    async def test_requisicao_sem_autenticacao_nao_conta(
        self,
        client: AsyncClient,
        api_key: str,
    ) -> None:
        """Requisicoes sem autenticacao (401) nao devem contar."""
        # Faz requisicoes sem API key (devem retornar 401)
        for _ in range(15):
            await client.get("/quantitativointerrupcoesativas")

        # Requisicao autenticada deve funcionar
        response = await client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": api_key},
        )
        assert response.status_code == status.HTTP_200_OK
