# Fluxo de Dados - Projeto RADAR

## Arquitetura de Dados

```mermaid
flowchart TB
    subgraph RADAR["Banco RADAR (Principal)"]
        RADAR_SCHEMA[(Schema RADAR)]
        DBLINKS[DBLinks]
        VIEWS[Views Materializadas<br/>*opcional*]
        HISTORICO[(Tabela Histórico)]
    end

    subgraph Fonte["Sistemas Fonte (via DBLink)"]
        subgraph INSERVICE["INSERVICE"]
            AE[AGENCY_EVENT]
            SPT[SWITCH_PLAN_TASKS]
            OMS[OMS_CONNECTIVITY]
            CAV[CONSUMIDORES_ATINGIDOS_VIEW]
            UH[UN_HI]
        end

        subgraph INDICADORES["INDICADORES"]
            IU[IND_UNIVERSOS]
        end

        subgraph AJURI["AJURI (Futuro)"]
            UC_AJURI[Unidades Consumidoras]
        end
    end

    DBLINKS -->|INSERVICE_LINK| INSERVICE
    DBLINKS -->|INDICADORES_LINK| INDICADORES
    DBLINKS -.->|AJURI_LINK| AJURI

    style RADAR fill:#e8f5e9
    style Fonte fill:#fff3e0
```

## Fluxo da API 1 - Interrupções Ativas

```mermaid
flowchart LR
    subgraph Request
        REQ[GET /quantitativo<br/>interrupcoesativas]
    end

    subgraph Processing
        CACHE{Cache<br/>válido?}
        QUERY[Query com JOINs]
        AGG[Agregação por<br/>Município + Conjunto]
        MAP[Mapear para<br/>formato ANEEL]
    end

    subgraph DataSources
        AE[(AGENCY_EVENT)]
        SPT[(SWITCH_PLAN_TASKS)]
        OMS[(OMS_CONNECTIVITY)]
        IU[(IND_UNIVERSOS)]
    end

    subgraph Response
        RES[JSON Response]
    end

    REQ --> CACHE
    CACHE -->|Hit| MAP
    CACHE -->|Miss| QUERY
    QUERY --> AE
    QUERY --> SPT
    QUERY --> OMS
    QUERY --> IU
    AE --> AGG
    SPT --> AGG
    OMS --> AGG
    IU --> AGG
    AGG --> MAP
    MAP --> RES

    style CACHE fill:#fff3e0
    style AGG fill:#e3f2fd
```

## Query Principal - Interrupções Ativas

```mermaid
erDiagram
    AGENCY_EVENT ||--o{ SWITCH_PLAN_TASKS : "num_1 = OUTAGE_NUM"
    AGENCY_EVENT ||--o{ OMS_CONNECTIVITY : "dev_id = mslink"
    AGENCY_EVENT ||--|| IND_UNIVERSOS : "dev_id = ID_DISPOSITIVO"

    AGENCY_EVENT {
        number num_1 PK "ID do evento"
        char is_open "T=Aberto F=Fechado"
        number NUM_CUST "Qtd UCs afetadas"
        number dev_id FK "ID dispositivo"
        varchar ag_id "370 = Roraima"
        timestamp ad_ts "Data abertura"
    }

    SWITCH_PLAN_TASKS {
        number OUTAGE_NUM FK "ID do evento"
        number PLAN_ID "Se existe = PROGRAMADA"
    }

    OMS_CONNECTIVITY {
        number mslink PK "ID equipamento"
        varchar conj "Conjunto elétrico"
        number dist "370 = Roraima"
    }

    IND_UNIVERSOS {
        number ID_DISPOSITIVO FK "ID dispositivo"
        number CD_UNIVERSO "Código IBGE 7 dígitos"
        number CD_TIPO_UNIVERSO "2 = Município"
    }
```

## Transformação de Dados

```mermaid
flowchart TB
    subgraph Input["Dados Brutos (Oracle)"]
        RAW["num_1: 12345<br/>is_open: T<br/>NUM_CUST: 150<br/>dev_id: 67890<br/>PLAN_ID: 999<br/>conj: 1<br/>CD_UNIVERSO: 1400050"]
    end

    subgraph Domain["Entidade de Domínio"]
        ENT["InterrupcaoEntity<br/>{<br/>  id: 12345<br/>  tipoInterrupcao: PROGRAMADA<br/>  municipioIbge: 1400050<br/>  conjunto: 1<br/>  ucsAfetadas: 150<br/>}"]
    end

    subgraph Aggregation["Agregação"]
        AGG["InterrupcaoAgregada<br/>{<br/>  idConjunto: 1<br/>  municipioIbge: 1400050<br/>  qtdProgramada: 150<br/>  qtdNaoProgramada: 0<br/>}"]
    end

    subgraph Output["Response ANEEL"]
        RES["{<br/>  ideConjuntoUnidadeConsumidora: 1<br/>  ideMunicipio: 1400050<br/>  qtdOcorrenciaProgramada: 150<br/>  qtdOcorrenciaNaoProgramada: 0<br/>}"]
    end

    Input --> |Repository| Domain
    Domain --> |Use Case| Aggregation
    Aggregation --> |Mapper| Output

    style Input fill:#fce4ec
    style Domain fill:#c8e6c9
    style Aggregation fill:#e3f2fd
    style Output fill:#fff3e0
```

## Cache Flow

```mermaid
stateDiagram-v2
    [*] --> CheckCache: Request recebido

    CheckCache --> CacheHit: Dados no cache e válidos
    CheckCache --> CacheMiss: Cache vazio ou expirado

    CacheHit --> ReturnCached: Retornar dados do cache
    ReturnCached --> [*]

    CacheMiss --> QueryDatabase: Consultar Oracle
    QueryDatabase --> ProcessData: Processar e agregar
    ProcessData --> StoreCache: Armazenar no cache
    StoreCache --> ReturnFresh: Retornar dados frescos
    ReturnFresh --> [*]

    QueryDatabase --> HandleError: Erro de conexão
    HandleError --> CheckStaleCache: Verificar cache stale
    CheckStaleCache --> ReturnStale: Cache stale disponível
    CheckStaleCache --> ReturnError: Sem dados disponíveis
    ReturnStale --> [*]
    ReturnError --> [*]
```

## Mapeamento de Campos

| Campo ANEEL | Origem | Tabela | Transformação |
|-------------|--------|--------|---------------|
| `ideConjuntoUnidadeConsumidora` | `conj` | OMS_CONNECTIVITY | Direto |
| `ideMunicipio` | `CD_UNIVERSO` | IND_UNIVERSOS | Direto (7 dígitos) |
| `qtdUCsAtendidas` | - | View futura | Total UCs no conjunto |
| `qtdOcorrenciaProgramada` | `NUM_CUST` onde `PLAN_ID IS NOT NULL` | AGENCY_EVENT + SWITCH_PLAN_TASKS | SUM agrupado |
| `qtdOcorrenciaNaoProgramada` | `NUM_CUST` onde `PLAN_ID IS NULL` | AGENCY_EVENT | SUM agrupado |
