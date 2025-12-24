"""Testes unitarios para Use Case GetInterrupcoesAtivasUseCase.

Seguindo TDD e padrao AAA (Arrange-Act-Assert).
"""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import AsyncMock

import pytest

from backend.apps.api_interrupcoes.repositories.interrupcao_repository import (
    InterrupcaoAgregadaDB,
)
from backend.apps.api_interrupcoes.schemas import InterrupcaoAgregadaItem
from backend.apps.api_interrupcoes.use_cases.get_interrupcoes_ativas import (
    GetInterrupcoesAtivasUseCase,
)


@pytest.mark.unit
class TestGetInterrupcoesAtivasUseCase:
    """Testes para Use Case GetInterrupcoesAtivasUseCase."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Mock do repositorio de interrupcoes."""
        repo = AsyncMock()
        repo.find_ativas_agregadas = AsyncMock(return_value=[])
        return repo

    @pytest.fixture
    def mock_cache(self) -> AsyncMock:
        """Mock do servico de cache."""
        cache = AsyncMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()
        cache.get_stale = AsyncMock(return_value=None)
        return cache

    @pytest.fixture
    def use_case(
        self,
        mock_repository: AsyncMock,
        mock_cache: AsyncMock,
    ) -> GetInterrupcoesAtivasUseCase:
        """Instancia do use case com mocks."""
        return GetInterrupcoesAtivasUseCase(
            repository=mock_repository,
            cache=mock_cache,
        )

    @pytest.fixture
    def interrupcao_agregada_factory(self) -> Callable[..., InterrupcaoAgregadaDB]:
        """Factory para criar InterrupcaoAgregadaDB de teste."""

        def _create(
            conjunto: int = 1,
            municipio_ibge: int = 1400100,
            qtd_ucs_atendidas: int = 0,
            qtd_programada: int = 100,
            qtd_nao_programada: int = 50,
        ) -> InterrupcaoAgregadaDB:
            return InterrupcaoAgregadaDB(
                conjunto=conjunto,
                municipio_ibge=municipio_ibge,
                qtd_ucs_atendidas=qtd_ucs_atendidas,
                qtd_programada=qtd_programada,
                qtd_nao_programada=qtd_nao_programada,
            )

        return _create

    class TestCacheHit:
        """Testes quando dados estao em cache."""

        @pytest.mark.asyncio
        async def test_deve_retornar_dados_do_cache_quando_disponivel(
            self,
            use_case: GetInterrupcoesAtivasUseCase,
            mock_cache: AsyncMock,
            mock_repository: AsyncMock,
        ) -> None:
            """Se cache tem dados, retorna do cache sem ir ao banco."""
            # Arrange
            cached_data = [
                InterrupcaoAgregadaItem(
                    ideConjuntoUnidadeConsumidora=1,
                    ideMunicipio=1400100,
                    qtdUCsAtendidas=0,
                    qtdOcorrenciaProgramada=100,
                    qtdOcorrenciaNaoProgramada=50,
                )
            ]
            mock_cache.get.return_value = cached_data

            # Act
            result = await use_case.execute()

            # Assert
            assert result.is_success
            assert result.value == cached_data
            mock_repository.find_ativas_agregadas.assert_not_called()

        @pytest.mark.asyncio
        async def test_nao_deve_atualizar_cache_quando_cache_hit(
            self,
            use_case: GetInterrupcoesAtivasUseCase,
            mock_cache: AsyncMock,
        ) -> None:
            """Cache hit nao deve chamar cache.set()."""
            # Arrange
            mock_cache.get.return_value = [
                InterrupcaoAgregadaItem(
                    ideConjuntoUnidadeConsumidora=1,
                    ideMunicipio=1400100,
                    qtdUCsAtendidas=0,
                    qtdOcorrenciaProgramada=100,
                    qtdOcorrenciaNaoProgramada=50,
                )
            ]

            # Act
            await use_case.execute()

            # Assert
            mock_cache.set.assert_not_called()

        @pytest.mark.asyncio
        async def test_deve_usar_chave_correta_do_cache(
            self,
            use_case: GetInterrupcoesAtivasUseCase,
            mock_cache: AsyncMock,
        ) -> None:
            """Deve buscar cache com a chave 'interrupcoes:ativas'."""
            # Arrange
            mock_cache.get.return_value = None

            # Act
            await use_case.execute()

            # Assert
            mock_cache.get.assert_called_once_with("interrupcoes:ativas")

    class TestCacheMiss:
        """Testes quando cache esta vazio."""

        @pytest.mark.asyncio
        async def test_deve_buscar_do_repositorio_quando_cache_vazio(
            self,
            use_case: GetInterrupcoesAtivasUseCase,
            mock_cache: AsyncMock,
            mock_repository: AsyncMock,
            interrupcao_agregada_factory: Callable[..., InterrupcaoAgregadaDB],
        ) -> None:
            """Cache miss deve buscar do repositorio."""
            # Arrange
            mock_cache.get.return_value = None
            mock_repository.find_ativas_agregadas.return_value = [
                interrupcao_agregada_factory(qtd_programada=50),
                interrupcao_agregada_factory(conjunto=2, qtd_programada=30),
            ]

            # Act
            result = await use_case.execute()

            # Assert
            assert result.is_success
            mock_repository.find_ativas_agregadas.assert_called_once()

        @pytest.mark.asyncio
        async def test_deve_atualizar_cache_apos_buscar_do_repositorio(
            self,
            use_case: GetInterrupcoesAtivasUseCase,
            mock_cache: AsyncMock,
            mock_repository: AsyncMock,
            interrupcao_agregada_factory: Callable[..., InterrupcaoAgregadaDB],
        ) -> None:
            """Apos buscar do banco, deve atualizar cache."""
            # Arrange
            mock_cache.get.return_value = None
            mock_repository.find_ativas_agregadas.return_value = [
                interrupcao_agregada_factory()
            ]

            # Act
            await use_case.execute()

            # Assert
            mock_cache.set.assert_called_once()

        @pytest.mark.asyncio
        async def test_cache_deve_ter_ttl_de_5_minutos(
            self,
            use_case: GetInterrupcoesAtivasUseCase,
            mock_cache: AsyncMock,
            mock_repository: AsyncMock,
            interrupcao_agregada_factory: Callable[..., InterrupcaoAgregadaDB],
        ) -> None:
            """Cache deve ser setado com TTL de 300 segundos."""
            # Arrange
            mock_cache.get.return_value = None
            mock_repository.find_ativas_agregadas.return_value = [
                interrupcao_agregada_factory()
            ]

            # Act
            await use_case.execute()

            # Assert
            call_args = mock_cache.set.call_args
            # cache.set(key, value, ttl)
            assert call_args[0][2] == 300

        @pytest.mark.asyncio
        async def test_deve_converter_para_formato_aneel(
            self,
            use_case: GetInterrupcoesAtivasUseCase,
            mock_cache: AsyncMock,
            mock_repository: AsyncMock,
            interrupcao_agregada_factory: Callable[..., InterrupcaoAgregadaDB],
        ) -> None:
            """Resultado deve ser convertido para formato ANEEL."""
            # Arrange
            mock_cache.get.return_value = None
            mock_repository.find_ativas_agregadas.return_value = [
                interrupcao_agregada_factory(
                    conjunto=1,
                    municipio_ibge=1400100,
                    qtd_programada=50,
                    qtd_nao_programada=30,
                )
            ]

            # Act
            result = await use_case.execute()

            # Assert
            assert result.is_success
            assert len(result.value) == 1
            item = result.value[0]
            # Verifica tipo pelo nome da classe (evita problemas de import diferente)
            assert type(item).__name__ == "InterrupcaoAgregadaItem"
            assert item.ideConjuntoUnidadeConsumidora == 1
            assert item.ideMunicipio == 1400100
            assert item.qtdOcorrenciaProgramada == 50
            assert item.qtdOcorrenciaNaoProgramada == 30

    class TestErros:
        """Testes de tratamento de erros."""

        @pytest.mark.asyncio
        async def test_deve_retornar_failure_quando_repositorio_falha_sem_stale(
            self,
            use_case: GetInterrupcoesAtivasUseCase,
            mock_cache: AsyncMock,
            mock_repository: AsyncMock,
        ) -> None:
            """Erro no repositorio sem stale cache deve retornar Result.fail()."""
            # Arrange
            mock_cache.get.return_value = None
            mock_cache.get_stale.return_value = None
            mock_repository.find_ativas_agregadas.side_effect = Exception("DB Error")

            # Act
            result = await use_case.execute()

            # Assert
            assert result.is_failure
            assert "DB Error" in result.error or "banco" in result.error.lower()

        @pytest.mark.asyncio
        async def test_deve_usar_stale_cache_quando_repositorio_falha(
            self,
            use_case: GetInterrupcoesAtivasUseCase,
            mock_cache: AsyncMock,
            mock_repository: AsyncMock,
        ) -> None:
            """Se banco falha e tem stale cache, usa stale."""
            # Arrange
            stale_data = [
                InterrupcaoAgregadaItem(
                    ideConjuntoUnidadeConsumidora=1,
                    ideMunicipio=1400100,
                    qtdUCsAtendidas=0,
                    qtdOcorrenciaProgramada=100,
                    qtdOcorrenciaNaoProgramada=50,
                )
            ]
            mock_cache.get.return_value = None
            mock_cache.get_stale.return_value = stale_data
            mock_repository.find_ativas_agregadas.side_effect = Exception("DB Error")

            # Act
            result = await use_case.execute()

            # Assert
            assert result.is_success
            assert result.value == stale_data
            mock_cache.get_stale.assert_called_once_with("interrupcoes:ativas")

        @pytest.mark.asyncio
        async def test_deve_tentar_stale_cache_antes_de_retornar_erro(
            self,
            use_case: GetInterrupcoesAtivasUseCase,
            mock_cache: AsyncMock,
            mock_repository: AsyncMock,
        ) -> None:
            """Ao falhar, deve tentar stale cache antes de retornar erro."""
            # Arrange
            mock_cache.get.return_value = None
            mock_cache.get_stale.return_value = None
            mock_repository.find_ativas_agregadas.side_effect = Exception("DB Error")

            # Act
            await use_case.execute()

            # Assert
            mock_cache.get_stale.assert_called_once()

    class TestSemDados:
        """Testes quando nao ha interrupcoes ativas."""

        @pytest.mark.asyncio
        async def test_deve_retornar_lista_vazia_quando_sem_interrupcoes(
            self,
            use_case: GetInterrupcoesAtivasUseCase,
            mock_cache: AsyncMock,
            mock_repository: AsyncMock,
        ) -> None:
            """Sem interrupcoes ativas, retorna lista vazia."""
            # Arrange
            mock_cache.get.return_value = None
            mock_repository.find_ativas_agregadas.return_value = []

            # Act
            result = await use_case.execute()

            # Assert
            assert result.is_success
            assert result.value == []

        @pytest.mark.asyncio
        async def test_deve_armazenar_lista_vazia_no_cache(
            self,
            use_case: GetInterrupcoesAtivasUseCase,
            mock_cache: AsyncMock,
            mock_repository: AsyncMock,
        ) -> None:
            """Lista vazia tambem deve ser armazenada no cache."""
            # Arrange
            mock_cache.get.return_value = None
            mock_repository.find_ativas_agregadas.return_value = []

            # Act
            await use_case.execute()

            # Assert
            mock_cache.set.assert_called_once()
            call_args = mock_cache.set.call_args
            assert call_args[0][1] == []  # value = []

    class TestConstantes:
        """Testes das constantes do use case."""

        def test_cache_key_deve_ser_interrupcoes_ativas(self) -> None:
            """A chave do cache deve ser 'interrupcoes:ativas'."""
            assert GetInterrupcoesAtivasUseCase.CACHE_KEY == "interrupcoes:ativas"

        def test_cache_ttl_deve_ser_300_segundos(self) -> None:
            """O TTL do cache deve ser 300 segundos (5 minutos)."""
            assert GetInterrupcoesAtivasUseCase.CACHE_TTL_SECONDS == 300


