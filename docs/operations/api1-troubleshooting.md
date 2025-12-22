# Guia de Troubleshooting - API 1 (Quantitativo de Interrupções Ativas)

## 1. Diagnóstico Rápido

### Fluxograma de Diagnóstico

```
                     ┌─────────────────────┐
                     │   API não responde  │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │  Container rodando? │
                     └──────────┬──────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │ NÃO             │                 │ SIM
              ▼                 │                 ▼
     ┌────────────────┐         │       ┌────────────────┐
     │ Verificar logs │         │       │  Health check  │
     │ de startup     │         │       │  responde?     │
     └────────────────┘         │       └───────┬────────┘
                                │               │
                                │     ┌─────────┼─────────┐
                                │     │ NÃO     │         │ SIM
                                │     ▼         │         ▼
                                │ ┌──────────┐  │  ┌──────────────┐
                                │ │ Verificar│  │  │ Verificar    │
                                │ │ recursos │  │  │ dependências │
                                │ │ (CPU/MEM)│  │  │ (Oracle/Redis)│
                                │ └──────────┘  │  └──────────────┘
                                │               │
                                └───────────────┘
```

### Comandos de Diagnóstico Rápido

```bash
# Script de diagnóstico completo
#!/bin/bash
echo "=== RADAR API Diagnostic ==="
echo ""

echo "1. Container Status:"
docker compose ps
echo ""

echo "2. Health Check:"
curl -s http://localhost:8001/health | jq
echo ""

echo "3. Last 10 Errors:"
docker compose logs --tail=100 api 2>&1 | grep -i error | tail -10
echo ""

echo "4. Resource Usage:"
docker stats --no-stream radar-api
echo ""

echo "5. Redis Status:"
docker compose exec -T redis redis-cli ping
echo ""

echo "6. Connection Test:"
curl -s -o /dev/null -w "HTTP: %{http_code}, Time: %{time_total}s\n" \
    -H "x-api-key: $API_KEY" \
    http://localhost:8001/quantitativointerrupcoesativas
```

## 2. Problemas Comuns e Soluções

### 2.1 HTTP 401 - Unauthorized

#### Sintomas
```json
{
  "idcStatusRequisicao": 2,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "API Key inválida ou ausente",
  "quantitativoInterrupcoesAtivas": []
}
```

#### Causas e Soluções

| Causa | Verificação | Solução |
|-------|-------------|---------|
| Header ausente | `curl -v` e verificar headers | Adicionar `x-api-key: <chave>` |
| Header incorreto | Verificar nome do header | Usar exatamente `x-api-key` |
| Chave inválida | Comparar com hash configurado | Verificar `.env` RADAR_API_KEY_HASH |
| Chave expirada | Verificar data de validade | Solicitar nova chave à ANEEL |

#### Comandos de Diagnóstico
```bash
# Verificar se header está chegando
docker compose logs api 2>&1 | grep -i "api.key\|auth\|401"

# Testar com verbose
curl -v -H "x-api-key: SUA_CHAVE" http://localhost:8001/quantitativointerrupcoesativas

# Verificar configuração
docker compose exec api printenv | grep API_KEY
```

### 2.2 HTTP 429 - Too Many Requests

#### Sintomas
```json
{
  "idcStatusRequisicao": 2,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "Limite de requisições excedido. Aguarde 60 segundos.",
  "quantitativoInterrupcoesAtivas": []
}
```

#### Causas e Soluções

| Causa | Verificação | Solução |
|-------|-------------|---------|
| ANEEL polling muito rápido | Verificar frequência | Contatar ANEEL (deveria ser 5 min) |
| Múltiplos sistemas usando mesma key | Verificar origem das requisições | Separar API keys por sistema |
| Ataque/Scanning | Analisar logs de acesso | Bloquear IP no WAF |
| Teste automatizado | Verificar ambiente | Usar ambiente de homologação |

#### Comandos de Diagnóstico
```bash
# Contar requisições por minuto
docker compose logs --since 5m api 2>&1 | grep "quantitativointerrupcoesativas" | wc -l

# Identificar origem
grep "quantitativointerrupcoesativas" /var/log/nginx/radar_access.log | \
    awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# Verificar configuração de rate limit
cat nginx/nginx.conf | grep -A5 "limit_req"
```

### 2.3 HTTP 500 - Internal Server Error

#### Sintomas
```json
{
  "idcStatusRequisicao": 2,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "Erro interno do servidor",
  "quantitativoInterrupcoesAtivas": []
}
```

#### Diagnóstico por Mensagem de Erro

##### Erro: "Erro de conexão com banco de dados"

