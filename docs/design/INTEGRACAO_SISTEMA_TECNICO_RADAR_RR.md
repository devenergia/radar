# Documento de Integração com Sistema Técnico
## Projeto RADAR Roraima Energia

**Versão:** 2.0
**Data:** 10/12/2025
**Empresa:** Roraima Energia S/A
**Status:** Draft

---

## Índice

1. [Visão Geral da Integração](#1-visão-geral-da-integração)
2. [Arquitetura de Integração](#2-arquitetura-de-integração)
3. [Configuração do DBLink](#3-configuração-do-dblink)
4. [Dados Requeridos do Sistema Técnico](#4-dados-requeridos-do-sistema-técnico)
5. [Views e Consultas de Integração](#5-views-e-consultas-de-integração)
6. [Dados para APIs ANEEL (Ofício 14/2025)](#6-dados-para-apis-aneel-ofício-142025)
7. [Dados para Portal Público (REN 1.137)](#7-dados-para-portal-público-ren-1137)
8. [Dados para Notificações SMS/WhatsApp](#8-dados-para-notificações-smswhatsapp)
9. [Dados para Indicador DISE](#9-dados-para-indicador-dise)
10. [Mapeamento de Códigos](#10-mapeamento-de-códigos)
11. [Frequência de Atualização](#11-frequência-de-atualização)
12. [Tratamento de Erros](#12-tratamento-de-erros)
13. [Segurança e Permissões](#13-segurança-e-permissões)
14. [Checklist de Implementação](#14-checklist-de-implementação)

---

## 1. Visão Geral da Integração

### 1.1 Objetivo

Este documento especifica todos os dados e informações que o **Sistema Técnico** da Roraima Energia deve fornecer para o **Sistema RADAR**, bem como a estrutura de integração via DBLink.

### 1.2 Sistemas Envolvidos

| Sistema | Função | Banco | Tipo de Integração |
|---------|--------|-------|-------------------|
| **Sistema Técnico** | Fonte de dados de interrupções, equipamentos e DISE | Oracle | DBLink (leitura) |
| **Sistema Comercial (Ajuri)** | Fonte de dados de UCs, consumidores, demandas | Oracle | DBLink (leitura) |
| **RADAR** | Sistema centralizador e APIs ANEEL | Oracle | Banco próprio |

### 1.3 Fluxo de Dados

```
┌─────────────────────┐     ┌─────────────────────┐
│   Sistema Técnico   │     │  Sistema Comercial  │
│      (Oracle)       │     │   (Ajuri - Oracle)  │
└──────────┬──────────┘     └──────────┬──────────┘
           │                           │
           │ DBLink                    │ DBLink
           │                           │
           ▼                           ▼
┌──────────────────────────────────────────────────┐
│              ORACLE - RADAR                       │
│  ┌────────────────┐    ┌────────────────┐        │
│  │   Synonyms /   │    │   Synonyms /   │        │
│  │ Views Remotas  │    │ Views Remotas  │        │
│  │ Sistema Técnico│    │ Sistema Ajuri  │        │
│  └───────┬────────┘    └───────┬────────┘        │
│          │                     │                  │
│          ▼                     ▼                  │
│  ┌─────────────────────────────────────┐         │
│  │      Materialized Views             │         │
│  │   (Cache local - refresh periódico) │         │
│  └─────────────────────────────────────┘         │
│                      │                            │
│                      ▼                            │
│  ┌─────────────────────────────────────┐         │
│  │        Backend FastAPI              │         │
│  │   APIs ANEEL + Portal + Dashboard   │         │
│  └─────────────────────────────────────┘         │
└──────────────────────────────────────────────────┘
```

### 1.4 Regulamentações Atendidas

| Regulamentação | Requisito | Dados do Sistema Técnico |
|----------------|-----------|-------------------------|
| Ofício 14/2025 | API Interrupções Ativas | Interrupções, UCs afetadas |
| REN 1.137 Art. 106-107 | Portal Público | Status ocorrências, equipes, CHI |
| REN 1.137 Art. 105 | Notificações | UCs afetadas, causa, previsão |
| REN 1.137 Art. 173/180-A | Indicador DISE | DISE calculado pelo Sistema Técnico |

---

## 2. Arquitetura de Integração

### 2.1 Diagrama de Integração

```
┌────────────────────────────────────────────────────────────────────┐
│                  SISTEMA TÉCNICO (Oracle)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Interrupções │  │ Equipamentos │  │   DISE       │             │
│  │   Ativas     │  │   Status     │  │ (calculado)  │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Equipes    │  │ Alimentadores│  │  Ocorrências │             │
│  │   Campo      │  │              │  │   Históricas │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└──────────────────────────┬─────────────────────────────────────────┘
                           │
                    Oracle Database Link
                           │
                           ▼
┌────────────────────────────────────────────────────────────────────┐
│                      ORACLE - RADAR                                 │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 Synonyms: Sistema Técnico                    │   │
│  │  ┌────────────────────┐  ┌────────────────────┐             │   │
│  │  │ SYN_INTERRUPCOES   │  │ SYN_EQUIPAMENTOS   │             │   │
│  │  │ (synonym @SISTEC)  │  │ (synonym @SISTEC)  │             │   │
│  │  └────────────────────┘  └────────────────────┘             │   │
│  │  ┌────────────────────┐  ┌────────────────────┐             │   │
│  │  │ SYN_EQUIPES_CAMPO  │  │ SYN_DISE           │             │   │
│  │  │ (synonym @SISTEC)  │  │ (synonym @SISTEC)  │             │   │
│  │  └────────────────────┘  └────────────────────┘             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 Synonyms: Sistema Ajuri                      │   │
│  │  ┌────────────────────┐  ┌────────────────────┐             │   │
│  │  │ SYN_UNIDADES_CONS  │  │ SYN_CONSUMIDORES   │             │   │
│  │  │ (synonym @AJURI)   │  │ (synonym @AJURI)   │             │   │
│  │  └────────────────────┘  └────────────────────┘             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 Tabelas/Views Locais RADAR                   │   │
│  │  ┌────────────────────┐  ┌────────────────────┐             │   │
│  │  │ MV_INTERRUPCOES    │  │ MV_PORTAL_PUBLICO  │             │   │
│  │  │ (materialized view)│  │ (materialized view)│             │   │
│  │  └────────────────────┘  └────────────────────┘             │   │
│  │  ┌────────────────────┐  ┌────────────────────┐             │   │
│  │  │ INTERRUPCAO_SNAP   │  │ NOTIFICACOES_LOG   │             │   │
│  │  │ (tabela local)     │  │ (tabela local)     │             │   │
│  │  └────────────────────┘  └────────────────────┘             │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

### 2.2 Tecnologias

| Componente | Tecnologia | Versão |
|------------|------------|--------|
| Banco RADAR | Oracle Database | 19c+ |
| Banco Sistema Técnico | Oracle Database | 19c+ |
| Banco Ajuri | Oracle Database | 19c+ |
| Backend | Python + FastAPI | 3.11+ / 0.100+ |
| ORM | SQLAlchemy + oracledb | 2.0+ |
| Cache | Redis | 7+ |
| Task Queue | Celery + Redis | 5.3+ |

---

## 3. Configuração do DBLink (Oracle)

### 3.1 Configuração do tnsnames.ora

No servidor do banco RADAR, configurar o arquivo `$ORACLE_HOME/network/admin/tnsnames.ora`:

```
-- Entrada para o Sistema Técnico
SISTEC =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = servidor-sistema-tecnico)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = ORCL)
    )
  )

-- Entrada para o Sistema Ajuri
AJURI =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = servidor-ajuri)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = AJURI)
    )
  )
```

### 3.2 Criação do Database Link - Sistema Técnico

```sql
-- Criar Database Link para Sistema Técnico
CREATE DATABASE LINK SISTEC_LINK
    CONNECT TO RADAR_READONLY
    IDENTIFIED BY "senha_segura"
    USING 'SISTEC';

-- Testar conexão
SELECT * FROM DUAL@SISTEC_LINK;
```

### 3.3 Criação do Database Link - Sistema Ajuri

```sql
-- Criar Database Link para Sistema Ajuri
CREATE DATABASE LINK AJURI_LINK
    CONNECT TO RADAR_READONLY
    IDENTIFIED BY "senha_segura"
    USING 'AJURI';

-- Testar conexão
SELECT * FROM DUAL@AJURI_LINK;
```

### 3.4 Criação de Synonyms para Tabelas Remotas

```sql
-- Synonyms para Sistema Técnico
CREATE SYNONYM SYN_INTERRUPCOES_ATIVAS
    FOR OPERACAO.VW_INTERRUPCOES_ATIVAS_RADAR@SISTEC_LINK;

CREATE SYNONYM SYN_ALIMENTADORES
    FOR CADASTRO.VW_ALIMENTADORES_RADAR@SISTEC_LINK;

CREATE SYNONYM SYN_CONJUNTOS_ELETRICOS
    FOR CADASTRO.VW_CONJUNTOS_RADAR@SISTEC_LINK;

CREATE SYNONYM SYN_EQUIPES_CAMPO
    FOR OPERACAO.VW_EQUIPES_CAMPO_RADAR@SISTEC_LINK;

CREATE SYNONYM SYN_DISE
    FOR INDICADORES.VW_DISE_RADAR@SISTEC_LINK;

CREATE SYNONYM SYN_UCS_INTERRUPCAO
    FOR OPERACAO.VW_UCS_INTERRUPCAO_RADAR@SISTEC_LINK;

CREATE SYNONYM SYN_HISTORICO_INTERRUPCOES
    FOR HISTORICO.VW_HISTORICO_INTERRUPCOES_RADAR@SISTEC_LINK;

-- Synonyms para Sistema Ajuri
CREATE SYNONYM SYN_CONTATOS_CONSUMIDORES
    FOR COMERCIAL.VW_CONTATOS_RADAR@AJURI_LINK;

CREATE SYNONYM SYN_UNIDADES_CONSUMIDORAS
    FOR COMERCIAL.VW_UNIDADES_CONSUMIDORAS@AJURI_LINK;
```

### 3.5 Permissões

```sql
-- Conceder permissões ao usuário da aplicação
GRANT SELECT ON SYN_INTERRUPCOES_ATIVAS TO RADAR_APP;
GRANT SELECT ON SYN_ALIMENTADORES TO RADAR_APP;
GRANT SELECT ON SYN_CONJUNTOS_ELETRICOS TO RADAR_APP;
GRANT SELECT ON SYN_EQUIPES_CAMPO TO RADAR_APP;
GRANT SELECT ON SYN_DISE TO RADAR_APP;
GRANT SELECT ON SYN_UCS_INTERRUPCAO TO RADAR_APP;
GRANT SELECT ON SYN_HISTORICO_INTERRUPCOES TO RADAR_APP;
GRANT SELECT ON SYN_CONTATOS_CONSUMIDORES TO RADAR_APP;
GRANT SELECT ON SYN_UNIDADES_CONSUMIDORAS TO RADAR_APP;
```

---

## 4. Dados Requeridos do Sistema Técnico

### 4.1 Tabela: Interrupções Ativas

O Sistema Técnico **DEVE** fornecer uma view com as seguintes informações:

```sql
-- Estrutura esperada no Sistema Técnico: VW_INTERRUPCOES_ATIVAS_RADAR
-- Esta view deve ser criada no schema OPERACAO do Sistema Técnico

CREATE OR REPLACE VIEW OPERACAO.VW_INTERRUPCOES_ATIVAS_RADAR AS
SELECT
    -- Identificação
    id_interrupcao,              -- VARCHAR2(50) NOT NULL - ID único da interrupção

    -- Classificação
    tipo_interrupcao,            -- VARCHAR2(20) NOT NULL - 'PROGRAMADA' ou 'NAO_PROGRAMADA'
    origem,                      -- VARCHAR2(50) - Origem: 'INSERVICE', 'MANUAL', 'CRM'

    -- Localização
    id_alimentador,              -- VARCHAR2(20) NOT NULL - Código do alimentador
    nome_alimentador,            -- VARCHAR2(100) - Nome do alimentador
    id_subestacao,               -- VARCHAR2(20) - Código da subestação
    nome_subestacao,             -- VARCHAR2(100) - Nome da subestação

    -- Temporalidade
    data_hora_inicio,            -- TIMESTAMP NOT NULL - Início da interrupção
    data_hora_fim,               -- TIMESTAMP - Fim (NULL se ainda ativa)
    previsao_restabelecimento,   -- TIMESTAMP - Previsão de restabelecimento

    -- Causa
    id_causa,                    -- NUMBER(10) - Código da causa
    descricao_causa,             -- VARCHAR2(200) - Descrição da causa
    causa_conhecida,             -- NUMBER(1) DEFAULT 0 - 1=conhecida, 0=não

    -- Status da Ocorrência (REN 1.137 Art. 107)
    status_ocorrencia,           -- VARCHAR2(30) NOT NULL - 'EM_PREPARACAO', 'DESLOCAMENTO', 'EM_EXECUCAO', 'CONCLUIDA'

    -- Quantitativos
    qtd_ucs_afetadas,            -- NUMBER(10) NOT NULL - Quantidade de UCs afetadas
    qtd_consumidores,            -- NUMBER(10) - Quantidade de consumidores

    -- Equipes (REN 1.137 Art. 107)
    qtd_equipes_designadas,      -- NUMBER(10) DEFAULT 0 - Equipes designadas

    -- Geolocalização
    latitude,                    -- NUMBER(10,7) - Latitude do ponto
    longitude,                   -- NUMBER(10,7) - Longitude do ponto

    -- Área
    municipio_ibge,              -- NUMBER(10) - Código IBGE do município
    bairro,                      -- VARCHAR2(100) - Bairro/Localidade
    tipo_area,                   -- VARCHAR2(10) - 'URBANO' ou 'RURAL'

    -- Auditoria
    data_atualizacao             -- TIMESTAMP NOT NULL - Última atualização
FROM ... -- Tabelas internas do Sistema Técnico
WHERE data_hora_fim IS NULL;  -- Apenas interrupções ativas

-- Acesso via DBLink no RADAR:
-- SELECT * FROM SYN_INTERRUPCOES_ATIVAS;
-- ou
-- SELECT * FROM OPERACAO.VW_INTERRUPCOES_ATIVAS_RADAR@SISTEC_LINK;
```

### 4.2 Tabela: Equipamentos/Alimentadores

```sql
-- Estrutura esperada: ALIMENTADORES
CREATE FOREIGN TABLE sistema_tecnico.ft_alimentadores (
    id_alimentador          VARCHAR(20) PRIMARY KEY,
    nome_alimentador        VARCHAR(100) NOT NULL,
    id_subestacao           VARCHAR(20),
    nome_subestacao         VARCHAR(100),
    tensao_kv               DECIMAL(10,2),
    extensao_km             DECIMAL(10,2),
    qtd_ucs_total           INTEGER NOT NULL,       -- Total de UCs no alimentador
    municipio_principal     INTEGER,                 -- Código IBGE município principal
    ativo                   BOOLEAN DEFAULT TRUE,
    data_atualizacao        TIMESTAMP
)
SERVER sistema_tecnico_server
OPTIONS (schema 'CADASTRO', table 'VW_ALIMENTADORES_RADAR');
```

### 4.3 Tabela: Conjuntos Elétricos

```sql
-- Estrutura esperada: CONJUNTOS_ELETRICOS
CREATE FOREIGN TABLE sistema_tecnico.ft_conjuntos_eletricos (
    id_conjunto             INTEGER PRIMARY KEY,     -- Código do conjunto ANEEL
    nome_conjunto           VARCHAR(100) NOT NULL,
    codigo_aneel            VARCHAR(20),             -- Código oficial ANEEL
    qtd_ucs_total           INTEGER NOT NULL,        -- Total de UCs no conjunto
    municipios_abrangidos   TEXT,                    -- Lista de códigos IBGE (JSON)
    ativo                   BOOLEAN DEFAULT TRUE,
    data_atualizacao        TIMESTAMP
)
SERVER sistema_tecnico_server
OPTIONS (schema 'CADASTRO', table 'VW_CONJUNTOS_RADAR');
```

### 4.4 Tabela: Equipes em Campo

```sql
-- Estrutura esperada: EQUIPES_CAMPO (REN 1.137 Art. 107)
CREATE FOREIGN TABLE sistema_tecnico.ft_equipes_campo (
    id_equipe               VARCHAR(20) PRIMARY KEY,
    nome_equipe             VARCHAR(100),
    tipo_equipe             VARCHAR(50),             -- 'LINHA_VIVA', 'EMERGENCIA', 'PROGRAMADA'
    status                  VARCHAR(30) NOT NULL,    -- 'DISPONIVEL', 'EM_DESLOCAMENTO', 'EM_CAMPO'
    id_interrupcao_atual    VARCHAR(50),             -- Interrupção sendo atendida
    latitude_atual          DECIMAL(10,7),
    longitude_atual         DECIMAL(10,7),
    hora_ultima_posicao     TIMESTAMP,
    data_atualizacao        TIMESTAMP
)
SERVER sistema_tecnico_server
OPTIONS (schema 'OPERACAO', table 'VW_EQUIPES_CAMPO_RADAR');
```

### 4.5 Tabela: DISE - Indicador de Emergência

**IMPORTANTE:** O cálculo do DISE é realizado pelo Sistema Técnico. O RADAR apenas consome o valor calculado.

```sql
-- Estrutura esperada: DISE (Art. 173/180-A REN 1.137)
CREATE FOREIGN TABLE sistema_tecnico.ft_dise (
    id_registro             BIGINT PRIMARY KEY,

    -- Identificação da Emergência
    id_emergencia           VARCHAR(50) NOT NULL,    -- ID da situação de emergência
    descricao_emergencia    VARCHAR(200),
    tipo_evento             VARCHAR(50),             -- 'TEMPESTADE', 'ENCHENTE', etc.

    -- Período
    data_inicio_emergencia  TIMESTAMP NOT NULL,
    data_fim_emergencia     TIMESTAMP,               -- NULL se ainda ativa
    emergencia_ativa        BOOLEAN DEFAULT TRUE,

    -- Unidade Consumidora
    id_uc                   VARCHAR(20) NOT NULL,    -- Código da UC
    municipio_ibge          INTEGER NOT NULL,
    tipo_area               VARCHAR(10) NOT NULL,    -- 'URBANO' ou 'RURAL'

    -- Interrupção
    id_interrupcao          VARCHAR(50) NOT NULL,
    data_inicio_interrupcao TIMESTAMP NOT NULL,
    data_fim_interrupcao    TIMESTAMP,               -- NULL se ainda interrompida

    -- DISE Calculado
    dise_minutos            INTEGER NOT NULL,        -- Duração em minutos
    dise_horas              DECIMAL(10,2) NOT NULL,  -- Duração em horas
    limite_horas            INTEGER NOT NULL,        -- 24 (urbano) ou 48 (rural)
    em_violacao             BOOLEAN DEFAULT FALSE,   -- TRUE se dise_horas > limite_horas
    percentual_limite       DECIMAL(5,2),            -- (dise_horas / limite_horas) * 100

    -- Decreto (se aplicável)
    decreto_estadual        VARCHAR(50),
    decreto_municipal       VARCHAR(50),

    -- Auditoria
    data_calculo            TIMESTAMP NOT NULL,      -- Data/hora do cálculo
    data_atualizacao        TIMESTAMP
)
SERVER sistema_tecnico_server
OPTIONS (schema 'INDICADORES', table 'VW_DISE_RADAR');
```

### 4.6 Tabela: Histórico de Interrupções

```sql
-- Estrutura esperada: HISTORICO_INTERRUPCOES
CREATE FOREIGN TABLE sistema_tecnico.ft_historico_interrupcoes (
    id_interrupcao          VARCHAR(50) NOT NULL,
    tipo_interrupcao        VARCHAR(20) NOT NULL,
    id_alimentador          VARCHAR(20),
    municipio_ibge          INTEGER,
    data_hora_inicio        TIMESTAMP NOT NULL,
    data_hora_fim           TIMESTAMP NOT NULL,
    duracao_minutos         INTEGER,
    qtd_ucs_afetadas        INTEGER,
    id_causa                INTEGER,
    descricao_causa         VARCHAR(200),
    chi                     DECIMAL(15,2),           -- Consumidor Hora Interrompido
    tipo_area               VARCHAR(10),
    data_registro           TIMESTAMP
)
SERVER sistema_tecnico_server
OPTIONS (schema 'HISTORICO', table 'VW_HISTORICO_INTERRUPCOES_RADAR');
```

### 4.7 Tabela: UCs por Interrupção

```sql
-- Relação de UCs afetadas por cada interrupção
CREATE FOREIGN TABLE sistema_tecnico.ft_ucs_interrupcao (
    id_interrupcao          VARCHAR(50) NOT NULL,
    id_uc                   VARCHAR(20) NOT NULL,
    data_hora_inicio        TIMESTAMP NOT NULL,
    data_hora_fim           TIMESTAMP,
    municipio_ibge          INTEGER,
    tipo_area               VARCHAR(10),             -- 'URBANO' ou 'RURAL'
    PRIMARY KEY (id_interrupcao, id_uc)
)
SERVER sistema_tecnico_server
OPTIONS (schema 'OPERACAO', table 'VW_UCS_INTERRUPCAO_RADAR');
```

---

## 5. Views e Consultas de Integração

### 5.1 Materialized View: Interrupções para API ANEEL (Oracle)

```sql
-- Materialized view para API /quantitativointerrupcoesativas
CREATE MATERIALIZED VIEW MV_INTERRUPCOES_ANEEL
BUILD IMMEDIATE
REFRESH FAST ON DEMAND
AS
SELECT
    ce.id_conjunto AS ide_conjunto_unidade_consumidora,
    i.municipio_ibge AS ide_municipio,
    NVL(ce.qtd_ucs_total, 0) AS qtd_ucs_atendidas,
    NVL(SUM(CASE WHEN i.tipo_interrupcao = 'PROGRAMADA' THEN i.qtd_ucs_afetadas ELSE 0 END), 0) AS qtd_ocorrencia_programada,
    NVL(SUM(CASE WHEN i.tipo_interrupcao = 'NAO_PROGRAMADA' THEN i.qtd_ucs_afetadas ELSE 0 END), 0) AS qtd_ocorrencia_nao_programada,
    SYSTIMESTAMP AS data_atualizacao
FROM SYN_INTERRUPCOES_ATIVAS i
LEFT JOIN SYN_CONJUNTOS_ELETRICOS ce
    ON i.municipio_ibge IN (
        SELECT REGEXP_SUBSTR(ce.municipios_abrangidos, '[^,]+', 1, LEVEL)
        FROM DUAL
        CONNECT BY REGEXP_SUBSTR(ce.municipios_abrangidos, '[^,]+', 1, LEVEL) IS NOT NULL
    )
WHERE i.data_hora_fim IS NULL  -- Apenas interrupções ativas
GROUP BY ce.id_conjunto, i.municipio_ibge, ce.qtd_ucs_total;

-- Índice para performance
CREATE UNIQUE INDEX IDX_MV_INTERRUPCOES_ANEEL
ON MV_INTERRUPCOES_ANEEL (ide_conjunto_unidade_consumidora, ide_municipio);

-- Refresh manual (será chamado pelo Celery/Scheduler)
-- EXEC DBMS_MVIEW.REFRESH('MV_INTERRUPCOES_ANEEL', 'C');
```

### 5.2 Materialized View: Portal Público (Oracle)

```sql
-- Materialized view para Portal Público (REN 1.137)
CREATE MATERIALIZED VIEW MV_PORTAL_PUBLICO
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
AS
SELECT
    i.id_interrupcao,
    i.tipo_interrupcao,
    i.municipio_ibge,
    m.nome AS municipio_nome,
    i.bairro,
    i.latitude,
    i.longitude,
    i.data_hora_inicio,
    i.previsao_restabelecimento,
    i.status_ocorrencia,
    i.qtd_ucs_afetadas,
    i.qtd_equipes_designadas,
    i.descricao_causa,
    i.causa_conhecida,
    i.tipo_area,

    -- Cálculo da duração em horas
    ROUND((SYSDATE - CAST(i.data_hora_inicio AS DATE)) * 24, 2) AS duracao_horas,

    -- Classificação por faixa de duração (Art. 107)
    CASE
        WHEN (SYSDATE - CAST(i.data_hora_inicio AS DATE)) * 24 < 1 THEN 'ate1h'
        WHEN (SYSDATE - CAST(i.data_hora_inicio AS DATE)) * 24 < 3 THEN '1a3h'
        WHEN (SYSDATE - CAST(i.data_hora_inicio AS DATE)) * 24 < 6 THEN '3a6h'
        WHEN (SYSDATE - CAST(i.data_hora_inicio AS DATE)) * 24 < 12 THEN '6a12h'
        WHEN (SYSDATE - CAST(i.data_hora_inicio AS DATE)) * 24 < 24 THEN '12a24h'
        WHEN (SYSDATE - CAST(i.data_hora_inicio AS DATE)) * 24 < 48 THEN '24a48h'
        ELSE 'mais48h'
    END AS faixa_duracao,

    -- CHI - Consumidor Hora Interrompido
    ROUND(i.qtd_ucs_afetadas * ((SYSDATE - CAST(i.data_hora_inicio AS DATE)) * 24), 2) AS chi,

    SYSTIMESTAMP AS data_atualizacao
FROM SYN_INTERRUPCOES_ATIVAS i
LEFT JOIN MUNICIPIO m ON i.municipio_ibge = m.id
WHERE i.data_hora_fim IS NULL;

-- Índices
CREATE INDEX IDX_MV_PORTAL_MUNICIPIO ON MV_PORTAL_PUBLICO (municipio_ibge);
CREATE INDEX IDX_MV_PORTAL_FAIXA ON MV_PORTAL_PUBLICO (faixa_duracao);
```

### 5.3 Materialized View: Equipes em Campo (Oracle)

```sql
-- Materialized view para status de equipes (REN 1.137 Art. 107)
CREATE MATERIALIZED VIEW MV_EQUIPES_STATUS
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
AS
SELECT
    SUM(CASE WHEN status = 'DISPONIVEL' THEN 1 ELSE 0 END) AS equipes_disponiveis,
    SUM(CASE WHEN status = 'EM_DESLOCAMENTO' THEN 1 ELSE 0 END) AS equipes_deslocamento,
    SUM(CASE WHEN status = 'EM_CAMPO' THEN 1 ELSE 0 END) AS equipes_em_campo,
    COUNT(*) AS equipes_total,
    SYSTIMESTAMP AS data_atualizacao
FROM SYN_EQUIPES_CAMPO;
```

### 5.4 Materialized View: DISE Consolidado (Oracle)

```sql
-- Materialized view para indicadores DISE
CREATE MATERIALIZED VIEW MV_DISE_CONSOLIDADO
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
AS
SELECT
    id_emergencia,
    descricao_emergencia,
    tipo_evento,
    data_inicio_emergencia,
    emergencia_ativa,
    tipo_area,

    -- Métricas
    COUNT(DISTINCT id_uc) AS total_ucs_afetadas,
    ROUND(AVG(dise_horas), 2) AS dise_medio_horas,
    MAX(dise_horas) AS dise_maximo_horas,
    SUM(CASE WHEN em_violacao = 1 THEN 1 ELSE 0 END) AS ucs_em_violacao,

    -- Limite por tipo de área
    MAX(limite_horas) AS limite_horas,

    SYSTIMESTAMP AS data_atualizacao
FROM SYN_DISE
GROUP BY
    id_emergencia,
    descricao_emergencia,
    tipo_evento,
    data_inicio_emergencia,
    emergencia_ativa,
    tipo_area;
```

### 5.5 Procedure de Refresh das Views (Oracle)

```sql
-- Procedure para refresh de todas as views materializadas
CREATE OR REPLACE PROCEDURE REFRESH_ALL_MVIEWS AS
    v_error_msg VARCHAR2(4000);
BEGIN
    -- Refresh das Materialized Views
    DBMS_MVIEW.REFRESH('MV_INTERRUPCOES_ANEEL', 'C');
    DBMS_MVIEW.REFRESH('MV_PORTAL_PUBLICO', 'C');
    DBMS_MVIEW.REFRESH('MV_EQUIPES_STATUS', 'C');
    DBMS_MVIEW.REFRESH('MV_DISE_CONSOLIDADO', 'C');

    -- Log de atualização
    INSERT INTO LOG_REFRESH (view_name, refresh_time, status)
    VALUES ('ALL', SYSTIMESTAMP, 'SUCCESS');
    COMMIT;

EXCEPTION WHEN OTHERS THEN
    v_error_msg := SQLERRM;
    INSERT INTO LOG_REFRESH (view_name, refresh_time, status, error_message)
    VALUES ('ALL', SYSTIMESTAMP, 'ERROR', v_error_msg);
    COMMIT;
    RAISE;
END;
/

-- Tabela de log de refresh
CREATE TABLE LOG_REFRESH (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    view_name VARCHAR2(100) NOT NULL,
    refresh_time TIMESTAMP DEFAULT SYSTIMESTAMP,
    status VARCHAR2(20),
    error_message VARCHAR2(4000)
);
```

---

## 6. Dados para APIs ANEEL (Ofício 14/2025)

### 6.1 API: /quantitativointerrupcoesativas

**Campos obrigatórios do Sistema Técnico:**

| Campo Sistema Técnico | Campo API ANEEL | Tipo | Obrigatório |
|-----------------------|-----------------|------|-------------|
| id_conjunto | ideConjuntoUnidadeConsumidora | INTEGER | Sim |
| municipio_ibge | ideMunicipio | INTEGER | Sim |
| qtd_ucs_total | qtdUCsAtendidas | INTEGER | Sim |
| qtd_ucs_afetadas (PROGRAMADA) | qtdOcorrenciaProgramada | INTEGER | Sim |
| qtd_ucs_afetadas (NAO_PROGRAMADA) | qtdOcorrenciaNaoProgramada | INTEGER | Sim |

**Consulta de exemplo:**
```sql
SELECT
    ide_conjunto_unidade_consumidora,
    ide_municipio,
    qtd_ucs_atendidas,
    qtd_ocorrencia_programada,
    qtd_ocorrencia_nao_programada
FROM MV_INTERRUPCOES_ANEEL;
```

### 6.2 Recuperação de Dados Históricos

Para o parâmetro `dthRecuperacao`, o Sistema Técnico deve manter histórico de:
- **Mínimo:** 7 dias
- **Recomendado:** 36 meses

```sql
-- Consulta histórica
SELECT *
FROM SYN_HISTORICO_INTERRUPCOES
WHERE data_hora_inicio <= :data_hora_recuperacao
  AND (data_hora_fim IS NULL OR data_hora_fim >= :data_hora_recuperacao);
```

---

## 7. Dados para Portal Público (REN 1.137)

### 7.1 Requisitos do Art. 106-107

| Requisito | Campo Sistema Técnico | Obrigatório |
|-----------|----------------------|-------------|
| Mapa georreferenciado | latitude, longitude | Sim |
| Quantidade de UCs por faixa | qtd_ucs_afetadas + data_hora_inicio | Sim |
| Status da ocorrência | status_ocorrencia | Sim |
| CHI | qtd_ucs_afetadas × duração | Sim |
| Quantidade de equipes | qtd_equipes_designadas | Sim |
| Atualização a cada 30 min | data_atualizacao | Sim |

### 7.2 Faixas de Duração

O Sistema Técnico deve permitir o cálculo das faixas:

| Faixa | Condição |
|-------|----------|
| < 1 hora | duração_horas < 1 |
| 1 a 3 horas | duração_horas >= 1 AND < 3 |
| 3 a 6 horas | duração_horas >= 3 AND < 6 |
| 6 a 12 horas | duração_horas >= 6 AND < 12 |
| 12 a 24 horas | duração_horas >= 12 AND < 24 |
| 24 a 48 horas | duração_horas >= 24 AND < 48 |
| > 48 horas | duração_horas >= 48 |

### 7.3 Status de Ocorrência

O Sistema Técnico deve fornecer os seguintes status:

| Status Sistema Técnico | Exibição Portal |
|-----------------------|-----------------|
| EM_PREPARACAO | Em preparação |
| DESLOCAMENTO | Deslocamento |
| EM_EXECUCAO | Em execução |
| CONCLUIDA | (não exibir) |

---

## 8. Dados para Notificações SMS/WhatsApp

### 8.1 Requisitos do Art. 105

Para notificação de consumidores, o Sistema Técnico deve fornecer:

| Dado | Campo | Prazo para Disponibilização |
|------|-------|---------------------------|
| UCs afetadas | id_uc (lista) | Imediato após detecção |
| Causa | descricao_causa, causa_conhecida | 15 min (se conhecida) |
| Previsão | previsao_restabelecimento | 15 min / 1h |
| Localização | municipio, bairro | Imediato |

### 8.2 Consulta para Notificações

```sql
-- Consulta para disparo de notificações (Oracle)
SELECT
    i.id_interrupcao,
    i.municipio_ibge,
    i.bairro,
    i.descricao_causa,
    i.causa_conhecida,
    i.previsao_restabelecimento,
    LISTAGG(u.id_uc, ',') WITHIN GROUP (ORDER BY u.id_uc) AS ucs_afetadas
FROM SYN_INTERRUPCOES_ATIVAS i
JOIN SYN_UCS_INTERRUPCAO u ON i.id_interrupcao = u.id_interrupcao
WHERE i.data_hora_inicio >= SYSDATE - INTERVAL '15' MINUTE
  AND i.data_hora_fim IS NULL
GROUP BY i.id_interrupcao, i.municipio_ibge, i.bairro,
         i.descricao_causa, i.causa_conhecida, i.previsao_restabelecimento;
```

### 8.3 Dados do Ajuri para Contatos

```sql
-- View esperada no Sistema Ajuri: VW_CONTATOS_RADAR
-- Acessível via: SELECT * FROM SYN_CONTATOS_CONSUMIDORES;

-- Estrutura esperada:
-- id_uc               VARCHAR2(20) PRIMARY KEY
-- telefone_celular    VARCHAR2(20)
-- telefone_whatsapp   VARCHAR2(20)
-- aceita_sms          NUMBER(1) DEFAULT 1  -- 1=sim, 0=não
-- aceita_whatsapp     NUMBER(1) DEFAULT 1  -- 1=sim, 0=não
-- opt_out             NUMBER(1) DEFAULT 0  -- 1=opt-out, 0=ativo
-- data_atualizacao    TIMESTAMP
```

---

## 9. Dados para Indicador DISE

### 9.1 Responsabilidade do Sistema Técnico

O **Sistema Técnico é responsável pelo cálculo do DISE**. O RADAR apenas consome o indicador já calculado.

### 9.2 Regras de Cálculo (a serem implementadas no Sistema Técnico)

```
DISE = Σ (tempo_interrupcao_durante_emergencia) para cada UC

Onde:
- tempo_interrupcao = data_fim_interrupcao - data_inicio_interrupcao
- Se ainda interrompida: tempo_interrupcao = NOW() - data_inicio_interrupcao
- Considerar apenas o período dentro da emergência declarada

Limites:
- Urbano: 24 horas
- Rural: 48 horas

em_violacao = DISE > limite
```

### 9.3 Campos Obrigatórios do DISE

| Campo | Tipo | Descrição | Obrigatório |
|-------|------|-----------|-------------|
| id_emergencia | VARCHAR | ID da situação de emergência | Sim |
| emergencia_ativa | BOOLEAN | Se a emergência está ativa | Sim |
| id_uc | VARCHAR | Código da UC | Sim |
| tipo_area | VARCHAR | 'URBANO' ou 'RURAL' | Sim |
| dise_horas | DECIMAL | DISE calculado em horas | Sim |
| limite_horas | INTEGER | 24 ou 48 | Sim |
| em_violacao | BOOLEAN | Se está em violação | Sim |
| data_calculo | TIMESTAMP | Data/hora do cálculo | Sim |

### 9.4 Exemplo de Cálculo no Sistema Técnico

```sql
-- Exemplo de view para cálculo do DISE no Sistema Técnico
CREATE OR REPLACE VIEW VW_DISE_RADAR AS
SELECT
    seq_dise.NEXTVAL AS id_registro,
    e.id_emergencia,
    e.descricao AS descricao_emergencia,
    e.tipo_evento,
    e.data_inicio AS data_inicio_emergencia,
    e.data_fim AS data_fim_emergencia,
    e.ativa AS emergencia_ativa,
    ui.id_uc,
    uc.municipio_ibge,
    uc.tipo_area,
    i.id_interrupcao,
    i.data_inicio AS data_inicio_interrupcao,
    i.data_fim AS data_fim_interrupcao,

    -- Cálculo do DISE em minutos
    ROUND(
        (COALESCE(i.data_fim, SYSDATE) - i.data_inicio) * 24 * 60
    ) AS dise_minutos,

    -- Cálculo do DISE em horas
    ROUND(
        (COALESCE(i.data_fim, SYSDATE) - i.data_inicio) * 24,
        2
    ) AS dise_horas,

    -- Limite conforme tipo de área
    CASE uc.tipo_area
        WHEN 'URBANO' THEN 24
        WHEN 'RURAL' THEN 48
    END AS limite_horas,

    -- Verificação de violação
    CASE
        WHEN ROUND((COALESCE(i.data_fim, SYSDATE) - i.data_inicio) * 24, 2) >
             CASE uc.tipo_area WHEN 'URBANO' THEN 24 WHEN 'RURAL' THEN 48 END
        THEN 1
        ELSE 0
    END AS em_violacao,

    -- Percentual do limite
    ROUND(
        (ROUND((COALESCE(i.data_fim, SYSDATE) - i.data_inicio) * 24, 2) /
         CASE uc.tipo_area WHEN 'URBANO' THEN 24 WHEN 'RURAL' THEN 48 END) * 100,
        2
    ) AS percentual_limite,

    e.decreto_estadual,
    e.decreto_municipal,
    SYSDATE AS data_calculo,
    SYSDATE AS data_atualizacao

FROM SITUACAO_EMERGENCIA e
JOIN INTERRUPCAO i ON i.data_inicio BETWEEN e.data_inicio AND COALESCE(e.data_fim, SYSDATE + 365)
JOIN UC_INTERRUPCAO ui ON ui.id_interrupcao = i.id_interrupcao
JOIN UNIDADE_CONSUMIDORA uc ON uc.id_uc = ui.id_uc
WHERE e.ativa = 1  -- Apenas emergências ativas ou para relatório
;
```

---

## 10. Mapeamento de Códigos

### 10.1 Códigos IBGE dos Municípios de Roraima

```sql
-- Tabela de referência local (Oracle)
CREATE TABLE MUNICIPIO (
    id              NUMBER(10) PRIMARY KEY,  -- Código IBGE
    nome            VARCHAR2(100) NOT NULL,
    latitude        NUMBER(10,7),
    longitude       NUMBER(10,7),
    populacao       NUMBER(10)
);

INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400050, 'Boa Vista', 2.8235, -60.6758);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400100, 'Alto Alegre', 2.9889, -61.3114);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400027, 'Amajari', 3.6481, -61.3656);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400159, 'Bonfim', 3.3614, -59.8331);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400175, 'Cantá', 2.6097, -60.5986);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400209, 'Caracaraí', 1.8267, -61.1278);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400233, 'Caroebe', 0.8842, -59.6958);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400282, 'Iracema', 2.1831, -61.0450);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400308, 'Mucajaí', 2.4336, -60.9125);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400407, 'Normandia', 3.8797, -59.6225);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400456, 'Pacaraima', 4.4797, -61.1478);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400472, 'Rorainópolis', 0.9419, -60.4394);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400506, 'São João da Baliza', 1.0256, -59.9089);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400605, 'São Luiz', 1.0131, -60.0392);
INSERT INTO MUNICIPIO (id, nome, latitude, longitude) VALUES (1400704, 'Uiramutã', 4.5972, -60.1844);
COMMIT;
```

### 10.2 Mapeamento de Status

```sql
-- Tabela de mapeamento de status (Oracle)
CREATE TABLE MAPEAMENTO_STATUS (
    codigo_sistema_tecnico  VARCHAR2(50) PRIMARY KEY,
    descricao_radar         VARCHAR2(100),
    exibir_portal           NUMBER(1) DEFAULT 1
);

