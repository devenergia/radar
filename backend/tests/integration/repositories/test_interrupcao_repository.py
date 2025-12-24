"""Testes de integracao para InterrupcaoRepository.

Testes que validam o comportamento do repositorio com mock do OraclePool.
Para testes com banco real, configurar as variaveis de ambiente:
- RADAR_DB_TEST_USER
- RADAR_DB_TEST_PASSWORD
- RADAR_DB_TEST_DSN
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.apps.api_interrupcoes.repositories.interrupcao_repository import (
    InterrupcaoAgregadaDB,
    InterrupcaoRepository,
)
from backend.shared.domain.errors import DatabaseQueryError
from backend.shared.infrastructure.database.oracle_pool import OraclePool


@pytest.fixture
def mock_pool() -> MagicMock:
    """Mock do OraclePool para testes de integracao."""
    pool = MagicMock(spec=OraclePool)
    pool.execute = AsyncMock(return_value=[])
    return pool


@pytest.fixture
def repository(mock_pool: MagicMock) -> InterrupcaoRepository:
    """Instancia do repositorio com pool mockado."""
    return InterrupcaoRepository(mock_pool)


@pytest.fixture
def sample_db_row() -> dict[str, Any]:
    """Linha de exemplo retornada pelo banco."""
    return {
        "conjunto": 1,
        "municipio_ibge": 1400100,
        "qtd_ucs_atendidas": 0,
        "qtd_programada": 50,
        "qtd_nao_programada": 30,
    }


@pytest.fixture
def sample_db_rows(sample_db_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Multiplas linhas de exemplo."""
    return [
        sample_db_row,
        {
            "conjunto": 2,
            "municipio_ibge": 1400100,
            "qtd_ucs_atendidas": 0,
            "qtd_programada": 20,
            "qtd_nao_programada": 10,
        },
        {
            "conjunto": 1,
            "municipio_ibge": 1400159,
            "qtd_ucs_atendidas": 0,
            "qtd_programada": 15,
            "qtd_nao_programada": 5,
        },
    ]


