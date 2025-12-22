-- ============================================================================
-- View: VW_INTERRUPCAO_FORNECIMENTO
-- Schema: RADAR_API
-- Descricao: Agregacao de interrupcoes de fornecimento por municipio e conjunto
-- Fonte: Adaptado de APIANEEL.VW_INTERRUPCAOFORNECIMENTO (radar-backend)
-- Data: 2025-12-19
-- ============================================================================
--
-- DEPENDENCIAS:
--   - DBLink: DBLINK_INSERVICE (acesso ao schema INSERVICE)
--   - Tabelas: INSERVICE.AGENCY_EVENT, INSERVICE.SWITCH_PLAN_TASKS,
--              INSERVICE.OMS_CONNECTIVITY, INSERVICE.CISPERSL
--
-- REGRAS DE NEGOCIO:
--   - Interrupcao PROGRAMADA: Possui registro em SWITCH_PLAN_TASKS (PLAN_ID)
--   - Interrupcao NAO PROGRAMADA: Nao possui registro em SWITCH_PLAN_TASKS
--   - Apenas eventos abertos (is_open = 'T')
--   - Apenas agencia 370 (Roraima Energia)
--   - Exclui eventos sem dispositivo valido
--
-- ============================================================================

CREATE OR REPLACE VIEW RADAR_API.VW_INTERRUPCAO_FORNECIMENTO (
    IDE_CONJUNTO_UC,
    IDE_MUNICIPIO,
    QTD_UCS_ATENDIDAS,
    QTD_OCORRENCIA_PROGRAMADA,
    QTD_OCORRENCIA_NAO_PROGRAMADA
) AS
WITH

-- ============================================================================
-- CTE 1: Tasks Programadas
-- Identifica outages que possuem plano de desligamento (programadas)
-- ============================================================================
Tasks_Programadas AS (
    SELECT DISTINCT
        spt.OUTAGE_NUM
    FROM
        INSERVICE.SWITCH_PLAN_TASKS@DBLINK_INSERVICE spt
    WHERE
        spt.OUTAGE_NUM IS NOT NULL
),

-- ============================================================================
-- CTE 2: Mapeamento Dispositivo -> Municipio
-- Relaciona dispositivos (transformadores) com seus municipios via IBGE
-- ============================================================================
Device_Municipio_Map AS (
    SELECT DISTINCT
        oc.DEV_NAME,
        oc.CONJ AS Conjunto,
        c.HXGN_COD_MUNICIPIO_IBGE AS IdeMunicipio
    FROM
        INSERVICE.CISPERSL@DBLINK_INSERVICE c
        INNER JOIN INSERVICE.OMS_CONNECTIVITY@DBLINK_INSERVICE oc
            ON oc.DEV_NAME = c.XFMR
    WHERE
        oc.DIST = '370'           -- Distribuidora Roraima (370)
        AND c.XFMR IS NOT NULL    -- Apenas UCs com transformador associado
        AND c.HXGN_COD_MUNICIPIO_IBGE IS NOT NULL
),

-- ============================================================================
-- CTE 3: UCs Atendidas por Conjunto/Municipio
-- Contagem total de Unidades Consumidoras por conjunto e municipio
-- ============================================================================
UCs_Atendidas AS (
    SELECT
        oc.CONJ AS Conjunto,
        c.HXGN_COD_MUNICIPIO_IBGE AS IdeMunicipio,
        COUNT(DISTINCT c.PREMISE) AS QtdUCsAtendidas
    FROM
        INSERVICE.CISPERSL@DBLINK_INSERVICE c
        INNER JOIN INSERVICE.OMS_CONNECTIVITY@DBLINK_INSERVICE oc
            ON oc.DEV_NAME = c.XFMR
    WHERE
        oc.DIST = '370'
        AND c.XFMR IS NOT NULL
        AND c.HXGN_COD_MUNICIPIO_IBGE IS NOT NULL
    GROUP BY
        oc.CONJ,
        c.HXGN_COD_MUNICIPIO_IBGE
),

