"""Rotas da API 1 - Quantitativo de Interrupcoes Ativas."""

from fastapi import APIRouter, Depends, Header

from backend.shared.infrastructure.http.aneel_response import AneelResponseBuilder
from backend.shared.infrastructure.config import Settings, get_settings

from backend.apps.api_interrupcoes.dependencies import verify_api_key
from backend.apps.api_interrupcoes.use_cases.get_interrupcoes_ativas import (
    GetInterrupcoesAtivasUseCase,
    get_interrupcoes_ativas_use_case,
)
from backend.apps.api_interrupcoes.schemas import (
    InterrupcoesAtivasResponse,
    HealthResponse,
)

router = APIRouter()


@router.get(
    "/quantitativointerrupcoesativas",
    response_model=InterrupcoesAtivasResponse,
    summary="Quantitativo de Interrupcoes Ativas",
    description="""
    Retorna o quantitativo de interrupcoes ativas no fornecimento de energia,
    agregado por municipio e conjunto eletrico.

    **Autenticacao**: Header `x-api-key` obrigatorio.

    **Formato de Resposta**: Padrao ANEEL conforme Oficio Circular 14/2025-SFE/ANEEL.
    """,
    tags=["Interrupcoes"],
)
async def get_quantitativo_interrupcoes_ativas(
    x_api_key: str = Depends(verify_api_key),
    use_case: GetInterrupcoesAtivasUseCase = Depends(get_interrupcoes_ativas_use_case),
) -> dict:
    """
    Endpoint principal para consulta de interrupcoes ativas.

    Retorna dados agregados por municipio e conjunto eletrico,
    separando interrupcoes programadas e nao programadas.
    """
    result = await use_case.execute()

    if result.is_failure:
        return AneelResponseBuilder.error(result.error)

    return AneelResponseBuilder.success(
        {"interrupcaoFornecimento": [item.model_dump() for item in result.value]}
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Verifica o status de saude da aplicacao.",
    tags=["Sistema"],
)
async def health_check(
    settings: Settings = Depends(get_settings),
) -> dict:
    """Endpoint de health check."""
    from backend.shared.infrastructure.database.oracle_pool import oracle_pool
    from backend.shared.infrastructure.cache.memory_cache import memory_cache

    db_health = await oracle_pool.health_check()
    cache_stats = memory_cache.get_stats()

    status = "healthy" if db_health["healthy"] else "unhealthy"

    return {
        "status": status,
        "version": settings.app_version,
        "checks": {
            "database": db_health,
            "cache": {
                "status": "up",
                "item_count": cache_stats.item_count,
                "hit_rate": round(cache_stats.hit_rate, 2),
            },
        },
    }


@router.get(
    "/",
    summary="Root",
    description="Informacoes basicas da API.",
    tags=["Sistema"],
)
async def root(settings: Settings = Depends(get_settings)) -> dict:
    """Endpoint raiz com informacoes da API."""
    return {
        "api": "RADAR - Interrupcoes Ativas",
        "version": settings.app_version,
        "docs": "/docs" if settings.is_development else None,
    }
