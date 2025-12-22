# Guia de Deployment - API RADAR

## 1. Visão Geral

Este documento descreve o processo de deployment da API RADAR em diferentes ambientes: desenvolvimento, homologação e produção.

## 2. Requisitos de Sistema

### 2.1 Hardware Mínimo

| Ambiente | CPU | RAM | Disco |
|----------|-----|-----|-------|
| Desenvolvimento | 2 cores | 4 GB | 20 GB |
| Homologação | 4 cores | 8 GB | 50 GB |
| Produção | 8 cores | 16 GB | 100 GB |

### 2.2 Software

| Componente | Versão | Observação |
|------------|--------|------------|
| Python | 3.11+ | Testado com 3.11.6 |
| Oracle Instant Client | 21.x | Para conexão Oracle |
| Redis | 7.x | Cache |
| Docker | 24.x | Containerização |
| Docker Compose | 2.x | Orquestração local |
| NGINX | 1.24+ | Reverse proxy/Load balancer |

### 2.3 Dependências Python

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
sqlalchemy[asyncio]>=2.0.23
oracledb>=2.0.0
redis>=5.0.0
structlog>=23.2.0
python-multipart>=0.0.6
httpx>=0.25.0
```

## 3. Configuração de Ambiente

### 3.1 Variáveis de Ambiente

Crie um arquivo `.env` baseado no template:

```bash
# .env.template

# === Aplicação ===
RADAR_APP_NAME=radar-api
RADAR_APP_VERSION=1.0.0
RADAR_DEBUG=false
RADAR_LOG_LEVEL=INFO

# === Servidor ===
RADAR_HOST=0.0.0.0
RADAR_PORT=8001
RADAR_WORKERS=4

# === Database Oracle ===
RADAR_DATABASE_URL=oracle+oracledb_async://user:pass@host:1521/?service_name=ORCL
RADAR_DATABASE_POOL_SIZE=10
RADAR_DATABASE_MAX_OVERFLOW=20
RADAR_DATABASE_POOL_TIMEOUT=30

# === Redis Cache ===
RADAR_REDIS_URL=redis://localhost:6379/0
RADAR_CACHE_TTL=300
RADAR_CACHE_PREFIX=api1

# === Autenticação ===
RADAR_API_KEY_HASH=sha256:abc123...
RADAR_API_KEY_HEADER=x-api-key

# === Rate Limiting ===
RADAR_RATE_LIMIT_REQUESTS=12
RADAR_RATE_LIMIT_WINDOW=60

# === CORS ===
RADAR_CORS_ORIGINS=["https://aneel.gov.br"]
RADAR_CORS_CREDENTIALS=true

# === Email de Contato ===
RADAR_EMAIL_INDISPONIBILIDADE=radar@roraimaenergia.com.br
```

### 3.2 Configuração por Ambiente

#### Desenvolvimento

```bash
# .env.development
RADAR_DEBUG=true
RADAR_LOG_LEVEL=DEBUG
RADAR_DATABASE_URL=oracle+oracledb_async://radar:radar_dev@localhost:1521/?service_name=XEPDB1
RADAR_REDIS_URL=redis://localhost:6379/0
RADAR_CORS_ORIGINS=["*"]
```

#### Homologação

```bash
# .env.homolog
RADAR_DEBUG=false
RADAR_LOG_LEVEL=INFO
RADAR_DATABASE_URL=oracle+oracledb_async://radar:${DB_PASS}@oracle-homolog:1521/?service_name=RADARH
RADAR_REDIS_URL=redis://redis-homolog:6379/0
RADAR_CORS_ORIGINS=["https://api-homolog.roraimaenergia.com.br"]
```

#### Produção

```bash
# .env.production
RADAR_DEBUG=false
RADAR_LOG_LEVEL=WARNING
RADAR_DATABASE_URL=oracle+oracledb_async://radar:${DB_PASS}@oracle-prod:1521/?service_name=RADARP
RADAR_REDIS_URL=redis://redis-prod:6379/0
RADAR_CORS_ORIGINS=["https://api.roraimaenergia.com.br"]
RADAR_WORKERS=8
```

## 4. Deployment com Docker

### 4.1 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Metadados
LABEL maintainer="radar@roraimaenergia.com.br"
LABEL version="1.0.0"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependências do sistema (Oracle Instant Client)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libaio1 \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Oracle Instant Client
WORKDIR /opt/oracle
RUN wget https://download.oracle.com/otn_software/linux/instantclient/2110000/instantclient-basic-linux.x64-21.10.0.0.0dbru.zip \
    && unzip instantclient-basic-linux.x64-21.10.0.0.0dbru.zip \
    && rm instantclient-basic-linux.x64-21.10.0.0.0dbru.zip

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_10:$LD_LIBRARY_PATH

# Aplicação
WORKDIR /app

# Copiar requirements primeiro (cache de layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY backend/ ./backend/

# Usuário não-root
RUN useradd -m -u 1000 radar && chown -R radar:radar /app
USER radar

# Porta
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8001/health').raise_for_status()"

# Comando de inicialização
CMD ["uvicorn", "backend.api1.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 4.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: radar-api
    ports:
      - "8001:8001"
    environment:
      - RADAR_DATABASE_URL=${RADAR_DATABASE_URL}
      - RADAR_REDIS_URL=redis://redis:6379/0
      - RADAR_LOG_LEVEL=${RADAR_LOG_LEVEL:-INFO}
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - radar-network
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  redis:
    image: redis:7-alpine
    container_name: radar-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - radar-network

  nginx:
    image: nginx:1.24-alpine
    container_name: radar-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - radar-network

volumes:
  redis-data:

networks:
  radar-network:
    driver: bridge
```