```bash
# 1. Verificar conectividade
docker compose exec api python -c "
import oracledb
try:
    conn = oracledb.connect(
        user='radar',
        password='xxx',
        dsn='host:1521/service'
    )
    print('Conexão OK')
except Exception as e:
    print(f'Erro: {e}')
"

# 2. Verificar DNS/IP
docker compose exec api nslookup oracle-host
docker compose exec api ping -c 3 oracle-host

# 3. Verificar porta
docker compose exec api nc -zv oracle-host 1521

# 4. Verificar TNS
docker compose exec api tnsping RADAR
```

##### Erro: "DBLink indisponível"

```bash
# 1. Testar DBLink diretamente
docker compose exec api python -c "
from sqlalchemy import text
from backend.shared.infrastructure.database import get_session
import asyncio

async def test():
    async with get_session() as session:
        result = await session.execute(
            text('SELECT 1 FROM DUAL@DBLINK_SISTEC')
        )
        print('DBLink OK')

asyncio.run(test())
"

# 2. Verificar no banco Oracle
# Conectar via SQL*Plus e executar:
# SELECT * FROM DBA_DB_LINKS WHERE DB_LINK = 'DBLINK_SISTEC';
# SELECT * FROM DUAL@DBLINK_SISTEC;
```

##### Erro: "Timeout na consulta"

```bash
# 1. Verificar tempo de query
docker compose exec api python -c "
import time
from sqlalchemy import text
from backend.shared.infrastructure.database import get_session
import asyncio

async def test():
    start = time.time()
    async with get_session() as session:
        result = await session.execute(
            text('SELECT COUNT(*) FROM VW_INTERRUPCOES_ATIVAS')
        )
        print(f'Tempo: {time.time() - start:.2f}s')

asyncio.run(test())
"

# 2. Verificar plan de execução da query
# No Oracle: EXPLAIN PLAN FOR SELECT ...

# 3. Verificar se há locks
# SELECT * FROM V$LOCK WHERE BLOCK > 0;
```

### 2.4 HTTP 503 - Service Unavailable

#### Sintomas
- NGINX retorna 503
- API não responde ao health check

#### Causas e Soluções

| Causa | Verificação | Solução |
|-------|-------------|---------|
| Container morto | `docker compose ps` | `docker compose up -d api` |
| Aplicação em startup | Aguardar | Verificar logs de inicialização |
| Manutenção programada | Verificar schedule | Aguardar término |
| Recursos esgotados | `docker stats` | Reiniciar container |

### 2.5 Latência Alta

#### Sintomas
- Tempo de resposta > 500ms
- Timeouts ocasionais

#### Diagnóstico
```bash
# 1. Medir tempo de resposta
for i in {1..10}; do
    curl -s -o /dev/null -w "Time: %{time_total}s\n" \
        -H "x-api-key: $API_KEY" \
        http://localhost:8001/quantitativointerrupcoesativas
done

# 2. Verificar cache hit/miss
docker compose logs --tail=50 api 2>&1 | grep -i "cache"

# 3. Verificar tempo de query
docker compose logs --tail=50 api 2>&1 | grep -i "query_time\|duration"

# 4. Verificar recursos
docker stats --no-stream

# 5. Verificar conexões
docker compose exec api netstat -an | grep ESTABLISHED | wc -l
```

#### Soluções por Causa

| Causa | Indicador | Solução |
|-------|-----------|---------|
| Cache miss | Logs mostram "cache_miss" | Verificar TTL do Redis |
| Query lenta | Query > 200ms | Otimizar query, índices |
| Pool esgotado | Conexões no limite | Aumentar pool size |
| CPU alta | > 80% | Aumentar recursos ou replicas |
| Rede lenta | Ping alto para Oracle | Verificar com infra |

### 2.6 Dados Desatualizados

#### Sintomas
- Interrupções não aparecem na API
- Dados diferentes do SISTEC

#### Diagnóstico
```bash
# 1. Verificar timestamp do cache
docker compose exec redis redis-cli TTL api1:interrupcoes:cache

# 2. Forçar atualização
docker compose exec redis redis-cli DEL api1:interrupcoes:cache
curl -H "x-api-key: $API_KEY" http://localhost:8001/quantitativointerrupcoesativas

# 3. Comparar com banco
docker compose exec api python -c "
from sqlalchemy import text
from backend.shared.infrastructure.database import get_session
import asyncio

async def test():
    async with get_session() as session:
        result = await session.execute(
            text('SELECT COUNT(*) FROM VW_INTERRUPCOES_ATIVAS@DBLINK_SISTEC')
        )
        print(f'Interrupções no SISTEC: {result.scalar()}')

asyncio.run(test())
"
```

### 2.7 Redis Problemas

