# Diagramas de Sequência - Projeto RADAR

## API 1: GET /quantitativointerrupcoesativas

### Fluxo Principal (Sucesso)

```mermaid
sequenceDiagram
    autonumber
    participant ANEEL
    participant LB as Load Balancer
    participant API as RADAR API
    participant Auth as AuthMiddleware
    participant Cache as MemoryCache
    participant UC as GetInterrupcoesUseCase
    participant Repo as InterrupcaoRepository
    participant DB as Oracle (via DBLink)

    ANEEL->>LB: GET /quantitativointerrupcoesativas<br/>Header: x-api-key
    LB->>API: Forward request

    API->>Auth: Verificar autenticação
    Auth->>Auth: Validar IP whitelist
    Auth->>Auth: Validar API Key
    Auth-->>API: Autenticado OK

    API->>Cache: get("interrupcoes:default")

    alt Cache Hit
        Cache-->>API: Dados em cache
        API-->>ANEEL: 200 OK (cached)
    else Cache Miss
        Cache-->>API: null

        API->>UC: execute()
        UC->>Repo: findAtivas()

        Repo->>DB: SELECT com JOINs<br/>(AGENCY_EVENT, SWITCH_PLAN_TASKS,<br/>OMS_CONNECTIVITY, IND_UNIVERSOS)
        DB-->>Repo: ResultSet

        Repo-->>UC: InterrupcaoEntity[]
        UC->>UC: Agregar por município + tipo
        UC-->>API: InterrupcaoAgregada[]

        API->>Cache: set("interrupcoes:default", data, TTL=5min)
        API->>API: Mapear para formato ANEEL
        API-->>ANEEL: 200 OK
    end
```

### Fluxo com Erro de Autenticação

```mermaid
sequenceDiagram
    autonumber
    participant ANEEL
    participant API as RADAR API
    participant Auth as AuthMiddleware
    participant Log as Logger

    ANEEL->>API: GET /quantitativointerrupcoesativas<br/>(sem x-api-key)

    API->>Auth: Verificar autenticação
    Auth->>Auth: Header x-api-key ausente
    Auth->>Log: log.warn("Requisição sem API Key")
    Auth-->>API: UnauthorizedError

    API-->>ANEEL: 401 Unauthorized<br/>{idcStatusRequisicao: 2, mensagem: "Header x-api-key é obrigatório"}
```

### Fluxo com Erro de Banco de Dados

```mermaid
sequenceDiagram
    autonumber
    participant ANEEL
    participant API as RADAR API
    participant UC as UseCase
    participant Repo as Repository
    participant Cache as MemoryCache
    participant DB as Oracle
    participant Log as Logger

    ANEEL->>API: GET /quantitativointerrupcoesativas

    API->>UC: execute()
    UC->>Repo: findAtivas()
    Repo->>DB: SELECT ...
    DB--xRepo: Connection Error

    Repo->>Log: log.error("Database connection failed")
    Repo-->>UC: DatabaseError

    UC->>Cache: getStale("interrupcoes:default")

    alt Stale Data Available
        Cache-->>UC: Dados stale
        UC->>Log: log.warn("Servindo dados stale")
        UC-->>API: InterrupcaoAgregada[] (stale)
        API-->>ANEEL: 200 OK (dados stale)
    else No Stale Data
        Cache-->>UC: null
        UC-->>API: DatabaseError
        API-->>ANEEL: 200 OK<br/>{idcStatusRequisicao: 2, mensagem: "Erro de conexão com banco"}
    end
```

## API 2: GET /quantitativodemandas

```mermaid
sequenceDiagram
    autonumber
    participant ANEEL
    participant API as RADAR API
    participant UC as GetDemandasUseCase
    participant Repo as DemandaRepository
    participant DB as Oracle

    ANEEL->>API: GET /quantitativodemandas?dthRecuperacao=10/12/2025 14:30

    API->>API: Validar formato data (dd/mm/yyyy hh:mm)

    API->>UC: execute({dataRecuperacao: Date})
    UC->>Repo: findByData(data)
    Repo->>DB: SELECT ... WHERE data = :data
    DB-->>Repo: ResultSet
    Repo-->>UC: DemandaEntity[]
    UC->>UC: Agregar por tipo/status
    UC-->>API: DemandaAgregada[]
    API-->>ANEEL: 200 OK
```

## Fluxo de Startup da Aplicação

```mermaid
sequenceDiagram
    autonumber
    participant Main as main.ts
    participant Config as ConfigLoader
    participant DB as DatabasePool
    participant Cache as CacheService
    participant Server as FastifyServer
    participant Health as HealthCheck

    Main->>Config: loadConfig()
    Config->>Config: Validar variáveis de ambiente
    Config-->>Main: AppConfig

    Main->>DB: createPool(config.database)
    DB->>DB: Inicializar pool Oracle
    DB-->>Main: Pool ready

    Main->>Cache: initialize(config.cache)
    Cache-->>Main: Cache ready

    Main->>Server: createServer(config)
    Server->>Server: Registrar plugins
    Server->>Server: Registrar rotas
    Server->>Server: Registrar error handler
    Server-->>Main: Server configured

    Main->>Server: listen(port)
    Server-->>Main: Listening on port 3000

    loop Every 30 seconds
        Server->>Health: checkHealth()
        Health->>DB: ping()
        DB-->>Health: OK
        Health-->>Server: healthy
    end
```

## Fluxo de Shutdown Graceful

```mermaid
sequenceDiagram
    autonumber
    participant OS as Sistema Operacional
    participant Main as main.ts
    participant Server as FastifyServer
    participant DB as DatabasePool
    participant Log as Logger

    OS->>Main: SIGTERM/SIGINT

    Main->>Log: log.info("Shutdown iniciado")

    Main->>Server: close()
    Server->>Server: Parar aceitar novas conexões
    Server->>Server: Aguardar requisições em andamento
    Server-->>Main: Server closed

    Main->>DB: closePool()
    DB->>DB: Fechar conexões ativas
    DB-->>Main: Pool closed

    Main->>Log: log.info("Shutdown completo")
    Main->>OS: process.exit(0)
```

## Health Check Detalhado

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant API as RADAR API
    participant HC as HealthCheckService
    participant DB as DatabasePool
    participant Cache as CacheService

    Client->>API: GET /health

    API->>HC: check()

    par Database Check
        HC->>DB: ping()
        DB->>DB: SELECT 1 FROM DUAL
        DB-->>HC: {status: "up", latencyMs: 15}
    and Cache Check
        HC->>Cache: getStats()
        Cache-->>HC: {status: "up", itemCount: 42}
    end

    HC->>HC: Determinar status geral

    alt All Healthy
        HC-->>API: {status: "healthy", checks: {...}}
        API-->>Client: 200 OK
    else Degraded
        HC-->>API: {status: "degraded", checks: {...}}
        API-->>Client: 200 OK
    else Unhealthy
        HC-->>API: {status: "unhealthy", checks: {...}}
        API-->>Client: 503 Service Unavailable
    end
```
