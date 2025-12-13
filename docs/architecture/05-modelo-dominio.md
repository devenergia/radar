# Modelo de Domínio - Projeto RADAR

## Entidades e Agregados

```mermaid
classDiagram
    class Interrupcao {
        <<Entity>>
        +number id
        +TipoInterrupcao tipo
        +CodigoIBGE municipio
        +number conjunto
        +number ucsAfetadas
        +Date dataInicio
        +Date? dataFim
        +boolean isAtiva()
    }

    class TipoInterrupcao {
        <<Value Object>>
        +string valor
        +static PROGRAMADA
        +static NAO_PROGRAMADA
        +static fromPlanId(planId) TipoInterrupcao
    }

    class CodigoIBGE {
        <<Value Object>>
        +number valor
        +static create(codigo) CodigoIBGE
        +isValid() boolean
    }

    class InterrupcaoAgregada {
        <<Aggregate>>
        +number idConjunto
        +CodigoIBGE municipio
        +number qtdUcsAtendidas
        +number qtdProgramada
        +number qtdNaoProgramada
    }

    class Demanda {
        <<Entity>>
        +string protocolo
        +TipoDemanda tipo
        +StatusDemanda status
        +Date dataAbertura
        +Date? dataEncerramento
    }

    class TipoDemanda {
        <<Value Object>>
        +string valor
        +static RECLAMACAO
        +static SOLICITACAO
        +static PEDIDO_INFORMACAO
    }

    class StatusDemanda {
        <<Value Object>>
        +string valor
        +static ABERTA
        +static EM_ANDAMENTO
        +static ENCERRADA
    }

    Interrupcao --> TipoInterrupcao
    Interrupcao --> CodigoIBGE
    InterrupcaoAgregada --> CodigoIBGE
    Demanda --> TipoDemanda
    Demanda --> StatusDemanda
```

## Bounded Contexts

```mermaid
flowchart TB
    subgraph InterrupcoesContext["Contexto: Interrupções"]
        INT_ENT[Interrupcao]
        INT_AGG[InterrupcaoAgregada]
        INT_REPO[InterrupcaoRepository]
        INT_SVC[InterrupcaoService]
    end

    subgraph DemandasContext["Contexto: Demandas"]
        DEM_ENT[Demanda]
        DEM_AGG[DemandaAgregada]
        DEM_REPO[DemandaRepository]
        DEM_SVC[DemandaService]
    end

    subgraph UniversoContext["Contexto: Universo (Compartilhado)"]
        UNI_MUN[Municipio]
        UNI_CONJ[ConjuntoEletrico]
        UNI_REPO[UniversoRepository]
    end

    InterrupcoesContext --> UniversoContext
    DemandasContext --> UniversoContext

    style InterrupcoesContext fill:#e3f2fd
    style DemandasContext fill:#fff3e0
    style UniversoContext fill:#e8f5e9
```

## Value Objects Detalhados

```mermaid
classDiagram
    class CodigoIBGE {
        <<Value Object>>
        -number _valor
        +get valor() number
        +static create(codigo: number) CodigoIBGE
        +static MUNICIPIOS_RORAIMA: number[]
        +isValid() boolean
        +equals(other: CodigoIBGE) boolean
        +toString() string
    }

    class TipoInterrupcao {
        <<Value Object>>
        -string _valor
        +get valor() string
        +get codigo() number
        +static PROGRAMADA: TipoInterrupcao
        +static NAO_PROGRAMADA: TipoInterrupcao
        +static fromPlanId(planId: number?) TipoInterrupcao
        +isProgramada() boolean
        +equals(other: TipoInterrupcao) boolean
    }

    class DataHoraBrasilia {
        <<Value Object>>
        -Date _valor
        +get valor() Date
        +static create(date: Date) DataHoraBrasilia
        +static fromString(str: string) DataHoraBrasilia
        +format(pattern: string) string
        +isAfter(other: DataHoraBrasilia) boolean
    }

    note for CodigoIBGE "Códigos IBGE válidos para RR:<br/>1400050 (Boa Vista)<br/>1400100 (Alto Alegre)<br/>... (13 outros)"

    note for TipoInterrupcao "PROGRAMADA = código 1<br/>NAO_PROGRAMADA = código 2"

    note for DataHoraBrasilia "Sempre em UTC-4 (Brasília)<br/>Formato ANEEL: dd/mm/yyyy hh:mm"
```

