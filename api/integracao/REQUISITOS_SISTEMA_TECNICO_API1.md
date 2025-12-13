# Requisitos para Sistema Técnico (Inservice)
## API 1 - Quantitativo de Interrupções Ativas

**Projeto:** RADAR - Rede de Acompanhamento e Diagnóstico da Distribuição
**Base Legal:** Ofício Circular nº 14/2025-SFE/ANEEL V4
**Prazo:** Dezembro/2025
**Data do Documento:** Dezembro/2025
**Última Atualização:** Dezembro/2025

---

## 1. Objetivo

Este documento especifica os requisitos de dados do **Sistema Técnico (Inservice)** para a implementação da **API 1 - Quantitativo de Interrupções Ativas** do Projeto RADAR.

A API precisa responder em tempo real o quantitativo de unidades consumidoras com interrupção de fornecimento **ativas no momento da consulta**, agrupadas por município e conjunto elétrico.

**Importante:** Todos os dados necessários são obtidos diretamente das tabelas do INSERVICE e INDICADORES. **Não há dependência do Sistema Comercial (Ajuri)** para esta API.

---

## 2. Contexto da Integração

```
┌─────────────────┐     ┌──────────────────────────────────────────────────┐
│   SCADA/SAGE    │────▶│              SISTEMA TÉCNICO                      │
│                 │     │                                                   │
└─────────────────┘     │  ┌─────────────────┐   ┌─────────────────────┐   │
                        │  │    INSERVICE    │   │    INDICADORES      │   │
                        │  │                 │   │                     │   │
                        │  │ AGENCY_EVENT    │   │ IND_UNIVERSOS       │   │
                        │  │ SWITCH_PLAN_... │   │ (Código IBGE)       │   │
                        │  │ OMS_CONNECTIVITY│   │                     │   │
                        │  │ CONSUMIDORES_..│   │                     │   │
                        │  └────────┬────────┘   └──────────┬──────────┘   │
                        │           │                       │              │
                        │           └───────────┬───────────┘              │
                        │                       │                          │
                        └───────────────────────┼──────────────────────────┘
                                                │
                                                ▼
                                    ┌─────────────────────┐
                                    │     API RADAR       │
                                    └──────────┬──────────┘
                                               │
                                               ▼
                                    ┌─────────────────────┐
                                    │       ANEEL         │
                                    └─────────────────────┘
```

**Fontes de Dados:**
- **INSERVICE:** Eventos, classificação, conjunto elétrico, UCs atingidas
- **INDICADORES:** Código IBGE dos municípios (via `IND_UNIVERSOS`)

---

## 3. Tabelas Fonte Identificadas

Todas as tabelas necessárias já existem nos schemas INSERVICE e INDICADORES:

| Schema | Tabela/View | Descrição | Uso |
|--------|-------------|-----------|-----|
| `INSERVICE` | `AGENCY_EVENT` | Eventos/Ocorrências de interrupção | Principal - dados do evento |
| `INSERVICE` | `SWITCH_PLAN_TASKS` | Planos de manobra programados | **Identificar se é PROGRAMADA** |
| `INSERVICE` | `OMS_CONNECTIVITY` | Conectividade - Conjuntos e equipamentos | **Conjunto elétrico** |
| `INSERVICE` | `CONSUMIDORES_ATINGIDOS_VIEW` | UCs atingidas por evento | **Lista de UCs afetadas** |
| `INSERVICE` | `UN_HI` | Histórico de unidades/equipes | Equipes em campo |
| `INSERVICE` | `HXGN_INT_AJURI` | Integração com coordenadas | Latitude/Longitude |
| `INDICADORES` | `IND_UNIVERSOS` | Universos (municípios, conjuntos) | **Código IBGE do município** |

**Nota:** Não há dependência da view `VW_MUNICIPIOS_IBGE_RADAR` do Ajuri. O código IBGE é obtido diretamente de `INDICADORES.IND_UNIVERSOS`.

---