#### Conexão recusada
```bash
# Verificar container
docker compose ps redis

# Verificar logs
docker compose logs redis

# Reiniciar
docker compose restart redis

# Verificar memória
docker compose exec redis redis-cli INFO memory
```

#### Cache não persiste
```bash
# Verificar configuração de persistência
docker compose exec redis redis-cli CONFIG GET save

# Verificar arquivo dump
ls -la /var/lib/docker/volumes/radar_redis-data/_data/

# Forçar save
docker compose exec redis redis-cli BGSAVE
```

## 3. Análise de Logs

### 3.1 Estrutura de Logs

```json
{
  "timestamp": "2025-12-10T14:30:00.123Z",
  "level": "INFO",
  "logger": "backend.api1.routes.interrupcoes",
  "message": "requisicao_processada",
  "request_id": "abc123",
  "duration_ms": 45,
  "cache_hit": true,
  "status_code": 200
}
```

### 3.2 Queries de Log Úteis

```bash
# Erros das últimas 24 horas
docker compose logs --since 24h api 2>&1 | grep '"level":"ERROR"'

# Requisições lentas (> 500ms)
docker compose logs api 2>&1 | jq 'select(.duration_ms > 500)'

# Taxa de cache hit
docker compose logs --since 1h api 2>&1 | \
    jq 'select(.message == "requisicao_processada")' | \
    jq -s '[.[].cache_hit] | (map(select(. == true)) | length) / length * 100'

# Erros por tipo
docker compose logs --since 1h api 2>&1 | \
    jq 'select(.level == "ERROR") | .error_type' | \
    sort | uniq -c

# Timeline de erros
docker compose logs --since 1h api 2>&1 | \
    jq -r 'select(.level == "ERROR") | "\(.timestamp) \(.message)"'
```

### 3.3 Correlação de Logs

```bash
# Rastrear uma requisição específica
REQUEST_ID="abc123"
docker compose logs api 2>&1 | grep "$REQUEST_ID"

# Incluir logs do NGINX
grep "$REQUEST_ID" /var/log/nginx/radar_access.log
```

## 4. Ferramentas de Diagnóstico

### 4.1 Endpoint de Diagnóstico (Interno)

```bash
# Se implementado /debug endpoint (apenas rede interna)
curl http://localhost:8001/debug/connections
curl http://localhost:8001/debug/cache-stats
curl http://localhost:8001/debug/config
```

### 4.2 Profiling

```bash
# CPU profiling
docker compose exec api py-spy record -o profile.svg --pid 1

# Memory profiling
docker compose exec api memray run -o memory.bin python -m backend.api1.main

# Async profiling
docker compose exec api python -c "
import asyncio
import cProfile
from backend.api1.main import app
# ... profile async code
"
```

### 4.3 Network Debugging

```bash
# Capturar tráfego
docker compose exec api tcpdump -i eth0 -w capture.pcap port 1521

# Verificar conexões
docker compose exec api ss -tuln

# DNS resolution
docker compose exec api dig oracle-host
```

## 5. Matriz de Decisão

### Quando Escalar

| Situação | Ação | Contato |
|----------|------|---------|
| API down > 5 min | Escalar Nível 2 | Equipe RADAR |
| Erro Oracle persistente | Escalar DBA | DBA Oracle |
| Problema de rede | Escalar Infra | Infra/Rede |
| Ataque suspeito | Escalar Segurança | Security Team |
| Reclamação ANEEL | Escalar Gestão | Coordenação |

### Prioridade de Resolução

| Impacto | Urgência | Prioridade |
|---------|----------|------------|
| ANEEL sem dados | Alta | P1 - Crítica |
| Latência alta | Média | P2 - Alta |
| Cache miss alto | Baixa | P3 - Média |
| Log verbose | Baixa | P4 - Baixa |

## 6. Checklists de Resolução

### Após Resolver Incidente

```markdown
## Checklist Pós-Incidente

- [ ] Serviço restaurado e verificado
- [ ] Root cause identificada
- [ ] Ação corretiva aplicada
- [ ] Logs coletados para análise
- [ ] Stakeholders notificados
- [ ] Documentação atualizada
- [ ] Post-mortem agendado (se P1/P2)
```

### Antes de Escalar

```markdown
## Checklist Pré-Escalação

- [ ] Logs coletados
- [ ] Diagnóstico básico executado
- [ ] Tentativas de resolução documentadas
- [ ] Impacto quantificado
- [ ] Timeline do incidente
- [ ] Request IDs afetados
```

## 7. Referências

- [Runbook Operacional](./api1-runbook.md)
- [Deployment Guide](../deployment/deployment-guide.md)
- [Monitoring Documentation](./monitoring-metrics.md)
- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Oracle ORA Errors](https://docs.oracle.com/en/error-help/db/)