@pytest.mark.integration
class TestInterrupcaoRepository:
    """Testes de integracao para InterrupcaoRepository."""

    class TestFindAtivasAgregadas:
        """Testes para find_ativas_agregadas()."""

        @pytest.mark.asyncio
        async def test_deve_retornar_lista_vazia_quando_sem_dados(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
        ) -> None:
            """Quando banco nao tem dados, retorna lista vazia."""
            # Arrange
            mock_pool.execute.return_value = []

            # Act
            result = await repository.find_ativas_agregadas()

            # Assert
            assert result == []
            mock_pool.execute.assert_called_once()

        @pytest.mark.asyncio
        async def test_deve_retornar_lista_de_interrupcoes_agregadas(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
            sample_db_rows: list[dict[str, Any]],
        ) -> None:
            """Retorna lista de InterrupcaoAgregadaDB quando ha dados."""
            # Arrange
            mock_pool.execute.return_value = sample_db_rows

            # Act
            result = await repository.find_ativas_agregadas()

            # Assert
            assert len(result) == 3
            assert all(isinstance(item, InterrupcaoAgregadaDB) for item in result)

        @pytest.mark.asyncio
        async def test_deve_mapear_conjunto_corretamente(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
            sample_db_row: dict[str, Any],
        ) -> None:
            """Campo conjunto mapeado corretamente."""
            # Arrange
            mock_pool.execute.return_value = [sample_db_row]

            # Act
            result = await repository.find_ativas_agregadas()

            # Assert
            assert result[0].conjunto == 1

        @pytest.mark.asyncio
        async def test_deve_mapear_municipio_ibge_corretamente(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
            sample_db_row: dict[str, Any],
        ) -> None:
            """Campo municipio_ibge mapeado corretamente."""
            # Arrange
            mock_pool.execute.return_value = [sample_db_row]

            # Act
            result = await repository.find_ativas_agregadas()

            # Assert
            assert result[0].municipio_ibge == 1400100

        @pytest.mark.asyncio
        async def test_deve_mapear_qtd_programada_corretamente(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
            sample_db_row: dict[str, Any],
        ) -> None:
            """Campo qtd_programada mapeado corretamente."""
            # Arrange
            mock_pool.execute.return_value = [sample_db_row]

            # Act
            result = await repository.find_ativas_agregadas()

            # Assert
            assert result[0].qtd_programada == 50

        @pytest.mark.asyncio
        async def test_deve_mapear_qtd_nao_programada_corretamente(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
            sample_db_row: dict[str, Any],
        ) -> None:
            """Campo qtd_nao_programada mapeado corretamente."""
            # Arrange
            mock_pool.execute.return_value = [sample_db_row]

            # Act
            result = await repository.find_ativas_agregadas()

            # Assert
            assert result[0].qtd_nao_programada == 30

        @pytest.mark.asyncio
        async def test_deve_tratar_valores_nulos_como_zero(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
        ) -> None:
            """Valores nulos devem ser convertidos para zero."""
            # Arrange
            mock_pool.execute.return_value = [
                {
                    "conjunto": 1,
                    "municipio_ibge": 1400100,
                    "qtd_ucs_atendidas": None,
                    "qtd_programada": None,
                    "qtd_nao_programada": None,
                }
            ]

            # Act
            result = await repository.find_ativas_agregadas()

            # Assert
            assert result[0].qtd_ucs_atendidas == 0
            assert result[0].qtd_programada == 0
            assert result[0].qtd_nao_programada == 0

        @pytest.mark.asyncio
        async def test_deve_executar_query_correta(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
        ) -> None:
            """Verifica que a query correta e executada."""
            # Arrange
            mock_pool.execute.return_value = []

            # Act
            await repository.find_ativas_agregadas()

            # Assert
            call_args = mock_pool.execute.call_args
            query = call_args[0][0]
            assert "INSERVICE.AGENCY_EVENT" in query
            assert "is_open = 'T'" in query
            assert "GROUP BY" in query

        @pytest.mark.asyncio
        async def test_deve_propagar_erro_de_query(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
        ) -> None:
            """Erro no banco deve ser propagado."""
            # Arrange
            mock_pool.execute.side_effect = DatabaseQueryError(
                Exception("Connection failed"),
                "SELECT ...",
            )

            # Act & Assert
            with pytest.raises(DatabaseQueryError):
                await repository.find_ativas_agregadas()

    class TestFindAtivasDetalhadas:
        """Testes para find_ativas_detalhadas()."""

        @pytest.mark.asyncio
        async def test_deve_retornar_lista_de_dicionarios(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
        ) -> None:
            """Retorna lista de dicionarios com detalhes."""
            # Arrange
            mock_pool.execute.return_value = [
                {
                    "id": 12345,
                    "ucs_afetadas": 100,
                    "data_inicio": "2025-01-01 10:00:00",
                    "plan_id": None,
                    "conjunto": 1,
                    "municipio_ibge": 1400100,
                }
            ]

            # Act
            result = await repository.find_ativas_detalhadas()

            # Assert
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], dict)

        @pytest.mark.asyncio
        async def test_deve_retornar_lista_vazia_quando_sem_dados(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
        ) -> None:
            """Quando nao ha interrupcoes, retorna lista vazia."""
            # Arrange
            mock_pool.execute.return_value = []

            # Act
            result = await repository.find_ativas_detalhadas()

            # Assert
            assert result == []

        @pytest.mark.asyncio
        async def test_deve_conter_campos_esperados(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
        ) -> None:
            """Resultado deve conter todos os campos esperados."""
            # Arrange
            expected_row = {
                "id": 12345,
                "ucs_afetadas": 100,
                "data_inicio": "2025-01-01 10:00:00",
                "plan_id": 999,
                "conjunto": 1,
                "municipio_ibge": 1400100,
            }
            mock_pool.execute.return_value = [expected_row]

            # Act
            result = await repository.find_ativas_detalhadas()

            # Assert
            assert "id" in result[0]
            assert "ucs_afetadas" in result[0]
            assert "data_inicio" in result[0]
            assert "plan_id" in result[0]
            assert "conjunto" in result[0]
            assert "municipio_ibge" in result[0]

        @pytest.mark.asyncio
        async def test_deve_executar_query_detalhada(
            self,
            repository: InterrupcaoRepository,
            mock_pool: MagicMock,
        ) -> None:
            """Verifica que a query detalhada e executada."""
            # Arrange
            mock_pool.execute.return_value = []

            # Act
            await repository.find_ativas_detalhadas()

            # Assert
            call_args = mock_pool.execute.call_args
            query = call_args[0][0]
            assert "ae.num_1 AS id" in query
            assert "ae.num_cust AS ucs_afetadas" in query
            assert "ae.ad_ts AS data_inicio" in query


