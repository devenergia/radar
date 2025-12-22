"""Ponto de entrada da API 1 - Quantitativo de Interrupcoes Ativas."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.shared.infrastructure.config import get_settings
from backend.shared.infrastructure.database.oracle_pool import oracle_pool
from backend.shared.infrastructure.cache.memory_cache import memory_cache
from backend.shared.infrastructure.logger import configure_logging, get_logger

from backend.apps.api_interrupcoes.routes import router
from backend.apps.api_interrupcoes.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    ErrorHandlerMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicacao."""
    settings = get_settings()
    logger = get_logger("startup")

    # Startup
    logger.info("Iniciando API de Interrupcoes", version=settings.app_version)

    # Configurar logging
    configure_logging(
        level=settings.log_level,
        json_format=settings.log_format == "json",
    )

    # Inicializar pool de conexoes
    logger.info("Conectando ao banco de dados...")
    await oracle_pool.initialize(settings)
    logger.info("Pool de conexoes inicializado")

    # Inicializar cache
    await memory_cache.start()
    logger.info("Cache inicializado")

    yield

    # Shutdown
    logger.info("Encerrando aplicacao...")
    await memory_cache.stop()
    await oracle_pool.close()
    logger.info("Aplicacao encerrada")


def create_app() -> FastAPI:
    """Factory para criar a aplicacao FastAPI."""
    settings = get_settings()

    app = FastAPI(
        title="RADAR API - Interrupcoes",
        description="API para consulta de quantitativo de interrupcoes ativas no fornecimento de energia",
        version=settings.app_version,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["*"],
    )

    # Middlewares customizados (ordem inversa de execucao)
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Rotas
    app.include_router(router)

    return app


# Instancia da aplicacao
app = create_app()


def main() -> None:
    """Ponto de entrada para execucao via CLI."""
    settings = get_settings()

    uvicorn.run(
        "backend.apps.api_interrupcoes.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        workers=1 if settings.is_development else settings.workers,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