## 4. Mapeamento de Campos Identificados

### 4.1 Tabela AGENCY_EVENT (INSERVICE)

| Campo Inservice | Tipo | Descrição | Mapeamento RADAR |
|-----------------|------|-----------|------------------|
| `num_1` | NUMBER | Número da ocorrência | `ID_INTERRUPCAO` |
| `is_open` | CHAR | **T** = Aberto, **F** = Fechado | Filtro de ativas |
| `ad_ts` | VARCHAR | Data/hora abertura (YYYYMMDDHH24MISSSS) | `DATA_HORA_INICIO` |
| `xdts` | VARCHAR | Data/hora encerramento | `DATA_HORA_FIM` |
| `NUM_CUST` | NUMBER | **Quantidade de UCs afetadas** | `QTD_UCS_AFETADAS` |
| `dev_id` | NUMBER | ID do dispositivo | **JOIN com IND_UNIVERSOS e OMS** |
| `hxgn_ds_municipio` | VARCHAR | Descrição do município | Referência |
| `feeder` | VARCHAR | Alimentador | `ALIMENTADOR` |
| `substation` | VARCHAR | Subestação | `SUBESTACAO` |
| `ag_id` | VARCHAR | ID da agência (**370** = Roraima) | Filtro |

### 4.2 Tabela SWITCH_PLAN_TASKS (INSERVICE) - Identificar Interrupção Programada

| Campo Inservice | Tipo | Descrição | Mapeamento RADAR |
|-----------------|------|-----------|------------------|
| `OUTAGE_NUM` | NUMBER | Número da ocorrência | **JOIN com AGENCY_EVENT.NUM_1** |
| `PLAN_ID` | NUMBER/VARCHAR | ID do plano de manobra | Se existir = **PROGRAMADA** |

**Regra de Negócio:**
- Se existe registro em `SWITCH_PLAN_TASKS` com `PLAN_ID` preenchido para o `NUM_1` do evento → **PROGRAMADA**
- Se não existe registro → **NAO_PROGRAMADA**

### 4.3 Tabela OMS_CONNECTIVITY (INSERVICE)

| Campo Inservice | Tipo | Descrição | Mapeamento RADAR |
|-----------------|------|-----------|------------------|
| `mslink` | NUMBER | Link do equipamento | **JOIN com AGENCY_EVENT.dev_id** |
| `conj` | VARCHAR/NUMBER | **Conjunto elétrico** | `ideConjuntoUnidadeConsumidora` |
| `mun` | VARCHAR | Município | Referência |
| `dist` | NUMBER | Distribuidora (**370**) | Filtro |

### 4.4 Tabela IND_UNIVERSOS (INDICADORES) - Código IBGE

| Campo | Tipo | Descrição | Mapeamento RADAR |
|-------|------|-----------|------------------|
| `ID_DISPOSITIVO` | NUMBER | ID do dispositivo | **JOIN com AGENCY_EVENT.dev_id** |
| `CD_UNIVERSO` | NUMBER(7) | **Código IBGE do município** | `ideMunicipio` |
| `CD_TIPO_UNIVERSO` | NUMBER | Tipo do universo | Filtro = **2** (município) |

**Regra de Negócio:**
- Filtrar por `CD_TIPO_UNIVERSO = 2` para obter o código IBGE do município
- O campo `CD_UNIVERSO` já contém o código IBGE de 7 dígitos

### 4.5 View CONSUMIDORES_ATINGIDOS_VIEW (INSERVICE) - UCs Atingidas

| Campo | Tipo | Descrição | Mapeamento RADAR |
|-------|------|-----------|------------------|
| `num_evento` | NUMBER | Número do evento | **JOIN com AGENCY_EVENT.num_1** |
| `num_instalacao` | NUMBER/VARCHAR | Número da UC | Lista de UCs afetadas |
| `data_interrupcao` | DATE | Data/hora da interrupção | Referência |
| `previsao_restabelecimento` | DATE | Previsão de retorno | Referência |
| `num_dispositivo` | NUMBER | ID do dispositivo | Referência |

