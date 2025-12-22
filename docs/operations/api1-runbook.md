# Runbook Operacional - API 1 (Quantitativo de Interrupções Ativas)

## 1. Informações Gerais

| Campo | Valor |
|-------|-------|
| **Serviço** | API RADAR - Interrupções Ativas |
| **Criticidade** | Alta (Integração ANEEL) |
| **SLA** | 99.5% disponibilidade |
| **Horário Crítico** | 24x7 (polling ANEEL contínuo) |
| **Contato Principal** | radar@roraimaenergia.com.br |
| **Escalação** | Coordenação TI - (95) XXXX-XXXX |

## 2. Arquitetura de Serviços

```
┌─────────────────────────────────────────────────────────────┐
│                    Serviços da API                          │
├─────────────────────────────────────────────────────────────┤
│  NGINX         │  Port 443  │  Load Balancer/SSL           │
│  radar-api     │  Port 8001 │  FastAPI Application         │
│  redis         │  Port 6379 │  Cache Layer                 │
│  Oracle RADAR  │  Port 1521 │  Database                    │
│  Oracle SISTEC │  DBLink    │  Fonte de Dados (externo)    │
└─────────────────────────────────────────────────────────────┘
```

## 3. Procedimentos Operacionais

### 3.1 Verificação de Status

#### Verificar todos os serviços
```bash
# Docker
docker compose ps

# Systemd
systemctl status radar-api redis nginx

# Health check da API
curl -s http://localhost:8001/health | jq
```

#### Output esperado (healthy)
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-10T14:30:00Z",
  "dependencies": {
    "database": "healthy",
    "cache": "healthy"
  }
}
```

### 3.2 Iniciar/Parar Serviços

#### Docker Compose
```bash
# Iniciar todos os serviços
docker compose up -d

# Parar todos os serviços
docker compose down

# Reiniciar apenas a API
docker compose restart api

# Reiniciar com rebuild
docker compose up -d --build api
```

#### Systemd
```bash
# Iniciar
sudo systemctl start radar-api

# Parar
sudo systemctl stop radar-api

# Reiniciar
sudo systemctl restart radar-api

# Reiniciar graceful (sem downtime)
sudo systemctl reload radar-api
```

### 3.3 Visualização de Logs

#### Logs em tempo real
```bash
# Docker
docker compose logs -f api
docker compose logs -f --tail=100 api

# Systemd
sudo journalctl -u radar-api -f
sudo journalctl -u radar-api --since "1 hour ago"
```

#### Filtrar logs por nível
```bash
# Erros apenas
docker compose logs api 2>&1 | grep -i error

# Warnings e erros
docker compose logs api 2>&1 | grep -iE "(error|warning)"
```

#### Logs estruturados (JSON)
```bash
# Buscar por request_id específico
docker compose logs api 2>&1 | grep "request_id=abc123"

# Filtrar por endpoint
docker compose logs api 2>&1 | jq 'select(.endpoint == "/quantitativointerrupcoesativas")'
```

### 3.4 Gerenciamento de Cache

#### Verificar status do Redis
```bash
# Conectar ao Redis
docker compose exec redis redis-cli

# Comandos úteis
INFO                              # Informações gerais
DBSIZE                            # Quantidade de chaves
KEYS api1:*                       # Listar chaves do API1
GET api1:interrupcoes:cache       # Ver valor do cache
TTL api1:interrupcoes:cache       # Ver TTL restante
```

#### Limpar cache
```bash
# Limpar cache específico da API1
docker compose exec redis redis-cli DEL api1:interrupcoes:cache

# Limpar todo cache da API1
docker compose exec redis redis-cli KEYS "api1:*" | xargs docker compose exec redis redis-cli DEL

# Limpar todo o Redis (CUIDADO!)
docker compose exec redis redis-cli FLUSHDB
```

#### Forçar atualização do cache
```bash
# 1. Limpar cache
docker compose exec redis redis-cli DEL api1:interrupcoes:cache

