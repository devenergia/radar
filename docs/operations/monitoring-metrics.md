# Monitoramento e Métricas - API RADAR

## 1. Visão Geral

Este documento descreve a estratégia de monitoramento e as métricas coletadas da API RADAR, incluindo configuração de alertas e dashboards.

## 2. Stack de Observabilidade

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Observability Stack                              │
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │    Logs      │    │   Metrics    │    │         Traces           │  │
│  │  structlog   │    │  Prometheus  │    │     OpenTelemetry        │  │
│  └──────┬───────┘    └──────┬───────┘    └────────────┬─────────────┘  │
│         │                   │                         │                 │
│         ▼                   ▼                         ▼                 │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                         Grafana                                   │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │  │
│  │  │ API Health │  │ Performance│  │  Business  │  │   Infra    │  │  │
│  │  │ Dashboard  │  │ Dashboard  │  │ Dashboard  │  │ Dashboard  │  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      Alertmanager                                 │  │
│  │        Email  │  Slack  │  PagerDuty  │  Teams                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3. Métricas da Aplicação

### 3.1 Métricas HTTP

| Métrica | Tipo | Labels | Descrição |
|---------|------|--------|-----------|
| `http_requests_total` | Counter | method, endpoint, status | Total de requisições |
| `http_request_duration_seconds` | Histogram | method, endpoint | Latência de requisições |
| `http_requests_in_progress` | Gauge | method, endpoint | Requisições em andamento |
| `http_request_size_bytes` | Histogram | method, endpoint | Tamanho das requisições |
| `http_response_size_bytes` | Histogram | method, endpoint | Tamanho das respostas |

### 3.2 Métricas de Negócio

| Métrica | Tipo | Labels | Descrição |
|---------|------|--------|-----------|
| `radar_interrupcoes_total` | Gauge | municipio, tipo | Total de interrupções ativas |
| `radar_ucs_afetadas_total` | Gauge | municipio | Total de UCs afetadas |
| `radar_equipes_campo_total` | Gauge | municipio | Total de equipes em campo |
| `radar_api_calls_aneel_total` | Counter | status | Chamadas da ANEEL |

### 3.3 Métricas de Cache

| Métrica | Tipo | Labels | Descrição |
|---------|------|--------|-----------|
| `cache_hits_total` | Counter | cache_type | Total de cache hits |
| `cache_misses_total` | Counter | cache_type | Total de cache misses |
| `cache_hit_ratio` | Gauge | cache_type | Razão hit/total |
| `cache_size_bytes` | Gauge | cache_type | Tamanho do cache |
| `cache_ttl_seconds` | Gauge | cache_type | TTL configurado |

### 3.4 Métricas de Banco de Dados

| Métrica | Tipo | Labels | Descrição |
|---------|------|--------|-----------|
| `db_connections_active` | Gauge | pool | Conexões ativas |
| `db_connections_idle` | Gauge | pool | Conexões ociosas |
| `db_connections_max` | Gauge | pool | Máximo de conexões |
| `db_query_duration_seconds` | Histogram | query | Duração das queries |
| `db_query_errors_total` | Counter | query, error_type | Erros de query |

## 4. Implementação de Métricas

### 4.1 Configuração Prometheus

```python
# backend/shared/infrastructure/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from fastapi import Response

# HTTP Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

REQUESTS_IN_PROGRESS = Gauge(
    'http_requests_in_progress',
    'HTTP requests in progress',
    ['method', 'endpoint']
)

# Business Metrics
INTERRUPCOES_TOTAL = Gauge(
    'radar_interrupcoes_total',
    'Total active interruptions',
    ['municipio', 'tipo']
)

UCS_AFETADAS = Gauge(
    'radar_ucs_afetadas_total',
    'Total affected consumer units',
    ['municipio']
)

# Cache Metrics
CACHE_HITS = Counter(
    'cache_hits_total',
    'Cache hits',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Cache misses',
    ['cache_type']
)

# Database Metrics
DB_CONNECTIONS = Gauge(
    'db_connections_active',
    'Active database connections',
    ['pool']
)

DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)
```

### 4.2 Middleware de Métricas

```python
# backend/shared/infrastructure/middleware/metrics.py
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from backend.shared.infrastructure.metrics import (
    REQUEST_COUNT, REQUEST_LATENCY, REQUESTS_IN_PROGRESS
)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        endpoint = request.url.path

        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as e:
            status = 500
            raise
        finally:
            duration = time.perf_counter() - start_time

            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()

            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            REQUESTS_IN_PROGRESS.labels(
                method=method,
                endpoint=endpoint
            ).dec()

        return response
```