### 4.3 Configuração NGINX

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    # Rate limiting zone
    limit_req_zone $http_x_api_key zone=api_limit:10m rate=12r/m;

    # Upstream para API
    upstream radar_api {
        server api:8001;
        keepalive 32;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name api.roraimaenergia.com.br;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name api.roraimaenergia.com.br;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_prefer_server_ciphers off;

        # Security Headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Logging
        access_log /var/log/nginx/radar_access.log;
        error_log /var/log/nginx/radar_error.log;

        # API Location
        location /radar/v1/ {
            # Rate limiting
            limit_req zone=api_limit burst=5 nodelay;

            # Proxy settings
            proxy_pass http://radar_api/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";

            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check (sem rate limit)
        location /radar/v1/health {
            proxy_pass http://radar_api/health;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
        }
    }
}
```

## 5. Deployment Manual (sem Docker)

### 5.1 Preparação do Ambiente

```bash
# 1. Criar usuário de aplicação
sudo useradd -m -s /bin/bash radar
sudo su - radar

# 2. Instalar pyenv
curl https://pyenv.run | bash

# 3. Instalar Python 3.11
pyenv install 3.11.6
pyenv global 3.11.6

# 4. Criar diretório da aplicação
mkdir -p /opt/radar/api
cd /opt/radar/api

# 5. Clonar repositório
git clone https://github.com/roraimaenergia/radar.git .

# 6. Criar virtual environment
python -m venv venv
source venv/bin/activate

# 7. Instalar dependências
pip install -r requirements.txt

# 8. Configurar variáveis de ambiente
cp .env.template .env
# Editar .env com valores de produção
```

### 5.2 Systemd Service

```ini
# /etc/systemd/system/radar-api.service
[Unit]
Description=RADAR API - Interrupções de Energia
After=network.target

[Service]
Type=exec
User=radar
Group=radar
WorkingDirectory=/opt/radar/api
Environment="PATH=/opt/radar/api/venv/bin"
EnvironmentFile=/opt/radar/api/.env
ExecStart=/opt/radar/api/venv/bin/uvicorn backend.api1.main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --workers 4 \
    --log-level info
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 5.3 Ativar e Iniciar

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar início automático
sudo systemctl enable radar-api

# Iniciar serviço
sudo systemctl start radar-api

# Verificar status
sudo systemctl status radar-api

