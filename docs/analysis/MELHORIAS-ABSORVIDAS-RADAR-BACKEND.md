# Analise de Melhorias - Projeto radar-backend

**Data da Analise:** 2025-12-19
**Projeto Analisado:** D:\roraima_radar\radar-backend (TypeScript/Fastify)
**Projeto Destino:** RADAR (Python/FastAPI)

---

## Sumario Executivo

O projeto `radar-backend` e uma implementacao funcional em TypeScript/Fastify que serve como referencia valiosa para o projeto RADAR. Esta analise identifica **melhorias absorviveis**, **padroes a adotar**, e **erros a evitar**.

### Principais Descobertas

| Categoria | Absorver | Evitar |
|-----------|----------|--------|
| **View SQL** | Estrutura otimizada com CTEs | - |
| **Cache Redis** | Background jobs com BullMQ | Falta de cache HTTP |
| **Autenticacao** | Separacao API Key vs JWT | UUIDs hardcoded |
| **Arquitetura** | Multi-database support | Controllers gordos |
| **Validacao** | Schema-first (Zod) | Logica espalhada |

---

## 1. View SQL - VW_INTERRUPCAOFORNECIMENTO

### O que Absorver

A view `VW_INTERRUPCAOFORNECIMENTO` e a principal descoberta. Ela resolve de forma elegante a agregacao de dados que o RADAR precisa.

#### Estrutura da View (Atual)

```sql
CREATE OR REPLACE VIEW "APIANEEL"."VW_INTERRUPCAOFORNECIMENTO" AS
WITH
    Tasks AS (
        SELECT DISTINCT OP.outage_num
        FROM inservice.switch_plan_tasks OP
    ),
    Device_Municipio_Map AS (
        SELECT DISTINCT oc.dev_name, oc.conj, c.HXGN_COD_MUNICIPIO_IBGE AS IdeMunicipio
        FROM inservice.cispersl c
        JOIN inservice.oms_connectivity oc ON oc.dev_name = c.xfmr
        WHERE oc.dist = '370' AND c.xfmr IS NOT NULL
    ),
    UCs_Atendidas AS (
        SELECT oc.conj, c.HXGN_COD_MUNICIPIO_IBGE AS IdeMunicipio,
               COUNT(c.premise) AS QtdUCsAtendidas
        FROM inservice.cispersl c
        JOIN inservice.oms_connectivity oc ON oc.dev_name = c.xfmr
        WHERE oc.dist = '370' AND c.xfmr IS NOT NULL
        GROUP BY oc.conj, c.HXGN_COD_MUNICIPIO_IBGE
    ),
    Ocorrencias AS (
        SELECT Mapa.conj, Mapa.IdeMunicipio,
               SUM(CASE WHEN T.outage_num IS NULL THEN ae.NUM_CUST ELSE 0 END) as QtdOcorrenciaNaoProgramada,
               SUM(CASE WHEN T.outage_num IS NOT NULL THEN ae.NUM_CUST ELSE 0 END) as QtdOcorrenciaProgramada
        FROM inservice.agency_event ae
        JOIN Device_Municipio_Map Mapa ON ae.dev_name = Mapa.dev_name
        LEFT JOIN Tasks T ON ae.num_1 = T.outage_num
        WHERE ae.ag_id = 370 AND ae.is_open = 'T'
              AND ae.HXGN_DT_ORACLE IS NOT NULL
              AND ae.tycod <> 'UC_NOXFMR'
              AND NVL(ae.dev_id, 0) > 0
        GROUP BY Mapa.conj, Mapa.IdeMunicipio
    )
SELECT
    COALESCE(UCs.conj, Ocs.conj) AS IdeConjuntoUnidadeConsumidora,
    COALESCE(UCs.IdeMunicipio, Ocs.IdeMunicipio) AS IdeMunicipio,
    NVL(UCs.QtdUCsAtendidas, 0) AS QtdUCsAtendidas,
    NVL(Ocs.QtdOcorrenciaProgramada, 0) AS QtdOcorrenciaProgramada,
    NVL(Ocs.QtdOcorrenciaNaoProgramada, 0) AS QtdOcorrenciaNaoProgramada
FROM UCs_Atendidas UCs
FULL OUTER JOIN Ocorrencias Ocs ON UCs.conj = Ocs.conj AND UCs.IdeMunicipio = Ocs.IdeMunicipio
WHERE NVL(Ocs.QtdOcorrenciaProgramada, 0) > 0 OR NVL(Ocs.QtdOcorrenciaNaoProgramada, 0) > 0
ORDER BY IdeConjuntoUnidadeConsumidora, IdeMunicipio;
```