# 2. Fazer requisição para popular novo cache
curl -H "x-api-key: $API_KEY" http://localhost:8001/quantitativointerrupcoesativas
```

### 3.5 Gerenciamento de Conexões

#### Verificar conexões Oracle
```bash
# Via aplicação
docker compose exec api python -c "
from backend.shared.infrastructure.database import engine
import asyncio
async def check():
    async with engine.connect() as conn:
        result = await conn.execute('SELECT 1 FROM DUAL')
        print('Oracle: OK')
asyncio.run(check())
"
```

#### Verificar pool de conexões
```bash
# Métricas do pool
curl -s http://localhost:8001/metrics | grep db_pool
```

#### Reset de conexões (emergência)
```bash
# Reiniciar aplicação para resetar pool
docker compose restart api
```

## 4. Procedimentos de Emergência

### 4.1 API Não Responde

**Sintomas**: HTTP 502/503, timeout, conexão recusada

**Diagnóstico**:
```bash
# 1. Verificar se container está rodando
docker compose ps api

# 2. Verificar logs de erro
docker compose logs --tail=50 api

# 3. Verificar uso de recursos
docker stats radar-api

# 4. Verificar health check interno
docker compose exec api curl -s http://localhost:8001/health
```

**Resolução**:
```bash
# Cenário 1: Container parado
docker compose up -d api

# Cenário 2: Out of Memory
docker compose restart api
# Considerar aumentar limite de memória

# Cenário 3: Deadlock/Hang
docker compose kill api
docker compose up -d api
```

### 4.2 Erro de Conexão com Oracle

**Sintomas**: Erro 500, mensagem "database connection failed"

**Diagnóstico**:
```bash
# 1. Verificar conectividade de rede
docker compose exec api ping -c 3 oracle-host

# 2. Testar porta Oracle
docker compose exec api nc -zv oracle-host 1521

# 3. Testar autenticação
docker compose exec api python -c "
import oracledb
conn = oracledb.connect(user='radar', password='xxx', dsn='host:1521/service')
print('OK')
"
```

**Resolução**:
```bash
# Cenário 1: Problema de rede
# Contatar equipe de infraestrutura

# Cenário 2: Credenciais inválidas
# Verificar e atualizar .env

# Cenário 3: DBLink SISTEC indisponível
# Notificar equipe responsável pelo SISTEC
# API retornará dados do cache (se disponível)
```

### 4.3 Redis Indisponível

**Sintomas**: Latência alta, sempre acessa banco

**Diagnóstico**:
```bash
# 1. Verificar container Redis
docker compose ps redis

# 2. Verificar conectividade
docker compose exec api redis-cli -h redis ping
```

**Resolução**:
```bash
# Reiniciar Redis
docker compose restart redis

# Se persistir, verificar logs
docker compose logs redis
```

### 4.4 Rate Limit Excedido

**Sintomas**: HTTP 429, "Too Many Requests"

**Diagnóstico**:
```bash
# Verificar requisições por IP/API key
grep "rate_limit" /var/log/nginx/radar_access.log | tail -20
```

**Resolução**:
```bash
# Cenário 1: ANEEL excedendo limite
# Verificar se frequência mudou (deveria ser 5 min)
# Contatar ANEEL se necessário

# Cenário 2: Tentativa de ataque
# Verificar IPs e bloquear se necessário
# Adicionar ao WAF/Firewall
```

### 4.5 Alto Consumo de Recursos

**Sintomas**: Lentidão, memory alerts

**Diagnóstico**:
```bash
# Recursos de containers
docker stats

# Top de processos
docker compose exec api top

# Conexões abertas
docker compose exec api netstat -an | grep ESTABLISHED | wc -l
```

**Resolução**:
```bash
# Cenário 1: Memory leak
docker compose restart api

# Cenário 2: Muitas conexões
# Verificar pool size e ajustar
# Possível ataque - verificar logs