INSERT INTO MAPEAMENTO_STATUS VALUES ('EM_PREPARACAO', 'Em preparação', 1);
INSERT INTO MAPEAMENTO_STATUS VALUES ('DESLOCAMENTO', 'Deslocamento', 1);
INSERT INTO MAPEAMENTO_STATUS VALUES ('EM_EXECUCAO', 'Em execução', 1);
INSERT INTO MAPEAMENTO_STATUS VALUES ('CONCLUIDA', 'Concluída', 0);
INSERT INTO MAPEAMENTO_STATUS VALUES ('CANCELADA', 'Cancelada', 0);
COMMIT;
```

### 10.3 Mapeamento de Causas

```sql
-- Tabela de mapeamento de causas (Oracle)
CREATE TABLE MAPEAMENTO_CAUSAS (
    id_causa_sistema_tecnico    NUMBER(10) PRIMARY KEY,
    descricao_padrao           VARCHAR2(200),
    categoria                   VARCHAR2(50)
);

-- Exemplos de causas comuns
INSERT INTO MAPEAMENTO_CAUSAS VALUES (1, 'Árvore sobre a rede', 'VEGETACAO');
INSERT INTO MAPEAMENTO_CAUSAS VALUES (2, 'Descarga atmosférica', 'CLIMATICO');
INSERT INTO MAPEAMENTO_CAUSAS VALUES (3, 'Defeito em equipamento', 'EQUIPAMENTO');
INSERT INTO MAPEAMENTO_CAUSAS VALUES (4, 'Manutenção programada', 'PROGRAMADA');
INSERT INTO MAPEAMENTO_CAUSAS VALUES (5, 'Acidente de terceiros', 'EXTERNO');
INSERT INTO MAPEAMENTO_CAUSAS VALUES (6, 'Causa em investigação', 'DESCONHECIDA');
COMMIT;
```

---

## 11. Frequência de Atualização

### 11.1 Tabela de Frequências

| Componente | Frequência | Justificativa |
|------------|------------|---------------|
| Interrupções Ativas | Tempo real (trigger) | Crítico para operação |
| Portal Público | 30 minutos | Art. 107 REN 1.137 |
| API ANEEL | 5 minutos | Cache recomendado |
| DISE | 30 minutos | Durante emergência |
| Equipes em Campo | 5 minutos | Localização |
| Histórico | 1 hora | Não crítico |

### 11.2 Implementação com Celery (Python)

```python
# tasks.py
from celery import Celery
from celery.schedules import crontab

