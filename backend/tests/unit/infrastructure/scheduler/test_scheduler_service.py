"""Testes unitários para SchedulerService."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest

if TYPE_CHECKING:
    from backend.shared.infrastructure.scheduler.scheduler_service import SchedulerService


@pytest.fixture
def scheduler() -> SchedulerService:
    """Cria instância do SchedulerService para testes."""
    from backend.shared.infrastructure.scheduler.scheduler_service import SchedulerService

    return SchedulerService()


@pytest.fixture
def mock_job() -> MagicMock:
    """Cria mock de um job."""
    job = MagicMock()
    job.name = "test_job"
    job.execute = AsyncMock(return_value=None)
    return job


@pytest.mark.unit
class TestSchedulerServiceInit:
    """Testes de inicialização do SchedulerService."""

    def test_deve_criar_scheduler_nao_rodando(self, scheduler: SchedulerService) -> None:
        """Scheduler deve iniciar parado."""
        assert scheduler.is_running() is False

    def test_deve_iniciar_sem_jobs_registrados(self, scheduler: SchedulerService) -> None:
        """Scheduler deve iniciar sem jobs."""
        status = scheduler.get_jobs_status()
        assert status["running"] is False
        assert len(status["jobs"]) == 0


@pytest.mark.unit
class TestSchedulerServiceAddCronJob:
    """Testes para adição de jobs cron."""

    def test_deve_adicionar_job_com_cron_expression_valida(
        self, scheduler: SchedulerService, mock_job: MagicMock
    ) -> None:
        """Deve adicionar job com expressão cron válida."""
        scheduler.add_cron_job(mock_job, "*/30 * * * *")

        status = scheduler.get_jobs_status()
        assert len(status["jobs"]) == 1
        assert status["jobs"][0]["name"] == "test_job"

    def test_deve_registrar_job_no_dicionario_interno(
        self, scheduler: SchedulerService, mock_job: MagicMock
    ) -> None:
        """Deve manter referência ao job no dicionário interno."""
        scheduler.add_cron_job(mock_job, "*/30 * * * *")
        assert "test_job" in scheduler._jobs
        assert scheduler._jobs["test_job"] == mock_job

    def test_deve_substituir_job_existente_com_mesmo_nome(
        self, scheduler: SchedulerService, mock_job: MagicMock
    ) -> None:
        """Deve substituir job existente quando replace_existing=True."""
        scheduler.start()  # Precisa iniciar para replace_existing funcionar
        try:
            scheduler.add_cron_job(mock_job, "*/30 * * * *")
            scheduler.add_cron_job(mock_job, "*/15 * * * *")

            status = scheduler.get_jobs_status()
            assert len(status["jobs"]) == 1
        finally:
            scheduler.stop()

    def test_deve_aceitar_diferentes_expressoes_cron(
        self, scheduler: SchedulerService
    ) -> None:
        """Deve aceitar várias expressões cron válidas."""
        expressoes = [
            "*/30 * * * *",  # A cada 30 minutos
            "0 */2 * * *",  # A cada 2 horas
            "0 8 * * 1-5",  # 8h em dias úteis
            "0 0 1 * *",  # Primeiro dia do mês
        ]

        for i, expr in enumerate(expressoes):
            job = MagicMock()
            job.name = f"job_{i}"
            job.execute = AsyncMock()
            scheduler.add_cron_job(job, expr)

        status = scheduler.get_jobs_status()
        assert len(status["jobs"]) == 4


@pytest.mark.unit
class TestSchedulerServiceStartStop:
    """Testes para iniciar e parar o scheduler."""

    def test_deve_iniciar_scheduler(self, scheduler: SchedulerService) -> None:
        """Deve iniciar o scheduler corretamente."""
        scheduler.start()
        assert scheduler.is_running() is True
        scheduler.stop()

    def test_deve_parar_scheduler(self, scheduler: SchedulerService) -> None:
        """Deve parar o scheduler corretamente."""
        scheduler.start()
        scheduler.stop()
        assert scheduler.is_running() is False

    def test_nao_deve_falhar_ao_iniciar_scheduler_ja_rodando(
        self, scheduler: SchedulerService
    ) -> None:
        """Não deve falhar ao iniciar scheduler já rodando."""
        scheduler.start()
        scheduler.start()  # Segunda chamada não deve falhar
        assert scheduler.is_running() is True
        scheduler.stop()

    def test_nao_deve_falhar_ao_parar_scheduler_ja_parado(
        self, scheduler: SchedulerService
    ) -> None:
        """Não deve falhar ao parar scheduler já parado."""
        scheduler.stop()  # Não deve falhar
        assert scheduler.is_running() is False


@pytest.mark.unit
class TestSchedulerServiceGetJobsStatus:
    """Testes para obter status dos jobs."""

    def test_deve_retornar_running_false_quando_parado(
        self, scheduler: SchedulerService
    ) -> None:
        """Deve retornar running=False quando scheduler parado."""
        status = scheduler.get_jobs_status()
        assert status["running"] is False

    def test_deve_retornar_running_true_quando_rodando(
        self, scheduler: SchedulerService
    ) -> None:
        """Deve retornar running=True quando scheduler rodando."""
        scheduler.start()
        status = scheduler.get_jobs_status()
        assert status["running"] is True
        scheduler.stop()

    def test_deve_retornar_lista_de_jobs_com_nome_e_next_run(
        self, scheduler: SchedulerService, mock_job: MagicMock
    ) -> None:
        """Deve retornar jobs com nome e próxima execução."""
        scheduler.add_cron_job(mock_job, "*/30 * * * *")
        scheduler.start()

        status = scheduler.get_jobs_status()

        assert len(status["jobs"]) == 1
        assert "name" in status["jobs"][0]
        assert "next_run" in status["jobs"][0]

        scheduler.stop()

    def test_deve_retornar_lista_vazia_quando_sem_jobs(
        self, scheduler: SchedulerService
    ) -> None:
        """Deve retornar lista vazia quando não há jobs."""
        status = scheduler.get_jobs_status()
        assert status["jobs"] == []


@pytest.mark.unit
class TestSchedulerServiceJobExecution:
    """Testes para execução de jobs."""

    def test_wrapper_deve_chamar_execute_do_job(
        self, scheduler: SchedulerService, mock_job: MagicMock
    ) -> None:
        """Wrapper deve chamar método execute do job."""
        scheduler.add_cron_job(mock_job, "*/30 * * * *")

        # Executar o wrapper diretamente (é síncrono e usa asyncio.run)
        wrapped_func = scheduler._create_job_wrapper(mock_job)
        wrapped_func()

        mock_job.execute.assert_called_once()

    def test_wrapper_deve_capturar_excecao_do_job(
        self, scheduler: SchedulerService, mock_job: MagicMock
    ) -> None:
        """Wrapper deve capturar exceção do job sem propagar."""
        mock_job.execute = AsyncMock(side_effect=RuntimeError("Erro teste"))

        scheduler.add_cron_job(mock_job, "*/30 * * * *")

        wrapped_func = scheduler._create_job_wrapper(mock_job)

        # Não deve propagar a exceção
        wrapped_func()  # Não deve lançar exceção

        mock_job.execute.assert_called_once()


@pytest.mark.unit
class TestSchedulerServiceAddIntervalJob:
    """Testes para adição de jobs com intervalo."""

    def test_deve_adicionar_job_com_intervalo_em_minutos(
        self, scheduler: SchedulerService, mock_job: MagicMock
    ) -> None:
        """Deve adicionar job com intervalo em minutos."""
        scheduler.add_interval_job(mock_job, minutes=30)

        status = scheduler.get_jobs_status()
        assert len(status["jobs"]) == 1
        assert status["jobs"][0]["name"] == "test_job"

    def test_deve_adicionar_job_com_intervalo_em_segundos(
        self, scheduler: SchedulerService, mock_job: MagicMock
    ) -> None:
        """Deve adicionar job com intervalo em segundos."""
        scheduler.add_interval_job(mock_job, seconds=300)

        status = scheduler.get_jobs_status()
        assert len(status["jobs"]) == 1
