"""Middlewares da API 1 - Interrupcoes."""

import time
import uuid
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.shared.infrastructure.http.aneel_response import AneelResponseBuilder
from backend.shared.infrastructure.logger import get_logger, log_request
from backend.shared.infrastructure.logging.audit import get_audit_logger

# Type alias para o callback do middleware
RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]


@dataclass
class RateLimitEntry:
    """Entrada de rate limit para um cliente."""

    count: int = 0
    window_start: float = field(default_factory=time.time)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para rate limiting conforme especificacao ANEEL (10 req/min)."""

    RATE_LIMIT = 10
    WINDOW_SECONDS = 60
    EXCLUDED_PATHS = frozenset(["/", "/health", "/docs", "/openapi.json", "/redoc"])

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self._clients: dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)

    def _get_client_key(self, request: Request) -> str:
        """Gera chave unica para o cliente (IP + API Key)."""
        client_ip = request.client.host if request.client else "unknown"
        api_key = request.headers.get("x-api-key", "")
        return f"{client_ip}:{api_key}"

    def _is_excluded_path(self, path: str) -> bool:
        """Verifica se o path esta excluido do rate limiting."""
        return path in self.EXCLUDED_PATHS

    def _should_skip_rate_limit(self, request: Request) -> bool:
        """Verifica se deve pular rate limiting (sem autenticacao)."""
        return "x-api-key" not in request.headers

    def _get_rate_limit_info(self, client_key: str) -> tuple[int, int]:
        """Retorna (remaining, retry_after) para o cliente."""
        entry = self._clients[client_key]
        current_time = time.time()

        # Reset window se expirou
        if current_time - entry.window_start >= self.WINDOW_SECONDS:
            entry.count = 0
            entry.window_start = current_time

        remaining = max(0, self.RATE_LIMIT - entry.count)
        retry_after = int(self.WINDOW_SECONDS - (current_time - entry.window_start))

        return remaining, max(1, retry_after)

    def _increment_counter(self, client_key: str) -> None:
        """Incrementa contador de requisicoes do cliente."""
        entry = self._clients[client_key]
        current_time = time.time()

        # Reset window se expirou
        if current_time - entry.window_start >= self.WINDOW_SECONDS:
            entry.count = 1
            entry.window_start = current_time
        else:
            entry.count += 1

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Aplica rate limiting nas requisicoes."""
        # Paths excluidos
        if self._is_excluded_path(request.url.path):
            return await call_next(request)

        # Requisicoes sem autenticacao nao contam
        if self._should_skip_rate_limit(request):
            return await call_next(request)

        client_key = self._get_client_key(request)
        remaining, retry_after = self._get_rate_limit_info(client_key)

        # Se excedeu o limite
        if remaining == 0:
            return JSONResponse(
                status_code=429,
                content={
                    "idcStatusRequisicao": 2,
                    "emailIndisponibilidade": "radar@roraimaenergia.com.br",
                    "mensagem": "Rate limit excedido. Limite: 10 requisicoes por minuto.",
                    "interrupcaoFornecimento": [],
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.RATE_LIMIT),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Incrementa contador
        self._increment_counter(client_key)

        # Processa requisicao
        response = await call_next(request)

        # Adiciona headers de rate limit
        new_remaining = max(0, self.RATE_LIMIT - self._clients[client_key].count)
        response.headers["X-RateLimit-Limit"] = str(self.RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(new_remaining)

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requisicoes."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
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
        self, request: Request, call_next: RequestResponseEndpoint
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


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware para auditoria de requisicoes conforme RAD-124."""

    EXCLUDED_PATHS = frozenset(["/", "/health", "/docs", "/openapi.json", "/redoc"])

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Audita todas as requisicoes."""
        audit = get_audit_logger()

        # Gerar request_id unico
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Paths excluidos
        if request.url.path in self.EXCLUDED_PATHS:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        # Extrair informacoes
        client_ip = self._get_client_ip(request)
        api_key = request.headers.get("x-api-key")
        method = request.method
        path = request.url.path

        # Log inicio
        audit.log_request(
            request_id=request_id,
            client_ip=client_ip,
            api_key=api_key,
            method=method,
            path=path,
        )

        # Processar
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log fim
            audit.log_response(
                request_id=request_id,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            # Headers de correlacao
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            audit.log_response(
                request_id=request_id,
                status_code=500,
                duration_ms=duration_ms,
                error=str(e),
            )
            raise

    def _get_client_ip(self, request: Request) -> str:
        """
        Obtem IP real do cliente.

        Considera headers de proxy reverso:
        - X-Forwarded-For
        - X-Real-IP
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
