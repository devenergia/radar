"""Testes unitários para InterrupcaoCacheWarmupJob."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest

if TYPE_CHECKING:
    from backend.apps.api_interrupcoes.jobs.interrupcao_cache_warmup import (
        InterrupcaoCacheWarmupJob,
    )


@pytest.fixture
def mock_use_case() -> MagicMock:
    """Cria mock do use case."""
    from backend.shared.domain.result import Result

    use_case = MagicMock()
    use_case.execute = AsyncMock(return_value=Result.ok([]))
    return use_case


@pytest.fixture
def job(mock_use_case: MagicMock) -> InterrupcaoCacheWarmupJob:
    """Cria instância do job para testes."""
    from backend.apps.api_interrupcoes.jobs.interrupcao_cache_warmup import (
        InterrupcaoCacheWarmupJob,
    )

    return InterrupcaoCacheWarmupJob(use_case=mock_use_case)


@pytest.mark.unit
class TestInterrupcaoCacheWarmupJobProperties:
    """Testes para propriedades do job."""

    def test_deve_ter_nome_correto(self, job: InterrupcaoCacheWarmupJob) -> None:
        """Nome do job deve ser 'interrupcao_cache_warmup'."""
        assert job.name == "interrupcao_cache_warmup"

    def test_deve_ter_cron_expression_30_minutos(
        self, job: InterrupcaoCacheWarmupJob
    ) -> None:
        """Expressão cron deve ser a cada 30 minutos."""
        assert job.CRON_EXPRESSION == "*/30 * * * *"

    def test_deve_ter_cache_key_definida(
        self, job: InterrupcaoCacheWarmupJob
    ) -> None:
        """Deve ter chave de cache definida."""
        assert job.CACHE_KEY == "interrupcoes:ativas:v1"


@pytest.mark.unit
class TestInterrupcaoCacheWarmupJobExecute:
    """Testes para execução do job."""

    @pytest.mark.asyncio
    async def test_deve_executar_use_case_com_force_refresh(
        self, job: InterrupcaoCacheWarmupJob, mock_use_case: MagicMock
    ) -> None:
        """Deve chamar use case com force_refresh=True."""
        from backend.shared.domain.result import Result

        mock_use_case.execute.return_value = Result.ok([])

        await job.execute()

        mock_use_case.execute.assert_called_once_with(force_refresh=True)

    @pytest.mark.asyncio
    async def test_deve_propagar_erro_quando_use_case_falha(
        self, job: InterrupcaoCacheWarmupJob, mock_use_case: MagicMock
    ) -> None:
        """Deve propagar erro quando use case falha."""
        from backend.shared.domain.result import Result

        mock_use_case.execute.return_value = Result.fail("Erro de conexão Oracle")

        with pytest.raises(RuntimeError, match="Cache warmup failed"):
            await job.execute()

    @pytest.mark.asyncio
    async def test_deve_completar_com_sucesso_quando_use_case_retorna_dados(
        self, job: InterrupcaoCacheWarmupJob, mock_use_case: MagicMock
    ) -> None:
        """Deve completar com sucesso quando use case retorna dados."""
        from backend.shared.domain.result import Result

        dados_mock = [{"id": 1, "tipo": "PROGRAMADA"}]
        mock_use_case.execute.return_value = Result.ok(dados_mock)

        # Não deve lançar exceção
        await job.execute()

        mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_deve_completar_com_sucesso_quando_use_case_retorna_lista_vazia(
        self, job: InterrupcaoCacheWarmupJob, mock_use_case: MagicMock
    ) -> None:
        """Deve completar com sucesso mesmo com lista vazia."""
        from backend.shared.domain.result import Result

        mock_use_case.execute.return_value = Result.ok([])

        # Não deve lançar exceção
        await job.execute()

        mock_use_case.execute.assert_called_once()


@pytest.mark.unit
class TestInterrupcaoCacheWarmupJobInit:
    """Testes para inicialização do job."""

    def test_deve_armazenar_use_case_recebido(self, mock_use_case: MagicMock) -> None:
        """Deve armazenar o use case recebido."""
        from backend.apps.api_interrupcoes.jobs.interrupcao_cache_warmup import (
            InterrupcaoCacheWarmupJob,
        )

        job = InterrupcaoCacheWarmupJob(use_case=mock_use_case)

        assert job._use_case == mock_use_case


@pytest.mark.unit
class TestInterrupcaoCacheWarmupJobProtocolCompliance:
    """Testes de conformidade com o Protocol Job."""

    def test_deve_implementar_property_name(
        self, job: InterrupcaoCacheWarmupJob
    ) -> None:
        """Deve implementar property 'name' do Protocol."""
        assert hasattr(job, "name")
        assert isinstance(job.name, str)

    @pytest.mark.asyncio
    async def test_deve_implementar_metodo_execute(
        self, job: InterrupcaoCacheWarmupJob, mock_use_case: MagicMock
    ) -> None:
        """Deve implementar método 'execute' do Protocol."""
        from backend.shared.domain.result import Result

        mock_use_case.execute.return_value = Result.ok([])

        assert hasattr(job, "execute")
        # Deve ser chamável e async
        await job.execute()