### 4.3 Endpoint de Métricas

```python
# backend/api1/interfaces/http/routes/metrics.py
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()

@router.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

## 5. Configuração Prometheus

### 5.1 prometheus.yml

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts/*.yml'

scrape_configs:
  - job_name: 'radar-api'
    static_configs:
      - targets: ['api:8001']
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

### 5.2 Regras de Alerta

```yaml
# prometheus/alerts/api.yml
groups:
  - name: radar-api-alerts
    rules:
      # API Down
      - alert: APIDown
        expr: up{job="radar-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API RADAR está indisponível"
          description: "A API não está respondendo há mais de 1 minuto"

      # High Error Rate
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) /
          sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Alta taxa de erros na API"
          description: "Taxa de erros acima de 5% nos últimos 5 minutos"

      # High Latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Latência alta na API"
          description: "P95 de latência acima de 500ms"

      # Low Cache Hit Rate
      - alert: LowCacheHitRate
        expr: |
          sum(rate(cache_hits_total[5m])) /
          (sum(rate(cache_hits_total[5m])) + sum(rate(cache_misses_total[5m]))) < 0.7
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Taxa de cache hit baixa"
          description: "Cache hit rate abaixo de 70%"

      # Database Connection Pool Exhausted
      - alert: DBPoolExhausted
        expr: db_connections_active / db_connections_max > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Pool de conexões quase esgotado"
          description: "Mais de 90% do pool de conexões em uso"

      # No ANEEL Requests
      - alert: NoANEELRequests
        expr: |
          increase(radar_api_calls_aneel_total[15m]) == 0
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Sem requisições da ANEEL"
          description: "Nenhuma requisição da ANEEL nos últimos 15 minutos"
```

## 6. Dashboards Grafana

### 6.1 Dashboard API Health

```json
{
  "title": "RADAR API - Health",
  "panels": [
    {
      "title": "Request Rate",
      "type": "graph",
      "targets": [
        {
          "expr": "sum(rate(http_requests_total[1m]))",
          "legendFormat": "req/s"
        }
      ]
    },
    {
      "title": "Error Rate",
      "type": "graph",
      "targets": [
        {
          "expr": "sum(rate(http_requests_total{status=~\"5..\"}[1m])) / sum(rate(http_requests_total[1m])) * 100",
          "legendFormat": "error %"
        }
      ]
    },
    {
      "title": "Latency P50/P95/P99",
      "type": "graph",
      "targets": [
        {
          "expr": "histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
          "legendFormat": "p50"
        },
        {
          "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
          "legendFormat": "p95"
        },
        {
          "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
          "legendFormat": "p99"
        }
      ]
    },
    {
      "title": "API Status",
      "type": "stat",
      "targets": [
        {
          "expr": "up{job=\"radar-api\"}",
          "legendFormat": "Status"
        }
      ],
      "options": {
        "colorMode": "background",
        "graphMode": "none"
      }
    }
  ]
}
```

### 6.2 Dashboard Business Metrics

```json
{
  "title": "RADAR API - Business",
  "panels": [
    {
      "title": "Interrupções por Município",
      "type": "table",
      "targets": [
        {
          "expr": "radar_interrupcoes_total",
          "format": "table"
        }
      ]
    },
    {
      "title": "Total UCs Afetadas",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(radar_ucs_afetadas_total)",
          "legendFormat": "UCs"
        }
      ]
    },
    {
      "title": "Equipes em Campo",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(radar_equipes_campo_total)",
          "legendFormat": "Equipes"
        }
      ]
    },
    {
      "title": "Chamadas ANEEL (24h)",
      "type": "stat",
      "targets": [
        {
          "expr": "increase(radar_api_calls_aneel_total[24h])",
          "legendFormat": "Chamadas"
        }
      ]
    }
  ]
}
```

### 6.3 Dashboard Cache & DB

```json
{
  "title": "RADAR API - Cache & Database",
  "panels": [
    {
      "title": "Cache Hit Rate",
      "type": "gauge",
      "targets": [
        {
          "expr": "sum(rate(cache_hits_total[5m])) / (sum(rate(cache_hits_total[5m])) + sum(rate(cache_misses_total[5m]))) * 100"
        }
      ],
      "options": {
        "thresholds": {
          "steps": [
            {"value": 0, "color": "red"},
            {"value": 70, "color": "yellow"},
            {"value": 90, "color": "green"}
          ]
        }
      }
    },
    {
      "title": "DB Connections",
      "type": "graph",
      "targets": [
        {
          "expr": "db_connections_active",
          "legendFormat": "Active"
        },
        {
          "expr": "db_connections_idle",
          "legendFormat": "Idle"
        },
        {
          "expr": "db_connections_max",
          "legendFormat": "Max"
        }
      ]
    },
    {
      "title": "Query Duration",
      "type": "heatmap",
      "targets": [
        {
          "expr": "sum(rate(db_query_duration_seconds_bucket[5m])) by (le)"
        }
      ]
    }
  ]
}
```

## 7. Logging Estruturado

### 7.1 Configuração structlog

```python
# backend/shared/infrastructure/logging.py
import structlog
from structlog.stdlib import filter_by_level

