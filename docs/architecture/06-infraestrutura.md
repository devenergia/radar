# Infraestrutura - Projeto RADAR

## Topologia de Rede

```mermaid
flowchart TB
    subgraph Internet
        ANEEL[ANEEL<br/>200.193.x.x]
    end

    subgraph Firewall["Firewall / WAF"]
        FW[Regras:<br/>- Whitelist IP ANEEL<br/>- Rate Limit<br/>- HTTPS Only]
    end

    subgraph DMZ
        LB[Load Balancer<br/>Nginx/HAProxy]
    end

    subgraph AppServers["Servidores de Aplicação"]
        API1[RADAR API<br/>Node 01]
        API2[RADAR API<br/>Node 02]
    end

    subgraph DataCenter["Data Center"]
        subgraph DBServers["Servidores de Banco"]
            RADAR_DB[(RADAR DB<br/>Oracle 19c)]
            INSERVICE[(Inservice<br/>Oracle)]
            INDICADORES[(Indicadores<br/>Oracle)]
        end
    end

    ANEEL -->|HTTPS:443| FW
    FW --> LB
    LB --> API1
    LB --> API2
    API1 --> RADAR_DB
    API2 --> RADAR_DB
    RADAR_DB -.->|DBLink| INSERVICE
    RADAR_DB -.->|DBLink| INDICADORES

    style ANEEL fill:#e1f5fe
    style AppServers fill:#c8e6c9
    style DBServers fill:#fff3e0
```

## Docker Compose (Desenvolvimento)

```mermaid
flowchart LR
    subgraph DockerNetwork["docker-network: radar-network"]
        API[radar-api<br/>:3000]
        ORACLE[oracle-xe<br/>:1521]
        PROMETHEUS[prometheus<br/>:9090]
        GRAFANA[grafana<br/>:3001]
    end

    DEV[Developer] --> API
    DEV --> GRAFANA
    API --> ORACLE
    PROMETHEUS --> API
    GRAFANA --> PROMETHEUS

    style DockerNetwork fill:#e3f2fd
```

## CI/CD Pipeline

```mermaid
flowchart LR
    subgraph Trigger
        PUSH[Push to main]
        PR[Pull Request]
    end

    subgraph Build["Build Stage"]
        CHECKOUT[Checkout]
        INSTALL[npm install]
        LINT[ESLint + Prettier]
        BUILD[tsc build]
    end

    subgraph Test["Test Stage"]
        UNIT[Unit Tests]
        INTEG[Integration Tests]
        COV[Coverage Report]
    end

    subgraph Security["Security Stage"]
        AUDIT[npm audit]
        SNYK[Snyk scan]
    end

    subgraph Deploy["Deploy Stage"]
        DOCKER[Build Docker Image]
        PUSH_REG[Push to Registry]
        DEPLOY_STG[Deploy Staging]
        DEPLOY_PROD[Deploy Production]
    end

    PUSH --> CHECKOUT
    PR --> CHECKOUT
    CHECKOUT --> INSTALL
    INSTALL --> LINT
    LINT --> BUILD
    BUILD --> UNIT
    UNIT --> INTEG
    INTEG --> COV
    COV --> AUDIT
    AUDIT --> SNYK
    SNYK --> DOCKER
    DOCKER --> PUSH_REG
    PUSH_REG --> DEPLOY_STG
    DEPLOY_STG -->|Manual Approval| DEPLOY_PROD

    style Build fill:#e3f2fd
    style Test fill:#c8e6c9
    style Security fill:#fff3e0
    style Deploy fill:#fce4ec
```

## Monitoramento

```mermaid
flowchart TB
    subgraph Application
        API[RADAR API]
        METRICS[/metrics]
        HEALTH[/health]
        LOGS[Logs stdout]
    end

    subgraph Collection
        PROM[Prometheus]
        LOKI[Loki]
    end

    subgraph Visualization
        GRAFANA[Grafana]
    end

    subgraph Alerting
        ALERTMANAGER[AlertManager]
        EMAIL[Email]
        SLACK[Slack]
    end

    API --> METRICS
    API --> HEALTH
    API --> LOGS

    PROM -->|Scrape| METRICS
    PROM -->|Scrape| HEALTH
    LOKI -->|Collect| LOGS

    GRAFANA --> PROM
    GRAFANA --> LOKI

    PROM --> ALERTMANAGER
    ALERTMANAGER --> EMAIL
    ALERTMANAGER --> SLACK

    style Application fill:#c8e6c9
    style Collection fill:#e3f2fd
    style Visualization fill:#fff3e0
    style Alerting fill:#fce4ec
```

## Configuração de Ambiente

```mermaid
flowchart TB
    subgraph Development
        DEV_ENV[".env.development"]
        DEV_DB["Oracle XE Local<br/>ou Container"]
        DEV_CACHE["Memory Cache"]
    end

    subgraph Staging
        STG_ENV[".env.staging"]
        STG_DB["Oracle Staging<br/>(DBLinks para cópias)"]
        STG_CACHE["Memory Cache"]
    end

    subgraph Production
        PROD_ENV[".env.production<br/>(Secrets Manager)"]
        PROD_DB["Oracle Produção<br/>(DBLinks para sistemas reais)"]
        PROD_CACHE["Memory Cache<br/>(ou Redis cluster)"]
    end

    style Development fill:#e8f5e9
    style Staging fill:#fff3e0
    style Production fill:#ffebee
```

## Backup e Recuperação

```mermaid
flowchart LR
    subgraph Dados
        RADAR_DB[(RADAR DB)]
        HISTORICO[(Histórico<br/>Snapshots)]
    end

    subgraph Backup
        RMAN[Oracle RMAN]
        EXPORT[Data Pump Export]
    end

    subgraph Storage
        DISK[Disco Local]
        TAPE[Fita/Cloud]
    end

    subgraph Recovery
        RESTORE[Restore]
        POINT_IN_TIME[Point-in-Time<br/>Recovery]
    end

    RADAR_DB --> RMAN
    HISTORICO --> EXPORT
    RMAN --> DISK
    EXPORT --> DISK
    DISK --> TAPE
    TAPE --> RESTORE
    RESTORE --> POINT_IN_TIME

    style Dados fill:#e3f2fd
    style Backup fill:#fff3e0
    style Storage fill:#f5f5f5
    style Recovery fill:#c8e6c9
```

## Requisitos de Infraestrutura

| Componente | Desenvolvimento | Staging | Produção |
|------------|-----------------|---------|----------|
| **CPU** | 2 cores | 4 cores | 8 cores |
| **RAM** | 4 GB | 8 GB | 16 GB |
| **Disco** | 50 GB | 100 GB | 500 GB |
| **Node.js** | 20 LTS | 20 LTS | 20 LTS |
| **Oracle** | XE 21c | 19c | 19c Enterprise |
| **Instâncias** | 1 | 1 | 2+ (HA) |

## SLA e Disponibilidade

| Métrica | Meta | Medição |
|---------|------|---------|
| **Disponibilidade** | 99.5% | Uptime mensal |
| **Tempo de Resposta (p95)** | < 5s | Prometheus histogram |
| **Taxa de Erro** | < 0.1% | Contador de erros / total |
| **MTTR** | < 1 hora | Tempo para restaurar serviço |
| **RPO** | 30 minutos | Snapshots de histórico |
| **RTO** | 4 horas | Tempo para recuperação total |