app = Celery('radar')

# Configuração de schedule
app.conf.beat_schedule = {
    'refresh-portal-30min': {
        'task': 'tasks.refresh_portal_publico',
        'schedule': crontab(minute='*/30'),  # A cada 30 minutos
    },
    'refresh-api-aneel-5min': {
        'task': 'tasks.refresh_api_aneel',
        'schedule': crontab(minute='*/5'),  # A cada 5 minutos
    },
    'refresh-equipes-5min': {
        'task': 'tasks.refresh_equipes_campo',
        'schedule': crontab(minute='*/5'),
    },
    'refresh-dise-30min': {
        'task': 'tasks.refresh_dise',
        'schedule': crontab(minute='*/30'),
    },
}

@app.task
def refresh_portal_publico():
    """Refresh da view materializada do portal público"""
    from app.database import engine
    with engine.connect() as conn:
        conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY radar.mv_portal_publico")
        conn.commit()

@app.task
def refresh_api_aneel():
    """Refresh da view materializada da API ANEEL"""
    from app.database import engine
    with engine.connect() as conn:
        conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY radar.mv_interrupcoes_aneel")
        conn.commit()
```

---

## 12. Tratamento de Erros

### 12.1 Cenários de Falha

| Cenário | Tratamento | Fallback |
|---------|------------|----------|
| DBLink indisponível | Retry 3x com backoff | Usar último cache válido |
| Dados inconsistentes | Log + alerta | Não processar registro |
| Timeout de consulta | Timeout 30s + retry | Cache anterior |
| Schema alterado | Validação na inicialização | Alerta para TI |

### 12.2 Tabela de Log de Erros

```sql
-- Tabela de log de integração (Oracle)
CREATE TABLE LOG_INTEGRACAO (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_hora       TIMESTAMP DEFAULT SYSTIMESTAMP,
    origem          VARCHAR2(50) NOT NULL,  -- 'SISTEMA_TECNICO', 'AJURI'
    operacao        VARCHAR2(100),
    status          VARCHAR2(20),  -- 'SUCCESS', 'ERROR', 'WARNING'
    mensagem        VARCHAR2(4000),
    detalhes        CLOB,  -- JSON como CLOB
    tempo_execucao  NUMBER(10)  -- em milissegundos
);