### Diferencas para o RADAR

| Aspecto | radar-backend | RADAR |
|---------|---------------|-------|
| Schema | `APIANEEL` | `RADAR_API` |
| DBLink | Acesso direto | Via DBLink |
| ag_id/dist | 7019 (Amazonas - incorreto) | 370 (Roraima - correto) |
| Tabela UCs | `cispersl` | Verificar equivalente |

### Acao Recomendada

Criar view adaptada para o RADAR em `RADAR_API` schema usando DBLinks.

---

## 2. Estrutura de Tabelas - Schema RADAR_ANEEL

### Tabelas Identificadas

#### 2.1 TOKEN_ACESSO (Autenticacao API)

```sql
CREATE TABLE RADAR_ANEEL.TOKEN_ACESSO (
    ID VARCHAR(100) NOT NULL,
    NOME VARCHAR(300) NOT NULL,
    CHAVE VARCHAR(100) NOT NULL,
    DATA_CRIACAO DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT TOKEN_ACESSO_PK PRIMARY KEY (ID)
);
```

**Absorver:** Tabela para gerenciar API Keys da ANEEL.

#### 2.2 CONSULTA (Auditoria de Requisicoes)

```sql
CREATE TABLE RADAR_ANEEL.CONSULTA (
    ID VARCHAR2(100) NOT NULL,
    ID_TIPO_CONSULTA NUMBER NOT NULL,
    DATA_BRASILIA DATE NOT NULL,
    DATA_INICIO DATE NOT NULL,
    DATA_FIM DATE NULL,
    CONSTRAINT CONSULTA_PK PRIMARY KEY (ID)
);
```

**Absorver:** Registro de todas as consultas realizadas (auditoria ANEEL).

#### 2.3 INTERRUPCAO_ATIVA (Historico)

```sql
CREATE TABLE RADAR_ANEEL.INTERRUPCAO_ATIVA (
    ID_CONSULTA VARCHAR(100) NOT NULL,
    ID_CONJUNTO_UC NUMBER NOT NULL,
    ID_MUNICIPIO NUMBER NOT NULL,
    QTD_UC_ATENDIDA NUMBER NOT NULL,
    QTD_PROGRAMADA NUMBER NOT NULL,
    QTD_NAO_PROGRAMADA NUMBER NOT NULL,
    CONSTRAINT FK_INTER_ATIV_CONS FOREIGN KEY (ID_CONSULTA) REFERENCES RADAR_ANEEL.CONSULTA(ID)
);
```

**Absorver:** Snapshot de cada consulta para historico e auditoria.

---

## 3. Cache e Background Jobs (Redis + BullMQ)

### Arquitetura Atual

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Fastify   │────▶│    Redis    │────▶│   BullMQ    │
│   (HTTP)    │     │   (Cache)   │     │   (Jobs)    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Worker    │
                    │ (30 min)    │
                    └─────────────┘
```

### Padrao de Background Job

```typescript
// InterrupcaoAtivaWork.ts
const queue = new Queue(queueName, { connection: redisConnection })

await queue.add(jobName, {}, {
    repeat: { pattern: '*/30 * * * *' },  // A cada 30 minutos
    jobId
})

new Worker(queueName, async () => {
    await InterrupcaoEnergiaController.iniciar()
}, { connection: redisConnection })
```

### Adaptacao para Python/FastAPI

```python
# Usar Celery + Redis
from celery import Celery
from celery.schedules import crontab