# Cenário 3: Disco cheio
df -h
docker system prune -a  # Limpar imagens não usadas
```

## 5. Manutenção Programada

### 5.1 Atualização de Versão

```bash
# 1. Notificar stakeholders
# Email para ANEEL com janela de manutenção

# 2. Backup de configurações
cp .env .env.backup.$(date +%Y%m%d)

# 3. Pull nova versão
docker compose pull api

# 4. Deploy com zero downtime
docker compose up -d --no-deps api

# 5. Verificar health
curl -s http://localhost:8001/health | jq

# 6. Monitorar logs
docker compose logs -f api

# 7. Rollback se necessário
docker compose down api
docker tag ghcr.io/repo/radar:previous ghcr.io/repo/radar:latest
docker compose up -d api
```

### 5.2 Rotação de Logs

```bash
# Configurar logrotate
cat > /etc/logrotate.d/radar << EOF
/var/log/radar/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 radar radar
}
EOF
```

### 5.3 Backup de Configurações

```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/backup/radar/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Configurações
cp .env $BACKUP_DIR/
cp docker-compose.yml $BACKUP_DIR/
cp nginx/nginx.conf $BACKUP_DIR/

# Redis data
docker compose exec redis redis-cli BGSAVE
cp /var/lib/docker/volumes/radar_redis-data/_data/dump.rdb $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

## 6. Contatos de Escalação

### Nível 1 - Operações
| Contato | Responsabilidade | Telefone |
|---------|------------------|----------|
| Plantão NOC | Monitoramento 24x7 | (95) XXXX-XXXX |
| Email | Alertas automáticos | noc@roraimaenergia.com.br |

### Nível 2 - Desenvolvimento
| Contato | Responsabilidade | Telefone |
|---------|------------------|----------|
| Equipe RADAR | Suporte aplicação | radar@roraimaenergia.com.br |
| Tech Lead | Decisões técnicas | (95) XXXX-XXXX |

### Nível 3 - Infraestrutura
| Contato | Responsabilidade | Telefone |
|---------|------------------|----------|
| DBA Oracle | Problemas banco | (95) XXXX-XXXX |
| Infra/Rede | Conectividade | (95) XXXX-XXXX |

### Externos
| Contato | Responsabilidade | Email |
|---------|------------------|-------|
| ANEEL - SFE | Fiscalização | sfe@aneel.gov.br |
| SISTEC | Sistema fonte | sistec@roraimaenergia.com.br |

## 7. Checklist de Verificação Diária

```markdown
## Checklist Diário - API RADAR

Data: ___/___/______
Operador: _________________

### Verificações
- [ ] Health check OK (HTTP 200)
- [ ] Logs sem erros críticos
- [ ] Cache funcionando (TTL correto)
- [ ] Conexão Oracle OK
- [ ] Espaço em disco > 20%
- [ ] Memória < 80%
- [ ] CPU < 80%
- [ ] Certificado SSL válido

### Testes
- [ ] GET /health retorna healthy
- [ ] GET /quantitativointerrupcoesativas com API key retorna 200
- [ ] Tempo de resposta < 500ms

### Observações
_________________________________________________
_________________________________________________
```

## 8. Métricas de Monitoramento

| Métrica | Threshold Normal | Alerta | Crítico |
|---------|------------------|--------|---------|
| Response Time p95 | < 200ms | > 500ms | > 1000ms |
| Error Rate | < 0.1% | > 1% | > 5% |
| CPU Usage | < 50% | > 70% | > 90% |
| Memory Usage | < 60% | > 80% | > 95% |
| Cache Hit Rate | > 90% | < 70% | < 50% |
| DB Connections | < 20 | > 30 | > 40 |
| Request Rate | ~12/min | N/A | > 100/min |

## 9. Referências

- [Deployment Guide](../deployment/deployment-guide.md)
- [Troubleshooting Guide](./api1-troubleshooting.md)
- [Monitoring Documentation](./monitoring-metrics.md)
- [Especificação API ANEEL](../api-specs/API_01_QUANTITATIVO_INTERRUPCOES_ATIVAS.md)