CREATE INDEX IDX_LOG_INT_DATA ON LOG_INTEGRACAO (data_hora DESC);
CREATE INDEX IDX_LOG_INT_STATUS ON LOG_INTEGRACAO (status);
```

### 12.3 Health Check dos DBLinks (Oracle)

```sql
-- Procedure de health check para DBLinks
CREATE OR REPLACE PROCEDURE CHECK_DBLINKS_HEALTH AS
    v_start_time TIMESTAMP;
    v_end_time TIMESTAMP;
    v_latency NUMBER;
    v_dummy NUMBER;
    v_error_msg VARCHAR2(4000);
BEGIN
    -- Check Sistema Técnico
    v_start_time := SYSTIMESTAMP;
    BEGIN
        SELECT 1 INTO v_dummy FROM DUAL@SISTEC_LINK WHERE ROWNUM = 1;
        v_end_time := SYSTIMESTAMP;
        v_latency := EXTRACT(SECOND FROM (v_end_time - v_start_time)) * 1000;

        INSERT INTO LOG_INTEGRACAO (origem, operacao, status, mensagem, tempo_execucao)
        VALUES ('SISTEMA_TECNICO', 'HEALTH_CHECK', 'SUCCESS', 'DBLink OK', v_latency);
    EXCEPTION WHEN OTHERS THEN
        v_error_msg := SQLERRM;
        INSERT INTO LOG_INTEGRACAO (origem, operacao, status, mensagem)
        VALUES ('SISTEMA_TECNICO', 'HEALTH_CHECK', 'ERROR', v_error_msg);
    END;

    -- Check Ajuri
    v_start_time := SYSTIMESTAMP;
    BEGIN
        SELECT 1 INTO v_dummy FROM DUAL@AJURI_LINK WHERE ROWNUM = 1;
        v_end_time := SYSTIMESTAMP;
        v_latency := EXTRACT(SECOND FROM (v_end_time - v_start_time)) * 1000;

        INSERT INTO LOG_INTEGRACAO (origem, operacao, status, mensagem, tempo_execucao)
        VALUES ('AJURI', 'HEALTH_CHECK', 'SUCCESS', 'DBLink OK', v_latency);
    EXCEPTION WHEN OTHERS THEN
        v_error_msg := SQLERRM;
        INSERT INTO LOG_INTEGRACAO (origem, operacao, status, mensagem)
        VALUES ('AJURI', 'HEALTH_CHECK', 'ERROR', v_error_msg);
    END;

    COMMIT;