celery_app = Celery('radar', broker='redis://localhost:6379/0')

celery_app.conf.beat_schedule = {
    'atualizar-interrupcoes': {
        'task': 'tasks.atualizar_interrupcoes',
        'schedule': crontab(minute='*/30'),  # A cada 30 minutos
    },
}

@celery_app.task
def atualizar_interrupcoes():
    """Background job para atualizar cache de interrupcoes."""
    use_case = GetInterrupcoesAtivasUseCase(...)
    result = use_case.execute()
    cache.set('interrupcoes:ativas', result.value, ttl=1800)
```

### O que Absorver

| Funcionalidade | Implementacao |
|----------------|---------------|
| Job scheduling | Celery Beat |
| Cache HTTP | Redis com TTL |
| Job monitoring | Flower (dashboard) |
| Dead letter queue | Celery retry policy |

---

## 4. Autenticacao - Padroes

### API Key (ANEEL)

```typescript
// AneelPlugin.ts
app.decorate('aneel', async (req) => {
    const { 'x-api-key': token } = req.headers
    const isValid = await TokenAcessoDAO.show({ token })
    if (!isValid) return reply.code(401).send({...})
    req.acesso = isValid
})
```

### Adaptacao para FastAPI

```python
# dependencies.py
from fastapi import Depends, Header, HTTPException

async def verify_api_key(
    x_api_key: str = Header(..., alias="x-api-key"),
    session: Session = Depends(get_session),
) -> TokenAcesso:
    """Valida API Key da ANEEL."""
    token = session.query(TokenAcesso).filter_by(chave=x_api_key).first()
    if not token:
        raise HTTPException(
            status_code=401,
            detail={
                "idcStatusRequisicao": 0,
                "desStatusRequisicao": "Token inválido ou não fornecido",
            }
        )
    return token
```

### O que Absorver

- Tabela `TOKEN_ACESSO` para gerenciar API Keys
- Validacao via header `x-api-key`
- Log de todas as autenticacoes

### O que Evitar

- UUIDs hardcoded para admin
- Falta de expiracao de tokens
- Ausencia de rate limiting por token

---

## 5. Estrutura de Resposta ANEEL

### Padrao Identificado

```typescript
const resposta = {
    idcStatusRequisicao: 1,           // 1=sucesso, 0=erro, 2=parcial
    desStatusRequisicao: 'Sucesso',
    emailIndisponibilidade: 'radar@roraima.com',
    mensagem: '',
    interrupcaoFornecimento: [...]
}
```

### Campos Obrigatorios

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `idcStatusRequisicao` | number | Codigo de status (0, 1, 2) |
| `desStatusRequisicao` | string | Descricao do status |
| `emailIndisponibilidade` | string | Email para contato |
| `mensagem` | string | Mensagem adicional |
| `interrupcaoFornecimento` | array | Lista de interrupcoes |

### Adaptacao Pydantic

```python
from pydantic import BaseModel, EmailStr
from typing import List

class InterrupcaoItem(BaseModel):
    ideConjuntoUnidadeConsumidora: int
    ideMunicipio: int
    qtdUCsAtendidas: int
    qtdOcorrenciaProgramada: int
    qtdOcorrenciaNaoProgramada: int

class AneelResponse(BaseModel):
    idcStatusRequisicao: int
    desStatusRequisicao: str
    emailIndisponibilidade: EmailStr
    mensagem: str
    interrupcaoFornecimento: List[InterrupcaoItem]
```

---

## 6. Multi-Database Support

### Arquitetura radar-backend

```typescript
// knexfile.ts - 3 conexoes Oracle
export default {
    ajuri: {
        client: 'oracledb',
        connection: { host: AJURI_HOST, ... },
        pool: { min: 2, max: 10, idleTimeoutMillis: 5000 }
    },
    hexagon: {
        client: 'oracledb',
        connection: { host: HEXAGON_HOST, ... }
    },
    appsp01: {
        client: 'oracledb',
        connection: { host: APPSP01_HOST, ... }
    }
}
```

### Adaptacao SQLAlchemy

```python
# infrastructure/database/engines.py
from sqlalchemy import create_engine

