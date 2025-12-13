"""Middlewares da API 1 - Interrupcoes."""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.shared.infrastructure.logger import get_logger, log_request
from backend.shared.infrastructure.http.aneel_response import AneelResponseBuilder


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requisicoes."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Loga todas as requisicoes."""
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000

        log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_ip=request.client.host if request.client else None,
        )

        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware para tratamento global de erros."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Trata excecoes nao capturadas."""
        logger = get_logger("error")

        try:
            return await call_next(request)
        except Exception as e:
            logger.error(
                "Erro nao tratado",
                error_type=type(e).__name__,
                error_message=str(e),
                path=request.url.path,
                exc_info=True,
            )

            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=500,
                content=AneelResponseBuilder.internal_error(),
            )