END;
/

-- View para consultar status dos DBLinks
CREATE OR REPLACE VIEW VW_DBLINKS_STATUS AS
SELECT
    origem AS server_name,
    status,
    mensagem,
    tempo_execucao AS latency_ms,
    data_hora AS last_check
FROM LOG_INTEGRACAO
WHERE operacao = 'HEALTH_CHECK'
  AND data_hora = (
      SELECT MAX(data_hora)
      FROM LOG_INTEGRACAO li2
      WHERE li2.origem = LOG_INTEGRACAO.origem
        AND li2.operacao = 'HEALTH_CHECK'
  );
```

---

## 13. Segurança e Permissões

### 13.1 Usuário da Aplicação no Banco RADAR

```sql
-- Criar usuário para aplicação FastAPI (no banco RADAR Oracle)
CREATE USER RADAR_APP IDENTIFIED BY "senha_forte_aqui"
    DEFAULT TABLESPACE USERS
    QUOTA UNLIMITED ON USERS;

-- Permissões de sessão
GRANT CREATE SESSION TO RADAR_APP;

-- Permissões nos synonyms (leitura via DBLink)
GRANT SELECT ON SYN_INTERRUPCOES_ATIVAS TO RADAR_APP;
GRANT SELECT ON SYN_ALIMENTADORES TO RADAR_APP;
GRANT SELECT ON SYN_CONJUNTOS_ELETRICOS TO RADAR_APP;
GRANT SELECT ON SYN_EQUIPES_CAMPO TO RADAR_APP;
GRANT SELECT ON SYN_DISE TO RADAR_APP;
GRANT SELECT ON SYN_UCS_INTERRUPCAO TO RADAR_APP;
GRANT SELECT ON SYN_HISTORICO_INTERRUPCOES TO RADAR_APP;
GRANT SELECT ON SYN_CONTATOS_CONSUMIDORES TO RADAR_APP;