## Repository Interfaces (Ports)

```mermaid
classDiagram
    class InterrupcaoRepository {
        <<interface>>
        +findAtivas(params: FindAtivasParams) Promise~Interrupcao[]~
        +findByMunicipio(ibge: CodigoIBGE) Promise~Interrupcao[]~
        +findHistorico(params: HistoricoParams) Promise~Interrupcao[]~
    }

    class UniversoRepository {
        <<interface>>
        +findMunicipioByDispositivo(devId: number) Promise~CodigoIBGE~
        +findConjuntoByDispositivo(devId: number) Promise~number~
        +findAllMunicipios() Promise~Municipio[]~
    }

    class DemandaRepository {
        <<interface>>
        +findByProtocolo(protocolo: string) Promise~Demanda~
        +findAbertas() Promise~Demanda[]~
        +findByPeriodo(inicio: Date, fim: Date) Promise~Demanda[]~
    }

    class CacheRepository {
        <<interface>>
        +get~T~(key: string) Promise~T?~
        +set~T~(key: string, value: T, ttl: number) Promise~void~
        +invalidate(key: string) Promise~void~
        +invalidateAll() Promise~void~
    }
```

## Use Cases

```mermaid
classDiagram
    class GetInterrupcoesAtivasUseCase {
        -InterrupcaoRepository repository
        -UniversoRepository universoRepository
        -CacheRepository cache
        +execute(params) Promise~Result~InterrupcaoAgregada[]~~
    }

    class GetDadosDemandaUseCase {
        -DemandaRepository repository
        +execute(protocolo: string) Promise~Result~Demanda~~
    }

    class GetQuantitativoDemandasUseCase {
        -DemandaRepository repository
        +execute(params) Promise~Result~DemandaAgregada[]~~
    }

    GetInterrupcoesAtivasUseCase --> InterrupcaoRepository
    GetInterrupcoesAtivasUseCase --> UniversoRepository
    GetInterrupcoesAtivasUseCase --> CacheRepository
    GetDadosDemandaUseCase --> DemandaRepository
    GetQuantitativoDemandasUseCase --> DemandaRepository
```

## Regras de Negócio

```mermaid
flowchart TB
    subgraph Rules["Regras de Negócio"]
        R1["Uma interrupção é ATIVA quando<br/>is_open = 'T'"]
        R2["Uma interrupção é PROGRAMADA quando<br/>existe PLAN_ID em SWITCH_PLAN_TASKS"]
        R3["Código IBGE deve ter 7 dígitos<br/>e pertencer a Roraima (14xxxxx)"]
        R4["Dados devem ser agregados por<br/>Município + Conjunto + Tipo"]
        R5["Resposta deve seguir formato ANEEL<br/>mesmo em caso de erro"]
    end

    style Rules fill:#fff3e0
```

## Invariantes de Domínio

| Entidade | Invariante | Validação |
|----------|------------|-----------|
| `CodigoIBGE` | Deve ter 7 dígitos | `valor >= 1000000 && valor <= 9999999` |
| `CodigoIBGE` | Deve ser de Roraima | `valor >= 1400000 && valor <= 1499999` |
| `TipoInterrupcao` | Apenas PROGRAMADA ou NAO_PROGRAMADA | Enum restrito |
| `Interrupcao` | Se ativa, dataFim deve ser null | `isAtiva() => dataFim === null` |
| `Interrupcao` | ucsAfetadas >= 0 | `ucsAfetadas >= 0` |
