"""Dependencias da API 1 - Interrupcoes."""

from fastapi import Header, HTTPException, Request

from backend.shared.infrastructure.config import get_settings
from backend.shared.infrastructure.logger import get_logger


async def verify_api_key(
    request: Request,
    x_api_key: str | None = Header(None, alias="x-api-key"),
) -> str:
    """
    Verifica a chave de API no header.

    Args:
        request: Request FastAPI
        x_api_key: Chave de API do header

    Returns:
        Chave de API validada

    Raises:
        HTTPException: Se a chave for invalida ou ausente
    """
    logger = get_logger("auth")
    settings = get_settings()

    if not x_api_key:
        logger.warning(
            "Requisicao sem API Key",
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )
        raise HTTPException(
            status_code=401,
            detail={
                "idcStatusRequisicao": 2,
                "desStatusRequisicao": "Erro",
                "emailIndisponibilidade": settings.email_indisponibilidade,
                "mensagem": "Header x-api-key e obrigatorio",
            },
        )

    if x_api_key != settings.api_key:
        logger.warning(
            "API Key invalida",
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )
        raise HTTPException(
            status_code=401,
            detail={
                "idcStatusRequisicao": 2,
                "desStatusRequisicao": "Erro",
                "emailIndisponibilidade": settings.email_indisponibilidade,
                "mensagem": "API Key invalida",
            },
        )

    return x_api_key


async def verify_ip_whitelist(request: Request) -> None:
    """
    Verifica se o IP do cliente esta na whitelist.

    Args:
        request: Request FastAPI

    Raises:
        HTTPException: Se o IP nao estiver na whitelist
    """
    settings = get_settings()
    logger = get_logger("auth")

    # Se whitelist for *, permite todos
    if "*" in settings.allowed_ips_list:
        return

    client_ip = request.client.host if request.client else None

    if client_ip and client_ip not in settings.allowed_ips_list:
        logger.warning(
            "IP nao autorizado",
            path=request.url.path,
            client_ip=client_ip,
            allowed_ips=settings.allowed_ips_list,
        )
        raise HTTPException(
            status_code=403,
            detail={
                "idcStatusRequisicao": 2,
                "desStatusRequisicao": "Erro",
                "emailIndisponibilidade": settings.email_indisponibilidade,
                "mensagem": "Acesso nao autorizado para este IP",
            },
        )