-- Permissões nas Materialized Views
GRANT SELECT ON MV_INTERRUPCOES_ANEEL TO RADAR_APP;
GRANT SELECT ON MV_PORTAL_PUBLICO TO RADAR_APP;
GRANT SELECT ON MV_EQUIPES_STATUS TO RADAR_APP;
GRANT SELECT ON MV_DISE_CONSOLIDADO TO RADAR_APP;

-- Permissões nas tabelas locais
GRANT SELECT, INSERT, UPDATE, DELETE ON MUNICIPIO TO RADAR_APP;
GRANT SELECT, INSERT, UPDATE, DELETE ON MAPEAMENTO_STATUS TO RADAR_APP;
GRANT SELECT, INSERT, UPDATE, DELETE ON MAPEAMENTO_CAUSAS TO RADAR_APP;
GRANT SELECT, INSERT, UPDATE, DELETE ON LOG_INTEGRACAO TO RADAR_APP;
GRANT SELECT, INSERT, UPDATE, DELETE ON LOG_REFRESH TO RADAR_APP;

-- Permissão para executar procedures
GRANT EXECUTE ON REFRESH_ALL_MVIEWS TO RADAR_APP;
GRANT EXECUTE ON CHECK_DBLINKS_HEALTH TO RADAR_APP;
```

### 13.2 Usuário no Sistema Técnico (SOMENTE LEITURA)

O Sistema Técnico deve criar um usuário com permissões **SOMENTE LEITURA**:

```sql
-- Criar usuário no Sistema Técnico Oracle
CREATE USER RADAR_READONLY IDENTIFIED BY "senha_forte"
    DEFAULT TABLESPACE USERS;

