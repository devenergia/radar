# Arquitetura Hexagonal - Projeto RADAR

## Visão Geral

A arquitetura hexagonal (Ports and Adapters) isola o domínio de negócio das tecnologias externas.

```mermaid
flowchart TB
    subgraph External["Mundo Externo"]
        ANEEL[ANEEL]
        SWAGGER[Swagger UI]
        PROMETHEUS[Prometheus]
        ORACLE[(Oracle DBs)]
    end

    subgraph Hexagon["Hexágono da Aplicação"]
        subgraph DrivingAdapters["Adapters de Entrada (Driving)"]
            HTTP[HTTP Controller]
            HEALTH[Health Controller]
            METRICS[Metrics Controller]
        end

        subgraph Ports["Portas"]
            subgraph DrivingPorts["Portas de Entrada"]
                P1[InterrupcoesPort]
                P2[DemandasPort]
                P3[HealthPort]
            end

            subgraph DrivenPorts["Portas de Saída"]
                P4[InterrupcaoRepository]
                P5[UniversoRepository]
                P6[CachePort]
            end
        end

        subgraph Core["Núcleo (Domain + Application)"]
            UC[Use Cases]
            DOM[Domain]
        end

        subgraph DrivenAdapters["Adapters de Saída (Driven)"]
            REPO[OracleRepositories]
            CACHE[MemoryCache]
        end
    end

    ANEEL -->|REST| HTTP
    SWAGGER -->|REST| HTTP
    PROMETHEUS -->|Scrape| METRICS

    HTTP --> P1
    HTTP --> P2
    HEALTH --> P3

    P1 --> UC
    P2 --> UC
    P3 --> UC

    UC --> DOM
    UC --> P4
    UC --> P5
    UC --> P6

    P4 -.-> REPO
    P5 -.-> REPO
    P6 -.-> CACHE

    REPO -->|DBLink| ORACLE

    style Core fill:#c8e6c9
    style DrivingAdapters fill:#fff3e0
    style DrivenAdapters fill:#e1f5fe
    style Ports fill:#f3e5f5
```

## Estrutura de Diretórios

```mermaid
flowchart TB
    subgraph src["src/"]
        subgraph domain["domain/ - Núcleo"]
            entities["entities/<br/>Entidades de negócio"]
            valueObjects["value-objects/<br/>Objetos de valor"]
            repositories["repositories/<br/>Interfaces (Ports)"]
            services["services/<br/>Serviços de domínio"]
        end

        subgraph application["application/ - Casos de Uso"]
            useCases["use-cases/<br/>Implementação dos casos de uso"]
            dtos["dtos/<br/>Data Transfer Objects"]
            mappers["mappers/<br/>Conversores"]
        end

        subgraph infrastructure["infrastructure/ - Adapters de Saída"]
            database["database/<br/>Conexão Oracle"]
            repoImpl["repositories/<br/>Implementações"]
            cache["cache/<br/>Implementação de cache"]
        end

        subgraph interfaces["interfaces/ - Adapters de Entrada"]
            http["http/<br/>Controllers, Routes, Middlewares"]
        end

        subgraph shared["shared/ - Compartilhado"]
            config["config/"]
            errors["errors/"]
            utils["utils/"]
        end
    end

    style domain fill:#c8e6c9
    style application fill:#e3f2fd
    style infrastructure fill:#e1f5fe
    style interfaces fill:#fff3e0
    style shared fill:#f5f5f5
```

## Regra de Dependência

```mermaid
flowchart TB
    subgraph Camadas
        I[Interfaces<br/>Controllers] --> A[Application<br/>Use Cases]
        INF[Infrastructure<br/>Repositories] --> A
        A --> D[Domain<br/>Entities, Services]
    end

    subgraph Regra["Regra de Dependência"]
        R1["✓ Interfaces → Application → Domain"]
        R2["✓ Infrastructure → Application → Domain"]
        R3["✗ Domain NÃO conhece outras camadas"]
    end

    style D fill:#c8e6c9
    style A fill:#e3f2fd
    style I fill:#fff3e0
    style INF fill:#e1f5fe
```

## Exemplo: Fluxo GetInterrupcoesAtivas

```mermaid
sequenceDiagram
    autonumber
    participant C as Controller<br/>(interfaces)
    participant UC as UseCase<br/>(application)
    participant R as Repository<br/>(domain interface)
    participant RI as RepositoryImpl<br/>(infrastructure)
    participant DB as Oracle<br/>(external)

    C->>UC: execute(params)
    UC->>R: findAtivas(params)
    Note over R: Interface (Port)
    R->>RI: findAtivas(params)
    Note over RI: Implementação (Adapter)
    RI->>DB: SQL Query via DBLink
    DB-->>RI: ResultSet
    RI-->>R: InterrupcaoEntity[]
    R-->>UC: InterrupcaoEntity[]
    UC->>UC: Agregar por município/tipo
    UC-->>C: InterrupcaoAgregada[]
    C->>C: Mapear para Response ANEEL
```

## Inversão de Dependência

```mermaid
classDiagram
    class InterrupcaoRepository {
        <<interface>>
        +findAtivas(params) InterrupcaoEntity[]
        +findByMunicipio(ibge) InterrupcaoEntity[]
    }

    class OracleInterrupcaoRepository {
        -connection OracleConnection
        +findAtivas(params) InterrupcaoEntity[]
        +findByMunicipio(ibge) InterrupcaoEntity[]
    }

    class GetInterrupcoesAtivasUseCase {
        -repository InterrupcaoRepository
        +execute(params) Result~InterrupcaoAgregada[]~
    }

    InterrupcaoRepository <|.. OracleInterrupcaoRepository : implements
    GetInterrupcoesAtivasUseCase --> InterrupcaoRepository : depends on interface

    note for InterrupcaoRepository "Definido no Domain<br/>(src/domain/repositories)"
    note for OracleInterrupcaoRepository "Implementado na Infrastructure<br/>(src/infrastructure/repositories)"
    note for GetInterrupcoesAtivasUseCase "Usa apenas a interface<br/>Não conhece Oracle"
```

## Benefícios da Arquitetura

| Benefício | Descrição |
|-----------|-----------|
| **Testabilidade** | Domínio testável sem banco de dados |
| **Flexibilidade** | Trocar Oracle por outro DB sem afetar domínio |
| **Manutenibilidade** | Regras de negócio centralizadas |
| **Independência** | Framework HTTP pode ser trocado |
| **Clareza** | Responsabilidades bem definidas |