---

## 5. Lógica para Identificar Interrupção Programada

### 5.1 Relacionamento entre Tabelas

```
┌─────────────────────┐         ┌─────────────────────────┐
│   AGENCY_EVENT      │         │   SWITCH_PLAN_TASKS     │
├─────────────────────┤         ├─────────────────────────┤
│ NUM_1 (PK)          │◄───────►│ OUTAGE_NUM (FK)         │
│ is_open             │         │ PLAN_ID                 │
│ NUM_CUST            │         │ ...                     │
│ hxgn_cd_municipio   │         └─────────────────────────┘
│ ...                 │
└─────────────────────┘
```

### 5.2 Regra de Identificação

```sql
-- Se existe PLAN_ID para o evento → PROGRAMADA
-- Se não existe → NAO_PROGRAMADA

CASE
    WHEN sp.PLAN_ID IS NOT NULL THEN 'PROGRAMADA'
    ELSE 'NAO_PROGRAMADA'
END AS TIPO_INTERRUPCAO
```

---

## 6. Lógica para Obter Código IBGE do Município

### 6.1 Relacionamento entre Tabelas

```
┌─────────────────────┐         ┌─────────────────────────┐
│ INSERVICE           │         │ INDICADORES             │
│ AGENCY_EVENT        │         │ IND_UNIVERSOS           │
├─────────────────────┤         ├─────────────────────────┤
│ DEV_ID              │◄───────►│ ID_DISPOSITIVO          │
│                     │         │ CD_UNIVERSO (IBGE)      │
│                     │         │ CD_TIPO_UNIVERSO = 2    │
└─────────────────────┘         └─────────────────────────┘
```

### 6.2 JOIN para Obter Código IBGE

```sql
-- O código IBGE vem da tabela IND_UNIVERSOS
JOIN INDICADORES.IND_UNIVERSOS u
    ON u.ID_DISPOSITIVO = a.dev_id
    AND u.CD_TIPO_UNIVERSO = 2
```

**Importante:**
- O filtro `CD_TIPO_UNIVERSO = 2` é necessário para obter o código do município
- O campo `CD_UNIVERSO` já contém o código IBGE de 7 dígitos padrão

---

## 7. View Requerida (Opcional)

**Nota:** A criação de uma view é **opcional**. A API pode consultar diretamente as tabelas com os JOINs necessários. Porém, se preferir criar uma view para simplificar a consulta, segue a especificação:

### 7.1 Nome da View

```sql
VW_INTERRUPCOES_ATIVAS_RADAR
```

### 7.2 Estrutura da View

| Coluna | Tipo Oracle | Obrigatório | Descrição |
|--------|-------------|-------------|-----------|
| `ID_CONJUNTO` | NUMBER | Sim | Código do Conjunto Elétrico |
| `MUNICIPIO_IBGE` | NUMBER(7) | Sim | Código IBGE do município (7 dígitos) |
| `TIPO_INTERRUPCAO` | VARCHAR2(20) | Sim | 'PROGRAMADA' ou 'NAO_PROGRAMADA' |
| `QTD_UCS_AFETADAS` | NUMBER | Sim | Quantidade de UCs afetadas por esta interrupção |
| `DATA_HORA_INICIO` | DATE | Sim | Data/hora de início da interrupção |
| `DATA_HORA_FIM` | DATE | Não | Data/hora de fim (NULL = ativa) |
| `ID_INTERRUPCAO` | NUMBER | Sim | Identificador único da interrupção |
| `ALIMENTADOR` | VARCHAR2(50) | Não | Identificação do alimentador afetado |
| `SUBESTACAO` | VARCHAR2(50) | Não | Identificação da subestação |

### 7.3 DDL da View (Versão Atualizada - Sem Dependência do Ajuri)