def configure_logging(log_level: str = "INFO"):
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Uso
logger = structlog.get_logger(__name__)

async def get_interrupcoes():
    logger.info(
        "buscando_interrupcoes",
        cache_hit=True,
        municipios_count=15
    )
```

### 7.2 Campos de Log Padrão

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `timestamp` | string | ISO 8601 |
| `level` | string | DEBUG, INFO, WARNING, ERROR |
| `logger` | string | Nome do módulo |
| `message` | string | Descrição do evento |
| `request_id` | string | UUID da requisição |
| `duration_ms` | float | Duração em ms |
| `user_agent` | string | Client user agent |
| `remote_ip` | string | IP do cliente |

## 8. Tracing (OpenTelemetry)

### 8.1 Configuração

```python
# backend/shared/infrastructure/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

def configure_tracing(service_name: str, otlp_endpoint: str):
    provider = TracerProvider()
    processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=otlp_endpoint)
    )
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # Auto-instrumentation
    FastAPIInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
    RedisInstrumentor().instrument()
```

### 8.2 Spans Customizados

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def buscar_interrupcoes():
    with tracer.start_as_current_span("buscar_interrupcoes") as span:
        span.set_attribute("municipio_count", 15)

        with tracer.start_as_current_span("cache_lookup"):
            # Busca no cache
            pass

        with tracer.start_as_current_span("db_query"):
            # Query no banco
            pass
```

## 9. Alertas e Notificações

### 9.1 Configuração Alertmanager

```yaml
# alertmanager/alertmanager.yml
global:
  smtp_smarthost: 'smtp.roraimaenergia.com.br:587'
  smtp_from: 'alertas@roraimaenergia.com.br'
  smtp_auth_username: 'alertas'
  smtp_auth_password: '${SMTP_PASSWORD}'

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'

  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
      continue: true

    - match:
        severity: warning
      receiver: 'warning-alerts'

receivers:
  - name: 'default'
    email_configs:
      - to: 'noc@roraimaenergia.com.br'

  - name: 'critical-alerts'
    email_configs:
      - to: 'radar@roraimaenergia.com.br'
      - to: 'coordenacao-ti@roraimaenergia.com.br'
    # Adicionar Slack/PagerDuty para P1

  - name: 'warning-alerts'
    email_configs:
      - to: 'radar@roraimaenergia.com.br'
```

### 9.2 Níveis de Severidade

| Severidade | Descrição | Notificação | SLA Resposta |
|------------|-----------|-------------|--------------|
| Critical | Serviço indisponível | Email + Slack + PagerDuty | 15 min |
| Warning | Degradação de performance | Email + Slack | 1 hora |
| Info | Informativo | Dashboard apenas | N/A |

## 10. SLOs e SLIs

### 10.1 Service Level Indicators (SLIs)

| SLI | Descrição | Cálculo |
|-----|-----------|---------|
| Availability | % de tempo disponível | uptime / total_time |
| Latency | Tempo de resposta | p95 latência |
| Error Rate | Taxa de erros | errors / total_requests |
| Throughput | Vazão | requests / second |

### 10.2 Service Level Objectives (SLOs)

| SLO | Target | Window |
|-----|--------|--------|
| Availability | 99.5% | Mensal |
| Latency p95 | < 500ms | Diário |
| Error Rate | < 0.1% | Diário |
| Cache Hit Rate | > 90% | Semanal |

### 10.3 Error Budget

```
Error Budget = 100% - SLO
             = 100% - 99.5%
             = 0.5%

Tempo de indisponibilidade permitido (mensal):
= 30 dias * 24 horas * 60 minutos * 0.5%
= 216 minutos/mês
= 7.2 minutos/dia
```

## 11. Referências

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [OpenTelemetry Python](https://opentelemetry-python.readthedocs.io/)
- [SRE Book - Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