@pytest.mark.integration
class TestInterrupcaoAgregadaDB:
    """Testes para a dataclass InterrupcaoAgregadaDB."""

    def test_deve_criar_instancia_com_todos_campos(self) -> None:
        """Cria instancia com todos os campos."""
        # Arrange & Act
        agregada = InterrupcaoAgregadaDB(
            conjunto=1,
            municipio_ibge=1400100,
            qtd_ucs_atendidas=500,
            qtd_programada=50,
            qtd_nao_programada=30,
        )

        # Assert
        assert agregada.conjunto == 1
        assert agregada.municipio_ibge == 1400100
        assert agregada.qtd_ucs_atendidas == 500
        assert agregada.qtd_programada == 50
        assert agregada.qtd_nao_programada == 30

    def test_deve_ser_dataclass(self) -> None:
        """InterrupcaoAgregadaDB deve ser uma dataclass."""
        # Arrange
        from dataclasses import is_dataclass

        # Act & Assert
        assert is_dataclass(InterrupcaoAgregadaDB)

    def test_deve_ser_comparavel_por_valor(self) -> None:
        """Duas instancias com mesmos valores devem ser iguais."""
        # Arrange
        agregada1 = InterrupcaoAgregadaDB(
            conjunto=1,
            municipio_ibge=1400100,
            qtd_ucs_atendidas=0,
            qtd_programada=50,
            qtd_nao_programada=30,
        )
        agregada2 = InterrupcaoAgregadaDB(
            conjunto=1,
            municipio_ibge=1400100,
            qtd_ucs_atendidas=0,
            qtd_programada=50,
            qtd_nao_programada=30,
        )

        # Act & Assert
        assert agregada1 == agregada2

    def test_instancias_diferentes_nao_sao_iguais(self) -> None:
        """Instancias com valores diferentes nao sao iguais."""
        # Arrange
        agregada1 = InterrupcaoAgregadaDB(
            conjunto=1,
            municipio_ibge=1400100,
            qtd_ucs_atendidas=0,
            qtd_programada=50,
            qtd_nao_programada=30,
        )
        agregada2 = InterrupcaoAgregadaDB(
            conjunto=2,  # diferente
            municipio_ibge=1400100,
            qtd_ucs_atendidas=0,
            qtd_programada=50,
            qtd_nao_programada=30,
        )

        # Act & Assert
        assert agregada1 != agregada2


@pytest.mark.integration
class TestRepositorySingleton:
    """Testes para funcoes de dependency injection."""

    @pytest.mark.asyncio
    async def test_get_interrupcao_repository_retorna_instancia(self) -> None:
        """get_interrupcao_repository retorna uma instancia do repositorio."""
        # Arrange
        from backend.apps.api_interrupcoes.repositories.interrupcao_repository import (
            InterrupcaoRepository as LegacyInterrupcaoRepository,
            get_interrupcao_repository,
        )

        # Act
        repo = await get_interrupcao_repository()

        # Assert - Verifica que e uma instancia da classe concreta do mesmo modulo
        assert isinstance(repo, LegacyInterrupcaoRepository)

    @pytest.mark.asyncio
    async def test_get_interrupcao_repository_retorna_mesma_instancia(self) -> None:
        """get_interrupcao_repository retorna singleton."""
        # Arrange
        from backend.apps.api_interrupcoes.repositories.interrupcao_repository import (
            get_interrupcao_repository,
        )

        # Act
        repo1 = await get_interrupcao_repository()
        repo2 = await get_interrupcao_repository()

        # Assert
        assert repo1 is repo2