```sql
CREATE OR REPLACE VIEW VW_INTERRUPCOES_ATIVAS_RADAR AS
SELECT
    -- Conjunto Elétrico (da tabela OMS_CONNECTIVITY)
    eq.conj AS ID_CONJUNTO,

    -- Município - Código IBGE (da tabela IND_UNIVERSOS)
    u.CD_UNIVERSO AS MUNICIPIO_IBGE,

    -- Tipo de Interrupção (baseado em SWITCH_PLAN_TASKS)
    CASE
        WHEN sp.PLAN_ID IS NOT NULL THEN 'PROGRAMADA'
        ELSE 'NAO_PROGRAMADA'
    END AS TIPO_INTERRUPCAO,

    -- Quantidade de UCs afetadas
    NVL(a.NUM_CUST, 0) AS QTD_UCS_AFETADAS,

    -- Data/Hora de Início
    TO_DATE(SUBSTR(a.ad_ts, 1, 14), 'YYYYMMDDHH24MISS') AS DATA_HORA_INICIO,

    -- Data/Hora de Fim (NULL para ativas)
    NULL AS DATA_HORA_FIM,

    -- Identificador da interrupção
    a.num_1 AS ID_INTERRUPCAO,

    -- Dados complementares
    a.feeder AS ALIMENTADOR,
    a.substation AS SUBESTACAO

FROM
    INSERVICE.AGENCY_EVENT a
-- JOIN para identificar se é interrupção PROGRAMADA
LEFT JOIN (
    SELECT DISTINCT OUTAGE_NUM, PLAN_ID
    FROM INSERVICE.SWITCH_PLAN_TASKS
    WHERE PLAN_ID IS NOT NULL
) sp ON sp.OUTAGE_NUM = a.num_1
-- JOIN para obter o conjunto elétrico
LEFT JOIN
    INSERVICE.OMS_CONNECTIVITY eq
    ON eq.mslink = a.dev_id
    AND eq.dist = 370
-- JOIN para obter o código IBGE do município (da tabela INDICADORES)
JOIN
    INDICADORES.IND_UNIVERSOS u
    ON u.ID_DISPOSITIVO = a.dev_id
    AND u.CD_TIPO_UNIVERSO = 2
WHERE
    a.ag_id = '370'           -- Roraima Energia
    AND a.is_open = 'T'       -- T = Aberto (interrupção ativa)
WITH READ ONLY;

-- Conceder permissão de leitura ao usuário da API RADAR
GRANT SELECT ON VW_INTERRUPCOES_ATIVAS_RADAR TO RADAR_API;
```

**Importante:** Esta view **não depende mais do Ajuri**. O código IBGE é obtido diretamente de `INDICADORES.IND_UNIVERSOS`.

---

## 8. Dependência do Sistema Ajuri

### 8.1 Status: NÃO NECESSÁRIO

**A API 1 não depende mais do Sistema Comercial (Ajuri).**

Anteriormente, o código IBGE do município seria obtido via view `VW_MUNICIPIOS_IBGE_RADAR` do Ajuri. Porém, com a identificação da tabela `INDICADORES.IND_UNIVERSOS`, essa dependência foi eliminada.

### 8.2 Fonte Atual do Código IBGE

O código IBGE é obtido diretamente de:

| Tabela | Campo | Filtro |
|--------|-------|--------|
| `INDICADORES.IND_UNIVERSOS` | `CD_UNIVERSO` | `CD_TIPO_UNIVERSO = 2` |

### 8.3 Verificação de Mapeamento

Execute esta query para verificar se o mapeamento está correto:

```sql
SELECT DISTINCT
    a.dev_id,
    a.hxgn_ds_municipio AS nome_municipio,
    u.CD_UNIVERSO AS cod_ibge
FROM INSERVICE.AGENCY_EVENT a
JOIN INDICADORES.IND_UNIVERSOS u
    ON u.ID_DISPOSITIVO = a.dev_id
    AND u.CD_TIPO_UNIVERSO = 2
WHERE a.ag_id = '370'
ORDER BY a.hxgn_ds_municipio;
```

---