GRANT CREATE SESSION TO RADAR_READONLY;

-- Permissões de SELECT nas views do RADAR
GRANT SELECT ON OPERACAO.VW_INTERRUPCOES_ATIVAS_RADAR TO RADAR_READONLY;
GRANT SELECT ON OPERACAO.VW_EQUIPES_CAMPO_RADAR TO RADAR_READONLY;
GRANT SELECT ON OPERACAO.VW_UCS_INTERRUPCAO_RADAR TO RADAR_READONLY;
GRANT SELECT ON CADASTRO.VW_ALIMENTADORES_RADAR TO RADAR_READONLY;
GRANT SELECT ON CADASTRO.VW_CONJUNTOS_RADAR TO RADAR_READONLY;
GRANT SELECT ON INDICADORES.VW_DISE_RADAR TO RADAR_READONLY;
GRANT SELECT ON HISTORICO.VW_HISTORICO_INTERRUPCOES_RADAR TO RADAR_READONLY;
```

### 13.3 Usuário no Sistema Ajuri (SOMENTE LEITURA)

```sql
-- Criar usuário no Sistema Ajuri Oracle
CREATE USER RADAR_READONLY IDENTIFIED BY "senha_forte"
    DEFAULT TABLESPACE USERS;

GRANT CREATE SESSION TO RADAR_READONLY;