class DatabaseEngines:
    """Gerenciador de multiplas conexoes Oracle."""

    _engines = {}

    @classmethod
    def get_engine(cls, name: str) -> Engine:
        if name not in cls._engines:
            cls._engines[name] = create_engine(
                settings.get_connection_string(name),
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=1800,
            )
        return cls._engines[name]

    @classmethod
    def inservice(cls) -> Engine:
        return cls.get_engine('inservice')

    @classmethod
    def indicadores(cls) -> Engine:
        return cls.get_engine('indicadores')

    @classmethod
    def radar(cls) -> Engine:
        return cls.get_engine('radar')
```

---

## 7. Logging e Auditoria

### Tabela CONSULTA para Auditoria

O radar-backend registra cada consulta da ANEEL:

```typescript
// Antes de processar
const consulta = await ConsultaDAO.store({
    idTipoConsulta: 1,
    dataBrasilia: new Date(),
    dataInicio: new Date()
})

// Apos processar
await ConsultaDAO.update(consulta.id, { dataFim: new Date() })

// Armazenar resultado
for (const item of interrupcoes) {
    await InterrupcaoAtivaDAO.store({
        idConsulta: consulta.id,
        ...item
    })
}
```

### Beneficios

1. **Rastreabilidade**: Toda consulta ANEEL e registrada
2. **Historico**: Snapshots de cada momento
3. **Auditoria**: Prova de conformidade
4. **Debugging**: Reproduzir problemas

### Implementacao RADAR

```python
# domain/entities/consulta.py
@dataclass
class Consulta:
    id: str
    tipo: TipoConsulta
    data_brasilia: datetime
    data_inicio: datetime
    data_fim: datetime | None = None

    @classmethod
    def iniciar(cls, tipo: TipoConsulta) -> "Consulta":
        return cls(
            id=str(uuid4()),
            tipo=tipo,
            data_brasilia=datetime.now(tz=BRASILIA),
            data_inicio=datetime.now(),
        )

    def finalizar(self) -> None:
        self.data_fim = datetime.now()
```

---

## 8. Erros a Evitar

### 8.1 Controllers Gordos

```typescript
// EVITAR: Tudo no controller
class InterrupcaoEnergiaController {
    async iniciar() {
        // 1. Validacao
        // 2. Busca dados
        // 3. Transformacao
        // 4. Armazenamento
        // 5. Formatacao resposta
        // 100+ linhas de codigo misturado
    }
}
```

**Solucao RADAR:** Use Cases separados

```python
# CORRETO: Separacao de responsabilidades
class BuscarInterrupcoesUseCase:
    async def execute(self) -> Result[List[Interrupcao]]: ...

class ArmazenarConsultaUseCase:
    async def execute(self, consulta: Consulta, dados: List[Interrupcao]) -> Result: ...

class FormatarRespostaAneelService:
    def formatar(self, dados: List[Interrupcao]) -> AneelResponse: ...
```

### 8.2 Logica Espalhada

```typescript
// EVITAR: Parsing de data inline
const data = `${dthRecuperacao.split(' ')[0].split('/').reverse().join('-')} ...`
```

**Solucao RADAR:** Value Objects

```python
# CORRETO: Value Object para datas
@dataclass(frozen=True)
class DataRecuperacao:
    valor: datetime

    @classmethod
    def from_aneel_format(cls, raw: str) -> Result["DataRecuperacao"]:
        """Converte formato ANEEL (DD/MM/YYYY HH:MM:SS) para datetime."""
        try:
            dt = datetime.strptime(raw, "%d/%m/%Y %H:%M:%S")
            return Result.ok(cls(valor=dt))
        except ValueError as e:
            return Result.fail(f"Formato de data invalido: {raw}")
