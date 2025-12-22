"""Oracle Repository Implementation for Interrupcoes.

PADRAO: Usa Session SINCRONA do SQLAlchemy (endpoints sync).
Este e o padrao recomendado para Oracle no projeto de referencia (MJQEE-GFUZ).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.shared.domain.entities.interrupcao import Interrupcao
from backend.shared.domain.value_objects.codigo_ibge import CodigoIBGE
from backend.shared.domain.value_objects.tipo_interrupcao import TipoInterrupcao
from backend.shared.infrastructure.logger import get_logger

if TYPE_CHECKING:
    from backend.shared.domain.repositories.interrupcao_repository import (
        InterrupcaoRepository as InterrupcaoRepositoryProtocol,
    )

logger = get_logger(__name__)


class OracleInterrupcaoRepository:
    """
    Implementacao Oracle do InterrupcaoRepository.

    Busca dados de interrupcoes ativas via DBLinks usando
    Session SINCRONA do SQLAlchemy (padrao do projeto de referencia).

    Attributes:
        _session: Session SQLAlchemy (sincrona)
    """

    # Constantes da agencia Roraima Energia
    AG_ID_RORAIMA = 370
    DIST_RORAIMA = 370

    # Query base para interrupcoes
    _BASE_QUERY = """
        SELECT
            ae.num_1 AS id,
            ae.NUM_CUST AS ucs_afetadas,
            spt.PLAN_ID AS plan_id,
            oc.conj AS conjunto,
            iu.CD_UNIVERSO AS codigo_ibge,
            ae.DT_ON AS data_inicio,
            ae.DT_OFF AS data_fim
        FROM INSERVICE.AGENCY_EVENT@DBLINK_INSERVICE ae
        LEFT JOIN INSERVICE.SWITCH_PLAN_TASKS@DBLINK_INSERVICE spt
            ON spt.OUTAGE_NUM = ae.num_1
        INNER JOIN INSERVICE.OMS_CONNECTIVITY@DBLINK_INSERVICE oc
            ON oc.mslink = ae.dev_id
            AND oc.dist = :dist
        INNER JOIN INDICADORES.IND_UNIVERSOS@DBLINK_INDICADORES iu
            ON iu.ID_DISPOSITIVO = ae.dev_id
            AND iu.CD_TIPO_UNIVERSO = 2
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa repositorio com sessao sincrona.

        Args:
            session: Session SQLAlchemy (sincrona)
        """
        self._session = session

    def buscar_ativas(self) -> list[Interrupcao]:
        """
        Busca todas as interrupcoes ativas (is_open = 'T').

        Returns:
            Lista de entidades Interrupcao
        """
        query = text(f"""
            {self._BASE_QUERY}
            WHERE ae.is_open = 'T'
                AND ae.ag_id = :ag_id
        """)

        logger.info("buscando_interrupcoes_ativas", ag_id=self.AG_ID_RORAIMA)

        result = self._session.execute(
            query,
            {"ag_id": self.AG_ID_RORAIMA, "dist": self.DIST_RORAIMA},
        )
        rows = result.fetchall()

        interrupcoes = self._map_to_entities(rows)
        logger.info("interrupcoes_encontradas", quantidade=len(interrupcoes))

        return interrupcoes

    def buscar_por_municipio(self, codigo_ibge: CodigoIBGE) -> list[Interrupcao]:
        """
        Busca interrupcoes ativas de um municipio especifico.

        Args:
            codigo_ibge: Codigo IBGE do municipio (Value Object)

        Returns:
            Lista de interrupcoes do municipio
        """
        query = text(f"""
            {self._BASE_QUERY}
            WHERE ae.is_open = 'T'
                AND ae.ag_id = :ag_id
                AND iu.CD_UNIVERSO = :ibge
        """)

        logger.info(
            "buscando_interrupcoes_por_municipio",
            municipio=codigo_ibge.valor,
        )

        result = self._session.execute(
            query,
            {
                "ag_id": self.AG_ID_RORAIMA,
                "dist": self.DIST_RORAIMA,
                "ibge": codigo_ibge.valor,
            },
        )
        rows = result.fetchall()

        return self._map_to_entities(rows)

    def buscar_por_conjunto(self, id_conjunto: int) -> list[Interrupcao]:
        """
        Busca interrupcoes ativas de um conjunto eletrico especifico.

        Args:
            id_conjunto: ID do conjunto eletrico

        Returns:
            Lista de interrupcoes do conjunto
        """
        query = text(f"""
            {self._BASE_QUERY}
            WHERE ae.is_open = 'T'
                AND ae.ag_id = :ag_id
                AND oc.conj = :conjunto
        """)

        logger.info(
            "buscando_interrupcoes_por_conjunto",
            conjunto=id_conjunto,
        )

        result = self._session.execute(
            query,
            {
                "ag_id": self.AG_ID_RORAIMA,
                "dist": self.DIST_RORAIMA,
                "conjunto": id_conjunto,
            },
        )
        rows = result.fetchall()

        return self._map_to_entities(rows)

    def buscar_historico(
        self,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> list[Interrupcao]:
        """
        Busca historico de interrupcoes em um periodo.

        Args:
            data_inicio: Data inicial do periodo
            data_fim: Data final do periodo

        Returns:
            Lista de interrupcoes no periodo
        """
        query = text(f"""
            {self._BASE_QUERY}
            WHERE ae.ag_id = :ag_id
                AND ae.DT_ON BETWEEN :dt_inicio AND :dt_fim
        """)

        logger.info(
            "buscando_historico_interrupcoes",
            data_inicio=data_inicio.isoformat(),
            data_fim=data_fim.isoformat(),
        )

        result = self._session.execute(
            query,
            {
                "ag_id": self.AG_ID_RORAIMA,
                "dist": self.DIST_RORAIMA,
                "dt_inicio": data_inicio,
                "dt_fim": data_fim,
            },
        )
        rows = result.fetchall()

        return self._map_to_entities(rows)

    def _map_to_entities(self, rows: list) -> list[Interrupcao]:
        """
        Mapeia rows do banco para entidades de dominio.

        Args:
            rows: Rows do resultado da query

        Returns:
            Lista de entidades Interrupcao

        Note:
            Registros com IBGE invalido sao ignorados (logged).
        """
        entities: list[Interrupcao] = []

        for row in rows:
            # Criar Value Objects
            ibge_result = CodigoIBGE.create(row.codigo_ibge)
            if ibge_result.is_failure:
                logger.warning(
                    "ibge_invalido_ignorado",
                    codigo_ibge=row.codigo_ibge,
                    interrupcao_id=row.id,
                    error=ibge_result.error,
                )
                continue

            tipo = TipoInterrupcao.from_plan_id(row.plan_id)

            # Criar entidade
            interrupcao_result = Interrupcao.create(
                id=row.id,
                tipo=tipo,
                municipio=ibge_result.value,
                conjunto=row.conjunto,
                ucs_afetadas=row.ucs_afetadas or 0,
                data_inicio=row.data_inicio,
                data_fim=row.data_fim,
            )

            if interrupcao_result.is_success:
                entities.append(interrupcao_result.value)
            else:
                logger.warning(
                    "interrupcao_invalida_ignorada",
                    interrupcao_id=row.id,
                    error=interrupcao_result.error,
                )

        return entities
