# Visão Geral do Sistema - Projeto RADAR

## Contexto do Sistema (C4 - Nível 1)

```mermaid
C4Context
    title Sistema RADAR - Diagrama de Contexto

    Person(aneel, "ANEEL", "Agência Nacional de Energia Elétrica")
    Person(operador, "Operador COD", "Centro de Operação da Distribuição")

    System(radar, "Sistema RADAR", "API REST que fornece dados de interrupções e demandas para a ANEEL")

    System_Ext(inservice, "Inservice", "Sistema técnico de gestão de interrupções")
    System_Ext(indicadores, "Indicadores", "Base de dados de universos e códigos IBGE")
    System_Ext(ajuri, "Ajuri", "Sistema comercial de gestão de clientes")

    Rel(aneel, radar, "Consulta dados", "HTTPS/REST")
    Rel(operador, radar, "Monitora", "HTTPS")
    Rel(radar, inservice, "Consulta eventos", "Oracle DBLink")
    Rel(radar, indicadores, "Consulta IBGE", "Oracle DBLink")
    Rel(radar, ajuri, "Consulta UCs", "Oracle DBLink")
```

## Arquitetura de Alto Nível

```mermaid
flowchart TB
    subgraph Internet
        ANEEL[ANEEL]
    end

    subgraph DMZ["DMZ - Zona Desmilitarizada"]
        LB[Load Balancer / WAF]
    end

    subgraph AppLayer["Camada de Aplicação"]
        API[RADAR API<br/>Node.js/Fastify]
        CACHE[(Cache<br/>Em Memória)]
    end

    subgraph DataLayer["Camada de Dados"]
        RADAR_DB[(Banco RADAR<br/>Oracle)]
    end

    subgraph SourceSystems["Sistemas Fonte"]
        INSERVICE[(Inservice<br/>Oracle)]
        INDICADORES[(Indicadores<br/>Oracle)]
        AJURI[(Ajuri<br/>Oracle)]
    end

    ANEEL -->|HTTPS| LB
    LB -->|HTTP| API
    API <-->|Read/Write| CACHE
    API <-->|SQL| RADAR_DB
    RADAR_DB -.->|DBLink| INSERVICE
    RADAR_DB -.->|DBLink| INDICADORES
    RADAR_DB -.->|DBLink| AJURI

    style ANEEL fill:#e1f5fe
    style API fill:#c8e6c9
    style RADAR_DB fill:#fff3e0
    style INSERVICE fill:#fce4ec
    style INDICADORES fill:#fce4ec
    style AJURI fill:#fce4ec
```

## Componentes do Sistema (C4 - Nível 2)

```mermaid
flowchart TB
    subgraph radar["Sistema RADAR"]
        subgraph interfaces["Interfaces (Adapters de Entrada)"]
            HTTP[HTTP Controllers]
            SWAGGER[Swagger UI]
            HEALTH[Health Check]
            METRICS[Prometheus Metrics]
        end

        subgraph application["Application (Casos de Uso)"]
            UC1[GetInterrupcoesAtivas]
            UC2[GetDemandas]
            UC3[GetDadosDemanda]
        end

        subgraph domain["Domain (Núcleo)"]
            ENT[Entities]
            VO[Value Objects]
            REPO_INT[Repository Interfaces]
            DS[Domain Services]
        end

        subgraph infrastructure["Infrastructure (Adapters de Saída)"]
            ORACLE[Oracle Connection]
            REPO_IMPL[Repository Implementations]
            CACHE_IMPL[Cache Implementation]
        end
    end

    HTTP --> UC1
    HTTP --> UC2
    HTTP --> UC3

    UC1 --> REPO_INT
    UC2 --> REPO_INT
    UC3 --> REPO_INT

    REPO_INT -.-> REPO_IMPL
    REPO_IMPL --> ORACLE
    REPO_IMPL --> CACHE_IMPL

    style domain fill:#e8f5e9
    style application fill:#e3f2fd
    style interfaces fill:#fff8e1
    style infrastructure fill:#fce4ec
```

## Stack Tecnológica

```mermaid
mindmap
    root((RADAR API))
        Runtime
            Node.js 20 LTS
            TypeScript 5.x
        Framework
            Fastify 4.x
            Pino Logger
        Database
            Oracle 19c
            oracledb driver
        Testing
            Vitest
            Testcontainers
        DevOps
            Docker
            GitHub Actions
        Monitoring
            Prometheus
            Grafana
```

## Fluxo de Deploy

```mermaid
flowchart LR
    subgraph Dev["Desenvolvimento"]
        CODE[Código] --> TEST[Testes]
        TEST --> BUILD[Build]
    end

    subgraph CI["CI/CD"]
        BUILD --> LINT[Lint]
        LINT --> UNIT[Unit Tests]
        UNIT --> INT[Integration Tests]
        INT --> IMAGE[Docker Image]
    end

    subgraph Envs["Ambientes"]
        IMAGE --> STG[Staging]
        STG --> |Aprovado| PROD[Production]
    end

    style Dev fill:#e3f2fd
    style CI fill:#fff3e0
    style Envs fill:#e8f5e9
```

## Requisitos Não-Funcionais

| Requisito | Especificação | Justificativa |
|-----------|---------------|---------------|
| **Disponibilidade** | 99.5% (24x7) | Exigência ANEEL |
| **Tempo de Resposta** | < 5 segundos | Exigência ANEEL |
| **Frequência de Consulta** | A cada 30 minutos | Padrão ANEEL |
| **Retenção de Dados** | 36 meses | Exigência ANEEL |
| **Histórico** | 7 dias para recuperação | A partir de Abril/2026 |
