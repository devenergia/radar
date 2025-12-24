"""Testes unitarios para OracleInterrupcaoRepository (Session SINCRONA).

Seguindo TDD (RED phase): Estes testes devem FALHAR inicialmente.
O repositorio usa Session SINCRONA do SQLAlchemy (padrao do projeto de referencia).
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from backend.shared.domain.value_objects.codigo_ibge import CodigoIBGE
from backend.shared.domain.value_objects.tipo_interrupcao import TipoInterrupcao


@pytest.fixture
def mock_session() -> MagicMock:
    """Mock da Session sync do SQLAlchemy."""
    return MagicMock()


@pytest.fixture
def mock_result() -> MagicMock:
    """Mock do resultado da query."""
    result = MagicMock()
    result.fetchall.return_value = []
    return result


@pytest.fixture
def sample_row() -> MagicMock:
    """Linha de exemplo retornada pelo banco."""
    row = MagicMock()
    row.id = 12345
    row.ucs_afetadas = 100
    row.plan_id = None  # Nao programada
    row.conjunto = 1
    row.codigo_ibge = 1400100  # Boa Vista
    row.data_inicio = datetime(2025, 12, 22, 10, 0, 0)
    row.data_fim = None  # Ativa
    return row


@pytest.fixture
def sample_row_programada() -> MagicMock:
    """Linha de exemplo com interrupcao programada."""
    row = MagicMock()
    row.id = 12346
    row.ucs_afetadas = 50
    row.plan_id = 999  # Programada (tem PLAN_ID)
    row.conjunto = 2
    row.codigo_ibge = 1400159  # Bonfim
    row.data_inicio = datetime(2025, 12, 22, 8, 0, 0)
    row.data_fim = None
    return row


@pytest.fixture
def sample_row_invalid_ibge() -> MagicMock:
    """Linha com IBGE invalido (outro estado)."""
    row = MagicMock()
    row.id = 12347
    row.ucs_afetadas = 30
    row.plan_id = None
    row.conjunto = 1
    row.codigo_ibge = 3550308  # Sao Paulo - invalido
    row.data_inicio = datetime(2025, 12, 22, 9, 0, 0)
    row.data_fim = None
    return row


@pytest.mark.unit
class TestOracleInterrupcaoRepository:
    """Testes unitarios para OracleInterrupcaoRepository."""

    @pytest.fixture
    def repository(self, mock_session: MagicMock):
        """Repository com session mockada."""
        from backend.apps.api_interrupcoes.repositories.oracle_interrupcao_repository import (
            OracleInterrupcaoRepository,
        )

        return OracleInterrupcaoRepository(mock_session)

    class TestInit:
        """Testes para inicializacao do repositorio."""

        def test_deve_aceitar_session_sync(self, mock_session: MagicMock) -> None:
            """Repositorio deve aceitar Session sincrona."""
            from backend.apps.api_interrupcoes.repositories.oracle_interrupcao_repository import (
                OracleInterrupcaoRepository,
            )

            repo = OracleInterrupcaoRepository(mock_session)
            assert repo._session is mock_session

        def test_deve_ter_constantes_roraima(self, repository) -> None:
            """Repositorio deve ter constantes AG_ID e DIST de Roraima."""
            assert repository.AG_ID_RORAIMA == 370
            assert repository.DIST_RORAIMA == 370

    class TestBuscarAtivas:
        """Testes para metodo buscar_ativas()."""

        def test_deve_retornar_lista_vazia_sem_dados(
            self,
            repository,
            mock_session: MagicMock,
            mock_result: MagicMock,
        ) -> None:
            """Retorna lista vazia quando nao ha interrupcoes."""
            mock_session.execute.return_value = mock_result

            interrupcoes = repository.buscar_ativas()

            assert interrupcoes == []
            mock_session.execute.assert_called_once()

        def test_deve_usar_ag_id_370(
            self,
            repository,
            mock_session: MagicMock,
            mock_result: MagicMock,
        ) -> None:
            """Query deve usar ag_id 370 (Roraima Energia)."""
            mock_session.execute.return_value = mock_result

            repository.buscar_ativas()

            call_args = mock_session.execute.call_args
            params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]
            assert params.get("ag_id") == 370

        def test_deve_usar_dist_370(
            self,
            repository,
            mock_session: MagicMock,
            mock_result: MagicMock,
        ) -> None:
            """Query deve usar dist 370 (Roraima)."""
            mock_session.execute.return_value = mock_result

            repository.buscar_ativas()

            call_args = mock_session.execute.call_args
            params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]
            assert params.get("dist") == 370

        def test_deve_mapear_row_para_entidade_interrupcao(
            self,
            repository,
            mock_session: MagicMock,
            sample_row: MagicMock,
        ) -> None:
            """Row do banco deve ser mapeada para entidade Interrupcao."""
            from backend.shared.domain.entities.interrupcao import Interrupcao

            mock_result = MagicMock()
            mock_result.fetchall.return_value = [sample_row]
            mock_session.execute.return_value = mock_result

            interrupcoes = repository.buscar_ativas()

            assert len(interrupcoes) == 1
            assert isinstance(interrupcoes[0], Interrupcao)
            assert interrupcoes[0].id == 12345
            assert interrupcoes[0].ucs_afetadas == 100

        def test_deve_classificar_nao_programada_sem_plan_id(
            self,
            repository,
            mock_session: MagicMock,
            sample_row: MagicMock,
        ) -> None:
            """Interrupcao sem PLAN_ID deve ser NAO_PROGRAMADA."""
            mock_result = MagicMock()
            mock_result.fetchall.return_value = [sample_row]
            mock_session.execute.return_value = mock_result

            interrupcoes = repository.buscar_ativas()

            assert interrupcoes[0].is_programada() is False

        def test_deve_classificar_programada_com_plan_id(
            self,
            repository,
            mock_session: MagicMock,
            sample_row_programada: MagicMock,
        ) -> None:
            """Interrupcao com PLAN_ID deve ser PROGRAMADA."""
            mock_result = MagicMock()
            mock_result.fetchall.return_value = [sample_row_programada]
            mock_session.execute.return_value = mock_result

            interrupcoes = repository.buscar_ativas()

            assert interrupcoes[0].is_programada() is True

        def test_deve_ignorar_ibge_invalido(
            self,
            repository,
            mock_session: MagicMock,
            sample_row_invalid_ibge: MagicMock,
        ) -> None:
            """Registros com IBGE invalido devem ser ignorados."""
            mock_result = MagicMock()
            mock_result.fetchall.return_value = [sample_row_invalid_ibge]
            mock_session.execute.return_value = mock_result

            interrupcoes = repository.buscar_ativas()

            assert interrupcoes == []

        def test_deve_tratar_ucs_afetadas_null_como_zero(
            self,
            repository,
            mock_session: MagicMock,
            sample_row: MagicMock,
        ) -> None:
            """UCs afetadas NULL deve ser tratado como 0."""
            sample_row.ucs_afetadas = None
            mock_result = MagicMock()
            mock_result.fetchall.return_value = [sample_row]
            mock_session.execute.return_value = mock_result

            interrupcoes = repository.buscar_ativas()

            assert interrupcoes[0].ucs_afetadas == 0

        def test_deve_mapear_municipio_como_codigo_ibge(
            self,
            repository,
            mock_session: MagicMock,
            sample_row: MagicMock,
        ) -> None:
            """Municipio deve ser mapeado como CodigoIBGE."""
            mock_result = MagicMock()
            mock_result.fetchall.return_value = [sample_row]
            mock_session.execute.return_value = mock_result

            interrupcoes = repository.buscar_ativas()

            assert isinstance(interrupcoes[0].municipio, CodigoIBGE)
            assert interrupcoes[0].municipio.valor == 1400100

        def test_deve_mapear_data_inicio(
            self,
            repository,
            mock_session: MagicMock,
            sample_row: MagicMock,
        ) -> None:
            """Data inicio deve ser mapeada corretamente."""
            mock_result = MagicMock()
            mock_result.fetchall.return_value = [sample_row]
            mock_session.execute.return_value = mock_result

            interrupcoes = repository.buscar_ativas()

            assert interrupcoes[0].data_inicio == datetime(2025, 12, 22, 10, 0, 0)

        def test_deve_ser_metodo_sincrono(self, repository) -> None:
            """buscar_ativas deve ser metodo SINCRONO (nao async)."""
            import inspect

            assert not inspect.iscoroutinefunction(repository.buscar_ativas)

    class TestBuscarPorMunicipio:
        """Testes para metodo buscar_por_municipio()."""

        def test_deve_filtrar_por_codigo_ibge(
            self,
            repository,
            mock_session: MagicMock,
            mock_result: MagicMock,
        ) -> None:
            """Query deve filtrar por codigo IBGE especificado."""
            mock_session.execute.return_value = mock_result
            ibge = CodigoIBGE.create(1400100).value

            repository.buscar_por_municipio(ibge)

            call_args = mock_session.execute.call_args
            params = call_args[0][1]
            assert params.get("ibge") == 1400100

        def test_deve_retornar_lista_de_interrupcoes(
            self,
            repository,
            mock_session: MagicMock,
            sample_row: MagicMock,
        ) -> None:
            """Deve retornar lista de Interrupcoes do municipio."""
            from backend.shared.domain.entities.interrupcao import Interrupcao

            mock_result = MagicMock()
            mock_result.fetchall.return_value = [sample_row]
            mock_session.execute.return_value = mock_result

            ibge = CodigoIBGE.create(1400100).value
            interrupcoes = repository.buscar_por_municipio(ibge)

            assert len(interrupcoes) == 1
            assert isinstance(interrupcoes[0], Interrupcao)

        def test_deve_ser_metodo_sincrono(self, repository) -> None:
            """buscar_por_municipio deve ser metodo SINCRONO."""
            import inspect

            assert not inspect.iscoroutinefunction(repository.buscar_por_municipio)

    class TestBuscarHistorico:
        """Testes para metodo buscar_historico()."""

        def test_deve_filtrar_por_periodo(
            self,
            repository,
            mock_session: MagicMock,
            mock_result: MagicMock,
        ) -> None:
            """Query deve filtrar por periodo especificado."""
            mock_session.execute.return_value = mock_result
            data_inicio = datetime(2025, 1, 1)
            data_fim = datetime(2025, 1, 7)

            repository.buscar_historico(data_inicio, data_fim)

            call_args = mock_session.execute.call_args
            params = call_args[0][1]
            assert params.get("dt_inicio") == data_inicio
            assert params.get("dt_fim") == data_fim

        def test_deve_retornar_lista_de_interrupcoes(
            self,
            repository,
            mock_session: MagicMock,
            sample_row: MagicMock,
        ) -> None:
            """Deve retornar lista de Interrupcoes no periodo."""
            from backend.shared.domain.entities.interrupcao import Interrupcao

            mock_result = MagicMock()
            mock_result.fetchall.return_value = [sample_row]
            mock_session.execute.return_value = mock_result

            interrupcoes = repository.buscar_historico(
                datetime(2025, 1, 1),
                datetime(2025, 1, 7),
            )

            assert len(interrupcoes) == 1
            assert isinstance(interrupcoes[0], Interrupcao)

        def test_deve_ser_metodo_sincrono(self, repository) -> None:
            """buscar_historico deve ser metodo SINCRONO."""
            import inspect

            assert not inspect.iscoroutinefunction(repository.buscar_historico)

    class TestBuscarPorConjunto:
        """Testes para metodo buscar_por_conjunto()."""

        def test_deve_filtrar_por_id_conjunto(
            self,
            repository,
            mock_session: MagicMock,
            mock_result: MagicMock,
        ) -> None:
            """Query deve filtrar por id_conjunto especificado."""
            mock_session.execute.return_value = mock_result

            repository.buscar_por_conjunto(1)

            call_args = mock_session.execute.call_args
            params = call_args[0][1]
            assert params.get("conjunto") == 1

        def test_deve_ser_metodo_sincrono(self, repository) -> None:
            """buscar_por_conjunto deve ser metodo SINCRONO."""
            import inspect

            assert not inspect.iscoroutinefunction(repository.buscar_por_conjunto)


@pytest.mark.unit
class TestMapToEntities:
    """Testes para mapeamento de rows para entidades."""

    @pytest.fixture
    def repository(self, mock_session: MagicMock):
        """Repository com session mockada."""
        from backend.apps.api_interrupcoes.repositories.oracle_interrupcao_repository import (
            OracleInterrupcaoRepository,
        )

        return OracleInterrupcaoRepository(mock_session)

    def test_deve_ignorar_rows_com_ibge_invalido_e_continuar(
        self,
        repository,
        sample_row: MagicMock,
        sample_row_invalid_ibge: MagicMock,
    ) -> None:
        """Rows com IBGE invalido sao ignoradas, validas sao processadas."""
        rows = [sample_row_invalid_ibge, sample_row]

        entities = repository._map_to_entities(rows)

        # Apenas a row valida deve ser mapeada
        assert len(entities) == 1
        assert entities[0].id == 12345

    def test_deve_retornar_lista_vazia_para_rows_vazio(
        self,
        repository,
    ) -> None:
        """Lista vazia de rows retorna lista vazia de entidades."""
        entities = repository._map_to_entities([])
        assert entities == []


@pytest.mark.unit
class TestImplementsProtocol:
    """Testes para verificar que implementa InterrupcaoRepository Protocol."""

    def test_deve_ter_metodo_buscar_ativas(self, mock_session: MagicMock) -> None:
        """Repositorio deve ter metodo buscar_ativas."""
        from backend.apps.api_interrupcoes.repositories.oracle_interrupcao_repository import (
            OracleInterrupcaoRepository,
        )

        repo = OracleInterrupcaoRepository(mock_session)
        assert hasattr(repo, "buscar_ativas")
        assert callable(repo.buscar_ativas)

    def test_deve_ter_metodo_buscar_por_municipio(
        self,
        mock_session: MagicMock,
    ) -> None:
        """Repositorio deve ter metodo buscar_por_municipio."""
        from backend.apps.api_interrupcoes.repositories.oracle_interrupcao_repository import (
            OracleInterrupcaoRepository,
        )

        repo = OracleInterrupcaoRepository(mock_session)
        assert hasattr(repo, "buscar_por_municipio")
        assert callable(repo.buscar_por_municipio)

    def test_deve_ter_metodo_buscar_por_conjunto(
        self,
        mock_session: MagicMock,
    ) -> None:
        """Repositorio deve ter metodo buscar_por_conjunto."""
        from backend.apps.api_interrupcoes.repositories.oracle_interrupcao_repository import (
            OracleInterrupcaoRepository,
        )

        repo = OracleInterrupcaoRepository(mock_session)
        assert hasattr(repo, "buscar_por_conjunto")
        assert callable(repo.buscar_por_conjunto)

    def test_deve_ter_metodo_buscar_historico(self, mock_session: MagicMock) -> None:
        """Repositorio deve ter metodo buscar_historico."""
        from backend.apps.api_interrupcoes.repositories.oracle_interrupcao_repository import (
            OracleInterrupcaoRepository,
        )

        repo = OracleInterrupcaoRepository(mock_session)
        assert hasattr(repo, "buscar_historico")
        assert callable(repo.buscar_historico)