-- ============================================================================
-- CTE 4: Ocorrencias de Interrupcao
-- Agrega interrupcoes ativas por tipo (programada/nao programada)
-- ============================================================================
Ocorrencias AS (
    SELECT
        Mapa.Conjunto,
        Mapa.IdeMunicipio,
        -- Nao Programada: Eventos SEM registro em SWITCH_PLAN_TASKS
        SUM(
            CASE
                WHEN T.OUTAGE_NUM IS NULL THEN ae.NUM_CUST
                ELSE 0
            END
        ) AS QtdOcorrenciaNaoProgramada,
        -- Programada: Eventos COM registro em SWITCH_PLAN_TASKS
        SUM(
            CASE
                WHEN T.OUTAGE_NUM IS NOT NULL THEN ae.NUM_CUST
                ELSE 0
            END
        ) AS QtdOcorrenciaProgramada
    FROM
        INSERVICE.AGENCY_EVENT@DBLINK_INSERVICE ae
        INNER JOIN Device_Municipio_Map Mapa
            ON ae.DEV_NAME = Mapa.DEV_NAME
        LEFT JOIN Tasks_Programadas T
            ON ae.NUM_1 = T.OUTAGE_NUM
    WHERE
        ae.AG_ID = 370                      -- Agencia Roraima
        AND ae.IS_OPEN = 'T'                -- Apenas eventos abertos
        AND ae.HXGN_DT_ORACLE IS NOT NULL   -- Data Oracle preenchida
        AND ae.TYCOD <> 'UC_NOXFMR'         -- Exclui UCs sem transformador
        AND NVL(ae.DEV_ID, 0) > 0           -- Dispositivo valido
    GROUP BY
        Mapa.Conjunto,
        Mapa.IdeMunicipio
)

-- ============================================================================
-- SELECT Principal: Combina UCs Atendidas com Ocorrencias
-- ============================================================================
SELECT
    COALESCE(UCs.Conjunto, Ocs.Conjunto) AS IDE_CONJUNTO_UC,
    COALESCE(UCs.IdeMunicipio, Ocs.IdeMunicipio) AS IDE_MUNICIPIO,
    NVL(UCs.QtdUCsAtendidas, 0) AS QTD_UCS_ATENDIDAS,
    NVL(Ocs.QtdOcorrenciaProgramada, 0) AS QTD_OCORRENCIA_PROGRAMADA,
    NVL(Ocs.QtdOcorrenciaNaoProgramada, 0) AS QTD_OCORRENCIA_NAO_PROGRAMADA
FROM
    UCs_Atendidas UCs
    FULL OUTER JOIN Ocorrencias Ocs
        ON UCs.Conjunto = Ocs.Conjunto
        AND UCs.IdeMunicipio = Ocs.IdeMunicipio
WHERE
    -- Retorna apenas registros com pelo menos uma interrupcao
    NVL(Ocs.QtdOcorrenciaProgramada, 0) > 0
    OR NVL(Ocs.QtdOcorrenciaNaoProgramada, 0) > 0
ORDER BY
    IDE_CONJUNTO_UC,
    IDE_MUNICIPIO;

-- ============================================================================
-- Grants (executar como DBA)
-- ============================================================================
-- GRANT SELECT ON RADAR_API.VW_INTERRUPCAO_FORNECIMENTO TO RADAR_APP;

-- ============================================================================
-- Sinonimo publico (opcional)
-- ============================================================================
-- CREATE OR REPLACE PUBLIC SYNONYM VW_INTERRUPCAO_FORNECIMENTO
--     FOR RADAR_API.VW_INTERRUPCAO_FORNECIMENTO;

-- ============================================================================
-- Comentarios
-- ============================================================================
COMMENT ON TABLE RADAR_API.VW_INTERRUPCAO_FORNECIMENTO IS
    'View de agregacao de interrupcoes de fornecimento para API ANEEL';

COMMENT ON COLUMN RADAR_API.VW_INTERRUPCAO_FORNECIMENTO.IDE_CONJUNTO_UC IS
    'Identificador do conjunto de unidades consumidoras';

COMMENT ON COLUMN RADAR_API.VW_INTERRUPCAO_FORNECIMENTO.IDE_MUNICIPIO IS
    'Codigo IBGE do municipio (7 digitos)';

COMMENT ON COLUMN RADAR_API.VW_INTERRUPCAO_FORNECIMENTO.QTD_UCS_ATENDIDAS IS
    'Quantidade total de UCs atendidas no conjunto/municipio';

COMMENT ON COLUMN RADAR_API.VW_INTERRUPCAO_FORNECIMENTO.QTD_OCORRENCIA_PROGRAMADA IS
    'Quantidade de UCs afetadas por interrupcoes programadas';

COMMENT ON COLUMN RADAR_API.VW_INTERRUPCAO_FORNECIMENTO.QTD_OCORRENCIA_NAO_PROGRAMADA IS
    'Quantidade de UCs afetadas por interrupcoes nao programadas';
