"""Validacao de whitelist de IP conforme especificacao ANEEL.

Este modulo implementa a validacao de IPs autorizados para acesso a API,
seguindo a especificacao do Oficio Circular 14/2025-SFE/ANEEL.

Bloco autorizado: 200.198.220.128/25 (128 enderecos)
Range: 200.198.220.128 a 200.198.220.255
"""

from __future__ import annotations

from ipaddress import IPv4Network, IPv6Network, ip_address, ip_network
from typing import TYPE_CHECKING, Any

from starlette.types import ASGIApp

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from backend.shared.infrastructure.logger import get_logger

if TYPE_CHECKING:
    from backend.shared.infrastructure.config import Settings

logger = get_logger("security.ip_whitelist")


class IpWhitelistConfig:
    """Configuracao de whitelist de IP.

    Gerencia a lista de redes permitidas, incluindo o bloco ANEEL
    e redes extras configuradas via environment.
    """

    # Bloco ANEEL conforme Oficio Circular 14/2025-SFE/ANEEL
    ANEEL_CIDR = "200.198.220.128/25"

    def __init__(self, settings: Settings | None = None) -> None:
        """Inicializa configuracao de whitelist.

        Args:
            settings: Configuracoes da aplicacao. Se None, usa get_settings().
        """
        self._settings = settings
        self._allowed_networks = self._load_networks()

    def _load_networks(self) -> list[IPv4Network | IPv6Network]:
        """Carrega redes permitidas.

        Returns:
            Lista de objetos ip_network representando as redes permitidas.
        """
        networks = [ip_network(self.ANEEL_CIDR)]

        # Adicionar redes extras do settings (para desenvolvimento/testes)
        if self._settings and self._settings.ip_whitelist_extra:
            for cidr in self._settings.ip_whitelist_extra.split(","):
                cidr = cidr.strip()
                if cidr:
                    try:
                        networks.append(ip_network(cidr))
                    except ValueError:
                        logger.warning(
                            "CIDR invalido ignorado",
                            cidr=cidr,
                        )

        return networks

    def is_allowed(self, ip: str) -> bool:
        """Verifica se IP esta na whitelist.

        Args:
            ip: Endereco IP a verificar.

        Returns:
            True se o IP esta em uma das redes permitidas, False caso contrario.
        """
        try:
            client_ip = ip_address(ip)
            return any(client_ip in network for network in self._allowed_networks)
        except ValueError:
            return False


class IpWhitelistMiddleware(BaseHTTPMiddleware):
    """Middleware para validar whitelist de IP.

    IMPORTANTE: Este middleware deve ser adicionado ANTES
    do middleware de autenticacao (API Key).
    """

    def __init__(self, app: ASGIApp, settings: Settings | None = None) -> None:
        """Inicializa middleware.

        Args:
            app: Aplicacao FastAPI/Starlette.
            settings: Configuracoes da aplicacao.
        """
        super().__init__(app)
        self._config = IpWhitelistConfig(settings)
        self._bypass_paths = {"/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(
        self, request: Request, call_next: Any
    ) -> JSONResponse | Any:
        """Processa requisicao validando IP.

        Args:
            request: Requisicao HTTP.
            call_next: Proximo handler na cadeia.

        Returns:
            Resposta HTTP (403 se IP nao autorizado, ou resposta do handler).
        """
        # Bypass para endpoints publicos
        if request.url.path in self._bypass_paths:
            return await call_next(request)

        # Obter IP do cliente
        client_ip = self._get_client_ip(request)

        # Validar whitelist
        if not self._config.is_allowed(client_ip):
            logger.warning(
                "Acesso negado - IP nao autorizado",
                client_ip=client_ip,
                path=request.url.path,
            )
            return self._forbidden_response(client_ip)

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Obtem IP real do cliente.

        Considera headers de proxy reverso:
        - X-Forwarded-For (lista de IPs, primeiro e o cliente original)
        - X-Real-IP

        Args:
            request: Requisicao HTTP.

        Returns:
            Endereco IP do cliente.
        """
        # Tentar X-Forwarded-For primeiro (lista de IPs separados por virgula)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Primeiro IP e o cliente original
            return forwarded_for.split(",")[0].strip()

        # Tentar X-Real-IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fallback para IP direto
        if request.client:
            return request.client.host

        return "unknown"

    def _forbidden_response(self, ip: str) -> JSONResponse:  # noqa: ARG002
        """Resposta no formato ANEEL para IP nao autorizado.

        Args:
            ip: IP que foi rejeitado.

        Returns:
            JSONResponse com status 403 e formato ANEEL.
        """
        return JSONResponse(
            status_code=403,
            content={
                "idcStatusRequisicao": 2,
                "desStatusRequisicao": "Acesso negado",
                "emailIndisponibilidade": "radar@roraimaenergia.com.br",
                "mensagem": "IP de origem nao autorizado",
                "interrupcaoFornecimento": [],
            },
        )


async def verify_ip_whitelist(request: Request) -> str:
    """Dependency para validar IP em rotas especificas.

    Pode ser usado como alternativa ao middleware para validar
    IP apenas em rotas especificas.

    Args:
        request: Requisicao HTTP.

    Returns:
        IP do cliente validado.

    Raises:
        HTTPException: 403 se IP nao autorizado.
    """
    config = IpWhitelistConfig()

    # Obter IP do cliente
    client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()

    if not client_ip and request.client:
        client_ip = request.client.host

    if not client_ip:
        client_ip = "unknown"

    if not config.is_allowed(client_ip):
        logger.warning(
            "Acesso negado via dependency - IP nao autorizado",
            client_ip=client_ip,
            path=request.url.path,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "idcStatusRequisicao": 2,
                "desStatusRequisicao": "Acesso negado",
                "emailIndisponibilidade": "radar@roraimaenergia.com.br",
                "mensagem": "IP de origem nao autorizado",
                "interrupcaoFornecimento": [],
            },
        )

    return client_ip