-- Permissões de SELECT nas views do RADAR
GRANT SELECT ON COMERCIAL.VW_CONTATOS_RADAR TO RADAR_READONLY;
GRANT SELECT ON COMERCIAL.VW_UNIDADES_CONSUMIDORAS TO RADAR_READONLY;
```

### 13.4 Requisitos de Rede

| Origem | Destino | Porta | Protocolo |
|--------|---------|-------|-----------|
| Servidor RADAR Oracle | Sistema Técnico Oracle | 1521 | TCP |
| Servidor RADAR Oracle | Sistema Ajuri Oracle | 1521 | TCP |

---

## 14. Checklist de Implementação

### 14.1 Responsabilidades do Sistema Técnico

- [ ] **Views/Tabelas obrigatórias:**
  - [ ] VW_INTERRUPCOES_ATIVAS_RADAR
  - [ ] VW_ALIMENTADORES_RADAR
  - [ ] VW_CONJUNTOS_RADAR
  - [ ] VW_EQUIPES_CAMPO_RADAR
  - [ ] VW_DISE_RADAR
  - [ ] VW_UCS_INTERRUPCAO_RADAR
  - [ ] VW_HISTORICO_INTERRUPCOES_RADAR

- [ ] **Campos obrigatórios:**
  - [ ] Todos os campos marcados como NOT NULL nas estruturas
  - [ ] Código IBGE do município (não código interno)
  - [ ] Coordenadas (latitude/longitude) para mapa
  - [ ] Status da ocorrência conforme Art. 107

- [ ] **DISE:**
  - [ ] Implementar cálculo do DISE
  - [ ] Classificação urbano/rural
  - [ ] Verificação de violação de limite
  - [ ] Associação com situação de emergência

- [ ] **Usuário de integração:**
  - [ ] Criar usuário RADAR_READONLY
  - [ ] Conceder permissões de SELECT nas views

- [ ] **Performance:**
  - [ ] Criar índices adequados nas views
  - [ ] Garantir tempo de resposta < 5 segundos

### 14.2 Responsabilidades do RADAR

- [ ] **Configuração Oracle:**
  - [ ] Configurar tnsnames.ora
  - [ ] Criar Database Links (SISTEC_LINK, AJURI_LINK)
  - [ ] Criar Synonyms para tabelas remotas
  - [ ] Testar conectividade dos DBLinks

- [ ] **Materialized Views:**
  - [ ] Criar todas as MVs (MV_INTERRUPCOES_ANEEL, MV_PORTAL_PUBLICO, etc.)
  - [ ] Criar procedure REFRESH_ALL_MVIEWS
  - [ ] Configurar Celery para refresh automático
  - [ ] Criar índices

- [ ] **Monitoramento:**
  - [ ] Criar procedure CHECK_DBLINKS_HEALTH
  - [ ] Configurar alertas
  - [ ] Criar tabela LOG_INTEGRACAO

### 14.3 Testes de Integração

- [ ] Conectividade DBLink Sistema Técnico
- [ ] Conectividade DBLink Ajuri
- [ ] Consulta de interrupções ativas
- [ ] Consulta de DISE
- [ ] Refresh das views materializadas
- [ ] Tempo de resposta < 5 segundos
- [ ] Fallback em caso de falha

---

## Anexos

### A. Diagrama ER do Sistema Técnico (Esperado)

```
┌─────────────────────┐       ┌─────────────────────┐
│    INTERRUPCAO      │       │   ALIMENTADOR       │
├─────────────────────┤       ├─────────────────────┤
│ id_interrupcao (PK) │       │ id_alimentador (PK) │
│ tipo                │       │ nome                │
│ id_alimentador (FK) │──────▶│ id_subestacao       │
│ data_inicio         │       │ qtd_ucs_total       │
│ data_fim            │       └─────────────────────┘
│ status              │
│ causa               │       ┌─────────────────────┐
│ qtd_ucs_afetadas    │       │   UC_INTERRUPCAO    │
└──────────┬──────────┘       ├─────────────────────┤
           │                  │ id_interrupcao (FK) │
           └─────────────────▶│ id_uc (FK)          │
                              │ data_inicio         │
                              │ data_fim            │
┌─────────────────────┐       └──────────┬──────────┘
│ SITUACAO_EMERGENCIA │                  │
├─────────────────────┤                  │
│ id_emergencia (PK)  │                  ▼
│ descricao           │       ┌─────────────────────┐
│ tipo_evento         │       │ UNIDADE_CONSUMIDORA │
│ data_inicio         │       ├─────────────────────┤
│ data_fim            │       │ id_uc (PK)          │
│ ativa               │       │ municipio_ibge      │
│ decreto_estadual    │       │ tipo_area           │
│ decreto_municipal   │       │ id_alimentador      │
└─────────────────────┘       └─────────────────────┘
```

### B. Contatos

| Função | Nome | Email |
|--------|------|-------|
| Coordenador RADAR | TI Roraima Energia | ti@roraimaenergia.com.br |
| Suporte Sistema Técnico | - | - |
| Suporte Ajuri | - | - |
| ANEEL | Daniel Ribeiro | danielribeiro@aneel.gov.br |

---

**Histórico de Revisões**

| Versão | Data | Autor | Alterações |
|--------|------|-------|------------|
| 1.0 | 10/12/2025 | TI | Versão inicial |
| 2.0 | 10/12/2025 | TI | **Padronização Oracle**: Todos os bancos (RADAR, Sistema Técnico, Ajuri) são Oracle. Removido PostgreSQL e FDW. Implementação com Database Links nativos Oracle, Synonyms e Materialized Views Oracle. Scripts SQL atualizados para sintaxe Oracle. |

---

*Documento gerado em 10/12/2025 para o Projeto RADAR - Roraima Energia S/A*
