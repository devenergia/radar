# ADR-009: Logging e Monitoramento

## Status

Aceito

## Data

2025-12-12

## Contexto

A API RADAR é uma aplicação crítica com requisitos regulatórios. Precisamos de:

1. **Auditoria**: Registrar todas as requisições para compliance
2. **Debugging**: Facilitar identificação de problemas
3. **Monitoramento**: Métricas de performance e disponibilidade
4. **Alertas**: Notificação proativa de problemas

## Decisão

### Logging com Structlog

Utilizaremos **structlog** para logging estruturado em JSON, com integração ao uvicorn.

```python
# app/core/logging.py

import logging
import structlog
from typing import Any

def setup_logging(log_level: str = "INFO") -> None:
    """Configura logging estruturado com structlog"""

    # Procesadores compartilhados
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    # Configuração para produção (JSON)
    if log_level != "DEBUG":
        structlog.configure(
            processors=shared_processors + [
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    # Configuração para desenvolvimento (colorido)
    else:
        structlog.configure(
            processors=shared_processors + [
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    # Configurar logging padrão do Python
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=[logging.StreamHandler()]
    )


def get_logger(name: str) -> Any:
    """Retorna logger estruturado"""
    return structlog.get_logger(name)
```

### Middleware de Logging

```python
# app/infrastructure/http/middlewares/logging_middleware.py

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers
from app.core.logging import get_logger

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requisições"""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Gerar request ID
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))

        # Adicionar ao contexto
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=self._get_client_ip(request),
        )

        # Logar início da requisição
        logger.info(
            "request_started",
            user_agent=request.headers.get("user-agent"),
            api_key_masked=self._mask_api_key(
                request.headers.get("x-api-key", "")
            )
        )

        # Processar requisição
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Logar fim da requisição
        logger.info(
            "request_completed",
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2)
        )

        # Adicionar request ID ao header de resposta
        response.headers["X-Request-ID"] = request_id

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extrai IP real do cliente"""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _mask_api_key(self, api_key: str) -> str:
        """Mascara API key para logs"""
        if not api_key or len(api_key) <= 8:
            return "****"
        return f"{api_key[:4]}...{api_key[-4:]}"
```

### Níveis de Log

| Nível | Uso |
|-------|-----|
| `critical` | Erro irrecuperável, aplicação vai parar |
| `error` | Erro que afeta a requisição atual |
| `warning` | Situação anômala mas não crítica |
| `info` | Eventos importantes (requisições, startup) |
| `debug` | Informações detalhadas para debugging |

### Formato de Log

```json
{
  "event": "request_completed",
  "timestamp": "2025-12-12T10:30:45.123456Z",
  "level": "info",
  "logger": "app.middleware.logging",
  "request_id": "abc123-def456-ghi789",
  "method": "GET",
  "url": "/quantitativointerrupcoesativas",
  "client_ip": "200.193.x.x",
  "status_code": 200,
  "duration_ms": 234.56,
  "api_key_masked": "abcd...xyz"
}
```

### Campos Obrigatórios em Todo Log

```python
from dataclasses import dataclass

@dataclass
class LogContext:
    """Contexto obrigatório em logs"""
    request_id: str      # ID único da requisição
    timestamp: str       # ISO 8601
    service: str = "radar-api"
    environment: str = "production"  # production | staging | development
```

### Métricas com Prometheus

```python
# app/infrastructure/metrics/prometheus_metrics.py

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

# Registry customizado
registry = CollectorRegistry()

# Contador de requisições
http_requests_total = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'route', 'status_code'],
    registry=registry
)

# Histograma de latência
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP em segundos',
    ['method', 'route', 'status_code'],
    buckets=[0.1, 0.5, 1, 2, 5, 10],
    registry=registry
)

# Gauge de conexões de banco
db_connections_active = Gauge(
    'db_connections_active',
    'Conexões ativas no pool do banco',
    registry=registry
)

# Gauge de itens no cache
cache_items_total = Gauge(
    'cache_items_total',
    'Total de itens no cache',
    registry=registry
)

# Counter de cache hits/misses
cache_hits_total = Counter(
    'cache_hits_total',
    'Total de cache hits',
    ['endpoint'],
    registry=registry
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total de cache misses',
    ['endpoint'],
    registry=registry
)
```

### Middleware de Métricas

```python
# app/infrastructure/http/middlewares/metrics_middleware.py

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.infrastructure.metrics.prometheus_metrics import (
    http_requests_total,
    http_request_duration_seconds
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para coletar métricas Prometheus"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        # Registrar métricas
        route = request.url.path
        method = request.method
        status_code = response.status_code

        http_requests_total.labels(
            method=method,
            route=route,
            status_code=status_code
        ).inc()

        http_request_duration_seconds.labels(
            method=method,
            route=route,
            status_code=status_code
        ).observe(duration)

        return response
```

### Endpoint de Métricas

```python
# app/infrastructure/http/routes/metrics.py

from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.infrastructure.metrics.prometheus_metrics import registry

router = APIRouter()

@router.get("/metrics")
async def metrics():
    """Endpoint de métricas Prometheus"""
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )
```

### Health Check

```python
# app/infrastructure/http/routes/health.py

from typing import Literal
from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime
from app.infrastructure.database import check_database_health
from app.infrastructure.cache import get_cache_stats

router = APIRouter()

class HealthCheck(BaseModel):
    """Schema de health check"""
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime
    version: str
    checks: dict

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Endpoint de health check"""
    checks = {}
    overall_status = "healthy"

    # Verificar banco de dados
    db_check = await check_database_health()
    checks["database"] = db_check
    if db_check["status"] != "healthy":
        overall_status = "degraded"

    # Verificar cache
    cache_stats = get_cache_stats()
    checks["cache"] = cache_stats

    response_status = (
        status.HTTP_200_OK if overall_status == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return HealthCheck(
        status=overall_status,
        timestamp=datetime.now(),
        version="1.0.0",
        checks=checks
    )
```

### Alertas Recomendados

| Alerta | Condição | Severidade |
|--------|----------|------------|
| Alta Latência | p95 > 3s por 5 min | Warning |
| Erro Rate Alto | > 5% erros em 5 min | Critical |
| DB Connection Failed | Pool sem conexões | Critical |
| Cache Miss Rate Alto | > 90% miss em 15 min | Warning |
| API Indisponível | Health check falhou 3x | Critical |

## Consequências

### Positivas

- **Observabilidade**: Visão completa do comportamento da aplicação
- **Debugging**: Logs estruturados facilitam busca e análise
- **Compliance**: Registro de auditoria para ANEEL
- **Proatividade**: Alertas antes que usuários percebam
- **Contexto**: Request ID permite rastrear requisições completas

### Negativas

- **Overhead**: Logging adiciona latência (mínima com structlog)
- **Armazenamento**: Logs consomem espaço em disco
- **Complexidade**: Configurar stack de monitoramento

### Neutras

- Necessidade de rotação de logs
- Integração com ferramentas de observabilidade (Grafana, etc.)

## Retenção de Logs

| Tipo | Retenção |
|------|----------|
| Logs de aplicação | 30 dias |
| Logs de auditoria (requisições) | 365 dias |
| Métricas | 90 dias |

## Referências

- [Structlog Documentation](https://www.structlog.org/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Prometheus Metrics Best Practices](https://prometheus.io/docs/practices/naming/)
- [The Twelve-Factor App - Logs](https://12factor.net/logs)