```

### 8.3 Tratamento de Erro Generico

```typescript
// EVITAR: Catch-all sem contexto
catch (error) {
    console.log(error)
    return reply.status(400).send({ mensagem: 'Erro' })
}
```

**Solucao RADAR:** Erros de dominio tipados

```python
# CORRETO: Hierarquia de erros
class DomainError(Exception):
    code: str
    message: str

class DatabaseConnectionError(DomainError):
    code = "DB_CONNECTION_ERROR"

class InvalidTokenError(DomainError):
    code = "INVALID_TOKEN"

# Handler centralizado
@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=400,
        content={
            "idcStatusRequisicao": 0,
            "desStatusRequisicao": exc.message,
            "codigo": exc.code,
        }
    )
```

---

## 9. Checklist de Implementacao

### Fase 1: Infraestrutura (Prioridade Alta)

- [ ] Criar view `VW_INTERRUPCAOFORNECIMENTO` adaptada para RADAR
- [ ] Criar tabelas: `TOKEN_ACESSO`, `CONSULTA`, `INTERRUPCAO_ATIVA`
- [ ] Configurar Redis para cache e jobs
- [ ] Implementar Celery para background tasks

### Fase 2: Dominio (Prioridade Alta)

- [ ] Criar Value Object `DataRecuperacao`
- [ ] Criar Entity `Consulta` com metodos de ciclo de vida
- [ ] Criar Repository Protocol para auditoria
- [ ] Implementar Result Pattern para erros

### Fase 3: Aplicacao (Prioridade Media)

- [ ] Implementar `BuscarInterrupcoesUseCase`
- [ ] Implementar `RegistrarConsultaUseCase`
- [ ] Implementar `ArmazenarSnapshotUseCase`
- [ ] Criar service de formatacao ANEEL

### Fase 4: Interface (Prioridade Media)

- [ ] Implementar dependency `verify_api_key`
- [ ] Criar schemas Pydantic para request/response
- [ ] Implementar middleware de logging
- [ ] Adicionar rate limiting

### Fase 5: Operacoes (Prioridade Baixa)

- [ ] Configurar Celery Beat para job de 30 min
- [ ] Implementar health checks
- [ ] Configurar metricas Prometheus
- [ ] Criar dashboard Flower

---

## 10. Arquivos a Criar no RADAR

| Arquivo | Descricao | Prioridade |
|---------|-----------|------------|
| `database/views/vw_interrupcao_fornecimento.sql` | View adaptada | CRITICA |
| `database/tables/token_acesso.sql` | Tabela API Keys | ALTA |
| `database/tables/consulta.sql` | Tabela auditoria | ALTA |
| `database/tables/interrupcao_ativa.sql` | Tabela historico | ALTA |
| `infrastructure/cache/redis_client.py` | Cliente Redis | MEDIA |
| `infrastructure/tasks/celery_app.py` | Config Celery | MEDIA |
| `domain/value_objects/data_recuperacao.py` | VO para datas | MEDIA |
| `domain/entities/consulta.py` | Entity consulta | MEDIA |

---

## 11. Conclusao

O projeto `radar-backend` fornece uma base funcional que valida a abordagem tecnica. As principais licoes sao:

### Absorver
1. **View SQL otimizada** com CTEs para agregacao
2. **Estrutura de auditoria** (CONSULTA + INTERRUPCAO_ATIVA)
3. **Background jobs** para atualizacao periodica
4. **Autenticacao por API Key** com tabela dedicada

### Evitar
1. Controllers com muita responsabilidade
2. Logica de negocio espalhada
3. Tratamento de erro generico
4. Falta de testes automatizados

### Melhorar
1. Adicionar cache HTTP (ausente no original)
2. Implementar Clean Architecture completa
3. Usar TDD desde o inicio
4. Adicionar observabilidade (logs, metricas, traces)

---

**Documento criado por:** Claude Code
**Proxima revisao:** Apos implementacao da Fase 1
