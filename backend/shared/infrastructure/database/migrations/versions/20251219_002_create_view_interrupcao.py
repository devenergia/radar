"""Create view VW_INTERRUPCAO_FORNECIMENTO

Revision ID: 002
Revises: 001
Create Date: 2025-12-19

Cria a view VW_INTERRUPCAO_FORNECIMENTO que agrega dados de interrupcoes
de fornecimento por municipio e conjunto eletrico.

Fonte: Adaptado de APIANEEL.VW_INTERRUPCAOFORNECIMENTO (radar-backend)

Dependencias:
- DBLink: DBLINK_INSERVICE (acesso ao schema INSERVICE)
- Tabelas remotas: AGENCY_EVENT, SWITCH_PLAN_TASKS, OMS_CONNECTIVITY, CISPERSL
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Schema padrao do RADAR
SCHEMA = "RADAR_API"

# DDL da View
VIEW_DDL = f"""
CREATE OR REPLACE VIEW {SCHEMA}.VW_INTERRUPCAO_FORNECIMENTO (
    IDE_CONJUNTO_UC,
    IDE_MUNICIPIO,
    QTD_UCS_ATENDIDAS,
    QTD_OCORRENCIA_PROGRAMADA,
    QTD_OCORRENCIA_NAO_PROGRAMADA
) AS
WITH

-- CTE 1: Tasks Programadas
Tasks_Programadas AS (
    SELECT DISTINCT
        spt.OUTAGE_NUM
    FROM
        INSERVICE.SWITCH_PLAN_TASKS@DBLINK_INSERVICE spt
    WHERE
        spt.OUTAGE_NUM IS NOT NULL
),

-- CTE 2: Mapeamento Dispositivo -> Municipio
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
        oc.DIST = '370'
        AND c.XFMR IS NOT NULL
        AND c.HXGN_COD_MUNICIPIO_IBGE IS NOT NULL
),

-- CTE 3: UCs Atendidas por Conjunto/Municipio
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

-- CTE 4: Ocorrencias de Interrupcao
Ocorrencias AS (
    SELECT
        Mapa.Conjunto,
        Mapa.IdeMunicipio,
        SUM(
            CASE
                WHEN T.OUTAGE_NUM IS NULL THEN ae.NUM_CUST
                ELSE 0
            END
        ) AS QtdOcorrenciaNaoProgramada,
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
        ae.AG_ID = 370
        AND ae.IS_OPEN = 'T'
        AND ae.HXGN_DT_ORACLE IS NOT NULL
        AND ae.TYCOD <> 'UC_NOXFMR'
        AND NVL(ae.DEV_ID, 0) > 0
    GROUP BY
        Mapa.Conjunto,
        Mapa.IdeMunicipio
)

-- SELECT Principal
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
    NVL(Ocs.QtdOcorrenciaProgramada, 0) > 0
    OR NVL(Ocs.QtdOcorrenciaNaoProgramada, 0) > 0
ORDER BY
    IDE_CONJUNTO_UC,
    IDE_MUNICIPIO
"""


def upgrade() -> None:
    """Aplica a migracao - cria view de interrupcoes."""
    op.execute(VIEW_DDL)

    # Comentarios na view
    op.execute(
        f"""
        COMMENT ON TABLE {SCHEMA}.VW_INTERRUPCAO_FORNECIMENTO IS
        'View de agregacao de interrupcoes de fornecimento para API ANEEL'
        """
    )


def downgrade() -> None:
    """Reverte a migracao - remove view."""
    op.execute(f"DROP VIEW {SCHEMA}.VW_INTERRUPCAO_FORNECIMENTO")