# Ver logs
sudo journalctl -u radar-api -f
```

## 6. Pipeline CI/CD

### 6.1 GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy RADAR API

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - 'Dockerfile'
      - 'requirements.txt'

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements-test.txt

      - name: Run tests
        run: pytest --cov=backend --cov-fail-under=80

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    outputs:
      version: ${{ steps.meta.outputs.version }}

    steps:
      - uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  deploy-homolog:
    needs: build
    runs-on: ubuntu-latest
    environment: homolog

    steps:
      - name: Deploy to Homolog
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.HOMOLOG_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_KEY }}
          script: |
            cd /opt/radar
            docker compose pull
            docker compose up -d
            docker compose logs --tail=50

  deploy-production:
    needs: [build, deploy-homolog]
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Deploy to Production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_KEY }}
          script: |
            cd /opt/radar
            docker compose pull
            docker compose up -d --no-deps api
            docker compose logs --tail=50
```

## 7. Rollback

### 7.1 Docker

```bash
# Listar versões disponíveis
docker images ghcr.io/roraimaenergia/radar --format "{{.Tag}}"

# Rollback para versão anterior
docker compose down
export IMAGE_TAG=sha-abc123  # Tag da versão anterior
docker compose up -d

# Verificar logs
docker compose logs -f api
```

### 7.2 Manual

```bash
# Listar tags do Git
git tag -l

# Checkout para versão anterior
git checkout v1.0.0

# Reinstalar dependências se necessário
pip install -r requirements.txt

# Reiniciar serviço
sudo systemctl restart radar-api
```

## 8. Verificação de Deployment

### 8.1 Checklist Pós-Deployment

```bash
# 1. Health check
curl -s https://api.roraimaenergia.com.br/radar/v1/health | jq

# 2. Teste de autenticação
curl -s -H "x-api-key: $API_KEY" \
  https://api.roraimaenergia.com.br/radar/v1/quantitativointerrupcoesativas | jq

# 3. Verificar logs
docker compose logs --tail=100 api | grep -i error

# 4. Verificar métricas
curl -s http://localhost:8001/metrics

# 5. Verificar conexão com Redis
docker compose exec redis redis-cli ping

# 6. Verificar conexão com Oracle
docker compose exec api python -c "
from backend.shared.infrastructure.database import get_session
import asyncio
async def test():
    async with get_session() as s:
        result = await s.execute('SELECT 1 FROM DUAL')
        print('Oracle OK:', result.scalar())
asyncio.run(test())
"
```

### 8.2 Smoke Tests

```bash
#!/bin/bash
# smoke_test.sh

API_URL="https://api.roraimaenergia.com.br/radar/v1"
API_KEY="${RADAR_API_KEY}"

echo "=== RADAR API Smoke Tests ==="

# Test 1: Health Check
echo -n "Health Check: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")
if [ "$HTTP_CODE" = "200" ]; then
    echo "PASS"
else
    echo "FAIL (HTTP $HTTP_CODE)"
    exit 1
fi

# Test 2: Auth Required
echo -n "Auth Required: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/quantitativointerrupcoesativas")
if [ "$HTTP_CODE" = "401" ]; then
    echo "PASS"
else
    echo "FAIL (HTTP $HTTP_CODE)"
    exit 1
fi

# Test 3: Valid Request
echo -n "Valid Request: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "x-api-key: $API_KEY" \
    "$API_URL/quantitativointerrupcoesativas")
if [ "$HTTP_CODE" = "200" ]; then
    echo "PASS"
else
    echo "FAIL (HTTP $HTTP_CODE)"
    exit 1
fi

# Test 4: Response Format
echo -n "Response Format: "
RESPONSE=$(curl -s -H "x-api-key: $API_KEY" "$API_URL/quantitativointerrupcoesativas")
if echo "$RESPONSE" | jq -e '.idcStatusRequisicao' > /dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL (Invalid JSON)"
    exit 1
fi

echo "=== All tests passed ==="
```

## 9. Troubleshooting de Deployment

| Problema | Causa Provável | Solução |
|----------|---------------|---------|
| Container não inicia | Oracle Client faltando | Verificar Dockerfile e LD_LIBRARY_PATH |
| Erro conexão Oracle | Firewall ou credenciais | Testar conectividade e credenciais |
| Erro conexão Redis | Redis não está rodando | `docker compose up redis` |
| 502 Bad Gateway | API não respondendo | Verificar logs da aplicação |
| SSL Error | Certificado inválido | Renovar certificado SSL |
| Memory Error | Limite de memória | Aumentar limite no docker-compose |

## 10. Referências

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [NGINX Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client.html)
