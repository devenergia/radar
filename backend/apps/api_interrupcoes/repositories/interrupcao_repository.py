"""Repositorio de Interrupcoes - Acesso ao banco Oracle via DBLink."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from backend.shared.infrastructure.database.oracle_pool import OraclePool, oracle_pool
from backend.shared.infrastructure.logger import get_logger

if TYPE_CHECKING:
    from backend.apps.api_interrupcoes.schemas import InterrupcaoAgregadaItem


@dataclass
class InterrupcaoAgregadaDB:
    """Dados de interrupcao agregada retornados do banco."""

    conjunto: int
    municipio_ibge: int
    qtd_ucs_atendidas: int
    qtd_programada: int
    qtd_nao_programada: int

    def to_aneel_format(self) -> InterrupcaoAgregadaItem:
        """Converte para formato ANEEL."""
        from backend.apps.api_interrupcoes.schemas import InterrupcaoAgregadaItem

        return InterrupcaoAgregadaItem(
            ideConjuntoUnidadeConsumidora=self.conjunto,
            ideMunicipio=self.municipio_ibge,
            qtdUCsAtendidas=self.qtd_ucs_atendidas,
            qtdOcorrenciaProgramada=self.qtd_programada,
            qtdOcorrenciaNaoProgramada=self.qtd_nao_programada,
        )


class InterrupcaoRepository:
    """
    Repositorio para acesso a dados de interrupcoes.

    Utiliza DBLinks para consultar dados do INSERVICE e INDICADORES.
    """

    # Query principal para buscar interrupcoes ativas agregadas
    QUERY_INTERRUPCOES_ATIVAS = """
        SELECT
            oc.conj AS conjunto,
            iu.cd_universo AS municipio_ibge,
            0 AS qtd_ucs_atendidas,
            SUM(CASE WHEN spt.plan_id IS NOT NULL THEN ae.num_cust ELSE 0 END) AS qtd_programada,
            SUM(CASE WHEN spt.plan_id IS NULL THEN ae.num_cust ELSE 0 END) AS qtd_nao_programada
        FROM
            INSERVICE.AGENCY_EVENT@DBLINK_INSERVICE ae
        LEFT JOIN
            INSERVICE.SWITCH_PLAN_TASKS@DBLINK_INSERVICE spt
            ON spt.outage_num = ae.num_1
        INNER JOIN
            INSERVICE.OMS_CONNECTIVITY@DBLINK_INSERVICE oc
            ON oc.mslink = ae.dev_id
            AND oc.dist = 370
        INNER JOIN
            INDICADORES.IND_UNIVERSOS@DBLINK_INDICADORES iu
            ON iu.id_dispositivo = ae.dev_id
            AND iu.cd_tipo_universo = 2
        WHERE
            ae.is_open = 'T'
            AND ae.ag_id = 370
        GROUP BY
            oc.conj,
            iu.cd_universo
        ORDER BY
            iu.cd_universo,
            oc.conj
    """

    def __init__(self, pool: OraclePool) -> None:
        self.pool = pool
        self.logger = get_logger("repository.interrupcao")

    async def find_ativas_agregadas(self) -> list[InterrupcaoAgregadaDB]:
        """
        Busca interrupcoes ativas agregadas por municipio e conjunto.

        Returns:
            Lista de interrupcoes agregadas

        Raises:
            DatabaseQueryError: Se falhar ao executar query
        """
        self.logger.debug("Buscando interrupcoes ativas agregadas")

        rows = await self.pool.execute(self.QUERY_INTERRUPCOES_ATIVAS)

        result = [
            InterrupcaoAgregadaDB(
                conjunto=row["conjunto"],
                municipio_ibge=row["municipio_ibge"],
                qtd_ucs_atendidas=row["qtd_ucs_atendidas"] or 0,
                qtd_programada=row["qtd_programada"] or 0,
                qtd_nao_programada=row["qtd_nao_programada"] or 0,
            )
            for row in rows
        ]

        self.logger.info(
            "Interrupcoes ativas encontradas",
            count=len(result),
        )

        return result

    async def find_ativas_detalhadas(self) -> list[dict[str, Any]]:
        """
        Busca interrupcoes ativas com detalhes individuais.

        Returns:
            Lista de interrupcoes detalhadas
        """
        query = """
            SELECT
                ae.num_1 AS id,
                ae.num_cust AS ucs_afetadas,
                ae.ad_ts AS data_inicio,
                spt.plan_id,
                oc.conj AS conjunto,
                iu.cd_universo AS municipio_ibge
            FROM
                INSERVICE.AGENCY_EVENT@DBLINK_INSERVICE ae
            LEFT JOIN
                INSERVICE.SWITCH_PLAN_TASKS@DBLINK_INSERVICE spt
                ON spt.outage_num = ae.num_1
            INNER JOIN
                INSERVICE.OMS_CONNECTIVITY@DBLINK_INSERVICE oc
                ON oc.mslink = ae.dev_id
                AND oc.dist = 370
            INNER JOIN
                INDICADORES.IND_UNIVERSOS@DBLINK_INDICADORES iu
                ON iu.id_dispositivo = ae.dev_id
                AND iu.cd_tipo_universo = 2
            WHERE
                ae.is_open = 'T'
                AND ae.ag_id = 370
            ORDER BY
                ae.ad_ts DESC
        """

        return await self.pool.execute(query)


# Instancia singleton do repositorio
interrupcao_repository = InterrupcaoRepository(oracle_pool)


async def get_interrupcao_repository() -> InterrupcaoRepository:
    """Dependency injection para FastAPI."""
    return interrupcao_repository
