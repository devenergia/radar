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

### Logging com Pino

Utilizaremos **Pino** (integrado ao Fastify) para logging estruturado em JSON.

```typescript
// src/shared/config/logger.config.ts

import pino from 'pino';

export const loggerConfig = {
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'development'
    ? { target: 'pino-pretty', options: { colorize: true } }
    : undefined,
  redact: ['headers.x-api-key', 'body.password'], // Ocultar dados sensíveis
  serializers: {
    req: (req) => ({
      method: req.method,
      url: req.url,
      headers: {
        'user-agent': req.headers['user-agent'],
        'x-request-id': req.headers['x-request-id'],
      },
      remoteAddress: req.ip,
    }),
    res: (res) => ({
      statusCode: res.statusCode,
    }),
  },
};
```

### Níveis de Log

| Nível | Uso |
|-------|-----|
| `fatal` | Erro irrecuperável, aplicação vai parar |
| `error` | Erro que afeta a requisição atual |
| `warn` | Situação anômala mas não crítica |
| `info` | Eventos importantes (requisições, startup) |
| `debug` | Informações detalhadas para debugging |
| `trace` | Muito detalhado (queries SQL, payloads) |

### Formato de Log

```json
{
  "level": 30,
  "time": 1702396800000,
  "pid": 12345,
  "hostname": "radar-api-01",
  "requestId": "abc123",
  "msg": "Request completed",
  "req": {
    "method": "GET",
    "url": "/quantitativointerrupcoesativas",
    "remoteAddress": "200.193.x.x"
  },
  "res": {
    "statusCode": 200
  },
  "responseTime": 234
}
```

### Campos Obrigatórios em Todo Log

```typescript
interface LogContext {
  requestId: string;      // ID único da requisição
  timestamp: string;      // ISO 8601
  service: string;        // "radar-api"
  environment: string;    // "production" | "staging" | "development"
}
```

### Métricas com Prometheus

```typescript
// src/infrastructure/metrics/prometheus.metrics.ts

import { Counter, Histogram, Gauge, Registry } from 'prom-client';

export const registry = new Registry();

// Contador de requisições
export const httpRequestsTotal = new Counter({
  name: 'http_requests_total',
  help: 'Total de requisições HTTP',
  labelNames: ['method', 'route', 'status_code'],
  registers: [registry],
});

// Histograma de latência
export const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duração das requisições HTTP em segundos',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5, 10],
  registers: [registry],
});

// Gauge de conexões de banco
export const dbConnectionsActive = new Gauge({
  name: 'db_connections_active',
  help: 'Conexões ativas no pool do banco',
  registers: [registry],
});

// Gauge de itens no cache
export const cacheSize = new Gauge({
  name: 'cache_items_total',
  help: 'Total de itens no cache',
  registers: [registry],
});

// Counter de cache hits/misses
export const cacheHits = new Counter({
  name: 'cache_hits_total',
  help: 'Total de cache hits',
  labelNames: ['endpoint'],
  registers: [registry],
});
```

### Endpoint de Métricas

```typescript
// GET /metrics
app.get('/metrics', async (request, reply) => {
  reply.header('Content-Type', registry.contentType);
  return registry.metrics();
});
```

### Health Check

```typescript
// src/interfaces/http/routes/health.routes.ts

interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  checks: {
    database: { status: string; latencyMs?: number };
    cache: { status: string; itemCount?: number };
  };
}

// GET /health
// Retorna 200 se healthy, 503 se unhealthy
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
- **Debugging**: Logs estruturados facilitam busca
- **Compliance**: Registro de auditoria para ANEEL
- **Proatividade**: Alertas antes que usuários percebam

### Negativas

- **Overhead**: Logging adiciona latência (mínima com Pino)
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

- [Pino - Fast Node.js Logger](https://getpino.io/)
- [Prometheus Metrics Best Practices](https://prometheus.io/docs/practices/naming/)
- [The Twelve-Factor App - Logs](https://12factor.net/logs)