@pytest.mark.unit
class TestInterrupcaoAgregadaDB:
    """Testes para a dataclass InterrupcaoAgregadaDB."""

    def test_deve_criar_interrupcao_agregada(self) -> None:
        """Deve criar instancia com todos os campos."""
        # Arrange & Act
        agregada = InterrupcaoAgregadaDB(
            conjunto=1,
            municipio_ibge=1400100,
            qtd_ucs_atendidas=1000,
            qtd_programada=50,
            qtd_nao_programada=30,
        )

        # Assert
        assert agregada.conjunto == 1
        assert agregada.municipio_ibge == 1400100
        assert agregada.qtd_ucs_atendidas == 1000
        assert agregada.qtd_programada == 50
        assert agregada.qtd_nao_programada == 30

    def test_to_aneel_format_deve_retornar_schema_correto(self) -> None:
        """to_aneel_format() deve retornar InterrupcaoAgregadaItem."""
        # Arrange
        agregada = InterrupcaoAgregadaDB(
            conjunto=1,
            municipio_ibge=1400100,
            qtd_ucs_atendidas=1000,
            qtd_programada=50,
            qtd_nao_programada=30,
        )

        # Act
        result = agregada.to_aneel_format()

        # Assert
        # Verifica tipo pelo nome da classe (evita problemas de import diferente)
        assert type(result).__name__ == "InterrupcaoAgregadaItem"
        assert result.ideConjuntoUnidadeConsumidora == 1
        assert result.ideMunicipio == 1400100
        assert result.qtdUCsAtendidas == 1000
        assert result.qtdOcorrenciaProgramada == 50
        assert result.qtdOcorrenciaNaoProgramada == 30

    def test_to_aneel_format_deve_mapear_campos_corretamente(self) -> None:
        """Os campos devem ser mapeados para camelCase ANEEL."""
        # Arrange
        agregada = InterrupcaoAgregadaDB(
            conjunto=99,
            municipio_ibge=1400704,
            qtd_ucs_atendidas=500,
            qtd_programada=10,
            qtd_nao_programada=5,
        )

        # Act
        result = agregada.to_aneel_format()

        # Assert
        # Verifica mapeamento conjunto -> ideConjuntoUnidadeConsumidora
        assert result.ideConjuntoUnidadeConsumidora == agregada.conjunto
        # Verifica mapeamento municipio_ibge -> ideMunicipio
        assert result.ideMunicipio == agregada.municipio_ibge
        # Verifica mapeamento qtd_ucs_atendidas -> qtdUCsAtendidas
        assert result.qtdUCsAtendidas == agregada.qtd_ucs_atendidas
        # Verifica mapeamento qtd_programada -> qtdOcorrenciaProgramada
        assert result.qtdOcorrenciaProgramada == agregada.qtd_programada
        # Verifica mapeamento qtd_nao_programada -> qtdOcorrenciaNaoProgramada
        assert result.qtdOcorrenciaNaoProgramada == agregada.qtd_nao_programada