## 9. Códigos IBGE - Municípios de Roraima

| Código IBGE | Município |
|-------------|-----------|
| 1400050 | Boa Vista |
| 1400100 | Alto Alegre |
| 1400027 | Amajari |
| 1400159 | Bonfim |
| 1400175 | Cantá |
| 1400209 | Caracaraí |
| 1400233 | Caroebe |
| 1400282 | Iracema |
| 1400308 | Mucajaí |
| 1400407 | Normandia |
| 1400456 | Pacaraima |
| 1400472 | Rorainópolis |
| 1400506 | São João da Baliza |
| 1400605 | São Luiz |
| 1400704 | Uiramutã |

**Referência:** [IBGE - Códigos dos Municípios](https://www.ibge.gov.br/explica/codigos-dos-municipios.php)

---

## 10. Queries de Verificação

### 10.1 Verificar Estrutura da SWITCH_PLAN_TASKS

```sql
DESC INSERVICE.SWITCH_PLAN_TASKS;

SELECT
    OUTAGE_NUM,
    PLAN_ID,
    COUNT(*) as qtd
FROM INSERVICE.SWITCH_PLAN_TASKS
WHERE OUTAGE_NUM IS NOT NULL
GROUP BY OUTAGE_NUM, PLAN_ID
ORDER BY qtd DESC
FETCH FIRST 20 ROWS ONLY;
```

### 10.2 Verificar Conjuntos Elétricos

```sql
SELECT DISTINCT
    conj,
    mun,
    COUNT(*) AS qtd_equipamentos
FROM INSERVICE.OMS_CONNECTIVITY
WHERE dist = 370
GROUP BY conj, mun
ORDER BY conj;
```

### 10.3 Verificar Query Completa com Todos os JOINs

```sql
-- Testar a query com todos os JOINs (sem dependência do Ajuri)
SELECT
    a.num_1,
    a.is_open,
    a.NUM_CUST,
    a.hxgn_ds_municipio,
    u.CD_UNIVERSO AS cod_ibge,
    eq.conj AS conjunto,
    sp.PLAN_ID,
    CASE WHEN sp.PLAN_ID IS NOT NULL THEN 'PROGRAMADA' ELSE 'NAO_PROGRAMADA' END AS tipo
FROM INSERVICE.AGENCY_EVENT a
LEFT JOIN (
    SELECT DISTINCT OUTAGE_NUM, PLAN_ID
    FROM INSERVICE.SWITCH_PLAN_TASKS
    WHERE PLAN_ID IS NOT NULL
) sp ON sp.OUTAGE_NUM = a.num_1
LEFT JOIN INSERVICE.OMS_CONNECTIVITY eq
    ON eq.mslink = a.dev_id AND eq.dist = 370
JOIN INDICADORES.IND_UNIVERSOS u
    ON u.ID_DISPOSITIVO = a.dev_id
    AND u.CD_TIPO_UNIVERSO = 2
WHERE a.ag_id = '370'
  AND a.is_open = 'T'
ORDER BY a.num_1 DESC
FETCH FIRST 50 ROWS ONLY;
```

### 10.4 Verificar UCs Atingidas por Evento

```sql
-- Verificar a view de consumidores atingidos
SELECT
    num_evento,
    num_instalacao,
    data_interrupcao,
    previsao_restabelecimento,
    num_dispositivo
FROM INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW
WHERE num_evento = 325121200023;  -- Substituir por um evento real
```

---

## 11. Dados Esperados

### 11.1 Exemplo de Dados da View

| ID_CONJUNTO | MUNICIPIO_IBGE | TIPO_INTERRUPCAO | QTD_UCS_AFETADAS | DATA_HORA_INICIO | DATA_HORA_FIM | ID_INTERRUPCAO |
|-------------|----------------|------------------|------------------|------------------|---------------|----------------|
| 1 | 1400050 | NAO_PROGRAMADA | 1200 | 10/12/2025 14:30 | NULL | 12345 |
| 1 | 1400050 | PROGRAMADA | 500 | 10/12/2025 08:00 | NULL | 12340 |
| 1 | 1400175 | NAO_PROGRAMADA | 350 | 10/12/2025 15:45 | NULL | 12346 |
| 2 | 1400209 | PROGRAMADA | 200 | 10/12/2025 09:00 | NULL | 12341 |

### 11.2 Volume Esperado

| Cenário | Registros Estimados |
|---------|---------------------|
| Operação normal | 0 - 50 interrupções ativas |
| Evento climático moderado | 50 - 200 interrupções |
| Evento climático severo | 200 - 500+ interrupções |

---

## 12. Query de Consumo pela API

A API RADAR pode consultar diretamente as tabelas ou usar uma view. Segue a query direta:

```sql
-- Query direta (sem necessidade de view)
SELECT
    eq.conj AS ideConjuntoUnidadeConsumidora,
    u.CD_UNIVERSO AS ideMunicipio,
    SUM(CASE WHEN sp.PLAN_ID IS NOT NULL THEN NVL(a.NUM_CUST, 0) ELSE 0 END) AS qtdOcorrenciaProgramada,
    SUM(CASE WHEN sp.PLAN_ID IS NULL THEN NVL(a.NUM_CUST, 0) ELSE 0 END) AS qtdOcorrenciaNaoProgramada
FROM INSERVICE.AGENCY_EVENT a
LEFT JOIN (
    SELECT DISTINCT OUTAGE_NUM, PLAN_ID
    FROM INSERVICE.SWITCH_PLAN_TASKS
    WHERE PLAN_ID IS NOT NULL
) sp ON sp.OUTAGE_NUM = a.num_1
LEFT JOIN INSERVICE.OMS_CONNECTIVITY eq
    ON eq.mslink = a.dev_id AND eq.dist = 370
JOIN INDICADORES.IND_UNIVERSOS u
    ON u.ID_DISPOSITIVO = a.dev_id
    AND u.CD_TIPO_UNIVERSO = 2
WHERE a.ag_id = '370'
  AND a.is_open = 'T'
GROUP BY
    eq.conj,
    u.CD_UNIVERSO
ORDER BY
    eq.conj,
    u.CD_UNIVERSO;
```

**Nota:** O campo `qtdUCsAtendidas` (total de UCs atendidas no conjunto/município) virá de uma view separada do INSERVICE.

---

## 13. Requisitos Técnicos

### 13.1 Performance

| Requisito | Especificação |
|-----------|---------------|
| **Tempo de resposta** | Máximo 5 segundos para consulta completa |
| **Frequência de consulta** | A cada 30 minutos pela ANEEL |
| **Disponibilidade** | 24x7 (todos os dias da semana) |

### 13.2 Índices Recomendados

```sql
-- Índice para filtro de eventos abertos
CREATE INDEX IDX_AGENCY_EVENT_OPEN
ON INSERVICE.AGENCY_EVENT (AG_ID, IS_OPEN);

-- Índice para JOIN com OMS_CONNECTIVITY
CREATE INDEX IDX_OMS_CONN_MSLINK
ON INSERVICE.OMS_CONNECTIVITY (MSLINK, DIST);

-- Índice para JOIN com SWITCH_PLAN_TASKS
CREATE INDEX IDX_SWITCH_PLAN_OUTAGE
ON INSERVICE.SWITCH_PLAN_TASKS (OUTAGE_NUM, PLAN_ID);

-- Índice para JOIN com município
CREATE INDEX IDX_AGENCY_EVENT_MUN
ON INSERVICE.AGENCY_EVENT (HXGN_CD_MUNICIPIO);
```

### 13.3 Permissões Necessárias

```sql
-- Usuário da API RADAR precisa de SELECT nas tabelas
GRANT SELECT ON INSERVICE.AGENCY_EVENT TO RADAR_API;
GRANT SELECT ON INSERVICE.SWITCH_PLAN_TASKS TO RADAR_API;
GRANT SELECT ON INSERVICE.OMS_CONNECTIVITY TO RADAR_API;
GRANT SELECT ON INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW TO RADAR_API;
GRANT SELECT ON INDICADORES.IND_UNIVERSOS TO RADAR_API;

-- Se for criar a view, conceder também:
-- GRANT SELECT ON VW_INTERRUPCOES_ATIVAS_RADAR TO RADAR_API;
```

**Nota:** Não é mais necessário conceder permissões para views do Ajuri.

---

## 14. Requisito Adicional: Histórico (Abril/2026)

A partir de **01/04/2026**, a ANEEL poderá consultar dados históricos dos últimos 7 dias.

### 14.1 Mecanismo de Snapshot

Será necessário implementar um mecanismo que tire "snapshots" do estado das interrupções a cada 30 minutos:

```sql
-- Tabela de histórico
CREATE TABLE TB_INTERRUPCOES_HISTORICO_RADAR (
    SNAPSHOT_ID         NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    SNAPSHOT_TIMESTAMP  DATE NOT NULL,
    ID_CONJUNTO         NUMBER,
    MUNICIPIO_IBGE      NUMBER(7),
    TIPO_INTERRUPCAO    VARCHAR2(20),
    QTD_UCS_AFETADAS    NUMBER,
    ID_INTERRUPCAO      NUMBER
);

-- Job para executar a cada 30 minutos
BEGIN
    DBMS_SCHEDULER.CREATE_JOB (
        job_name        => 'JOB_SNAPSHOT_INTERRUPCOES_RADAR',
        job_type        => 'PLSQL_BLOCK',
        job_action      => 'BEGIN INSERT INTO TB_INTERRUPCOES_HISTORICO_RADAR
                           (SNAPSHOT_TIMESTAMP, ID_CONJUNTO, MUNICIPIO_IBGE,
                            TIPO_INTERRUPCAO, QTD_UCS_AFETADAS, ID_INTERRUPCAO)
                           SELECT SYSDATE, ID_CONJUNTO, MUNICIPIO_IBGE,
                                  TIPO_INTERRUPCAO, QTD_UCS_AFETADAS, ID_INTERRUPCAO
                           FROM VW_INTERRUPCOES_ATIVAS_RADAR; COMMIT; END;',
        start_date      => SYSTIMESTAMP,
        repeat_interval => 'FREQ=MINUTELY;INTERVAL=30',
        enabled         => TRUE
    );
END;
/
```

**Nota:** Este requisito é para implementação futura (Abril/2026).

---

## 15. Checklist de Entrega

### 15.1 Fontes de Dados (já disponíveis)

- [x] Tabela `INSERVICE.AGENCY_EVENT` disponível
- [x] Tabela `INSERVICE.SWITCH_PLAN_TASKS` disponível
- [x] Tabela `INSERVICE.OMS_CONNECTIVITY` disponível
- [x] View `INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW` disponível
- [x] Tabela `INDICADORES.IND_UNIVERSOS` disponível

### 15.2 Permissões e Configuração

- [ ] Usuário `RADAR_API` criado
- [ ] Permissão SELECT concedida nas tabelas do INSERVICE
- [ ] Permissão SELECT concedida na tabela `INDICADORES.IND_UNIVERSOS`
- [ ] (Opcional) View `VW_INTERRUPCOES_ATIVAS_RADAR` criada

### 15.3 Validação de JOINs

- [ ] JOIN com `SWITCH_PLAN_TASKS` testado (tipo interrupção)
- [ ] JOIN com `OMS_CONNECTIVITY` testado (conjunto elétrico)
- [ ] JOIN com `IND_UNIVERSOS` testado (código IBGE)
- [ ] Mapeamento DEV_ID ↔ ID_DISPOSITIVO validado

### 15.4 Performance

- [ ] Índices de performance criados (se necessário)
- [ ] Testes de volume realizados
- [ ] Tempo de resposta validado (< 5 segundos)

### 15.5 Validação Final

- [ ] Dados de exemplo validados
- [ ] Códigos IBGE retornando corretamente (7 dígitos)
- [ ] Classificação PROGRAMADA/NAO_PROGRAMADA correta
- [ ] Testes com equipe RADAR realizados

---

## 16. Resumo dos Campos Mapeados

| Campo RADAR | Origem | Tabela | Observação |
|-------------|--------|--------|------------|
| `ID_CONJUNTO` | `conj` | INSERVICE.OMS_CONNECTIVITY | Via JOIN por dev_id/mslink |
| `MUNICIPIO_IBGE` | `CD_UNIVERSO` | INDICADORES.IND_UNIVERSOS | Via JOIN ID_DISPOSITIVO = dev_id, CD_TIPO_UNIVERSO = 2 |
| `TIPO_INTERRUPCAO` | `PLAN_ID` | INSERVICE.SWITCH_PLAN_TASKS | Se PLAN_ID existe = PROGRAMADA |
| `QTD_UCS_AFETADAS` | `NUM_CUST` | INSERVICE.AGENCY_EVENT | Direto |
| `DATA_HORA_INICIO` | `ad_ts` | INSERVICE.AGENCY_EVENT | Converter formato |
| `DATA_HORA_FIM` | `xdts` | INSERVICE.AGENCY_EVENT | NULL para ativas |
| `ID_INTERRUPCAO` | `num_1` | INSERVICE.AGENCY_EVENT | Direto |
| Filtro ativas | `is_open = 'T'` | INSERVICE.AGENCY_EVENT | T = Aberto |
| Filtro agência | `ag_id = '370'` | INSERVICE.AGENCY_EVENT | Roraima Energia |

### 16.1 Relacionamentos (JOINs)

```
INSERVICE.AGENCY_EVENT (a)
    │
    ├── LEFT JOIN INSERVICE.SWITCH_PLAN_TASKS (sp)
    │       ON sp.OUTAGE_NUM = a.NUM_1
    │       → Identificar se é PROGRAMADA
    │
    ├── LEFT JOIN INSERVICE.OMS_CONNECTIVITY (eq)
    │       ON eq.MSLINK = a.DEV_ID AND eq.DIST = 370
    │       → Obter conjunto elétrico
    │
    ├── JOIN INDICADORES.IND_UNIVERSOS (u)
    │       ON u.ID_DISPOSITIVO = a.DEV_ID AND u.CD_TIPO_UNIVERSO = 2
    │       → Obter código IBGE do município
    │
    └── LEFT JOIN INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW (ca)
            ON ca.NUM_EVENTO = a.NUM_1
            → Obter lista de UCs atingidas (opcional)
```

**Nota:** Não há dependência do Sistema Ajuri para obter o código IBGE.

---

## 17. Contatos

### 17.1 Projeto RADAR

| Função | Contato |
|--------|---------|
| Coordenação do Projeto | [A definir] |
| Equipe de Desenvolvimento API | ti.radar@roraimaenergia.com.br |

### 17.2 Dúvidas Técnicas

Para dúvidas sobre os requisitos deste documento, entrar em contato com a equipe do Projeto RADAR.

---

## 18. Cronograma Sugerido

| Etapa | Atividade |
|-------|-----------|
| 1 | Validar mapeamento DEV_ID ↔ ID_DISPOSITIVO (IND_UNIVERSOS) |
| 2 | Criar usuário RADAR_API e conceder permissões |
| 3 | (Opcional) Criar view VW_INTERRUPCOES_ATIVAS_RADAR |
| 4 | Criar índices de performance (se necessário) |
| 5 | Testes de performance |
| 6 | Validação com equipe RADAR |
| 7 | Ajustes finais |

**Nota:** Não há dependência do Sistema Ajuri. A implementação pode iniciar imediatamente pois todas as tabelas necessárias já estão disponíveis.

---

*Documento gerado em Dezembro/2025 - Projeto RADAR - Roraima Energia S/A*
