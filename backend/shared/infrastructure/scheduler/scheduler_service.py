"""Serviço de agendamento de jobs usando APScheduler."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any, Protocol

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class Job(Protocol):
    """Protocol para jobs agendados."""

    @property
    def name(self) -> str:
        """Nome do job para logging e identificação."""
        ...

    async def execute(self) -> None:
        """Executa o job."""
        ...


class SchedulerService:
    """
    Wrapper para APScheduler com interface limpa.

    Fornece métodos para adicionar jobs com expressões cron
    ou intervalos, e gerenciar o ciclo de vida do scheduler.
    """

    def __init__(self) -> None:
        """Inicializa o SchedulerService."""
        self._scheduler = BackgroundScheduler()
        self._jobs: dict[str, Job] = {}

    def add_cron_job(
        self,
        job: Job,
        cron_expression: str,
    ) -> None:
        """
        Adiciona job com expressão cron.

        Args:
            job: Instância do job a executar (deve implementar Protocol Job)
            cron_expression: Expressão cron no formato "minute hour day month day_of_week"
                            Exemplo: "*/30 * * * *" para a cada 30 minutos
        """
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError(
                f"Expressão cron inválida: {cron_expression}. "
                "Formato esperado: 'minute hour day month day_of_week'"
            )

        minute, hour, day, month, day_of_week = parts

        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
        )

        wrapped_func = self._create_job_wrapper(job)

        self._scheduler.add_job(
            wrapped_func,
            trigger=trigger,
            id=job.name,
            name=job.name,
            replace_existing=True,
        )
        self._jobs[job.name] = job
        logger.info(f"Job registrado: {job.name} com cron '{cron_expression}'")

    def add_interval_job(
        self,
        job: Job,
        seconds: int | None = None,
        minutes: int | None = None,
        hours: int | None = None,
    ) -> None:
        """
        Adiciona job com intervalo de tempo.

        Args:
            job: Instância do job a executar
            seconds: Intervalo em segundos
            minutes: Intervalo em minutos
            hours: Intervalo em horas
        """
        trigger = IntervalTrigger(
            seconds=seconds or 0,
            minutes=minutes or 0,
            hours=hours or 0,
        )

        wrapped_func = self._create_job_wrapper(job)

        self._scheduler.add_job(
            wrapped_func,
            trigger=trigger,
            id=job.name,
            name=job.name,
            replace_existing=True,
        )
        self._jobs[job.name] = job
        logger.info(
            f"Job registrado: {job.name} com intervalo "
            f"(seconds={seconds}, minutes={minutes}, hours={hours})"
        )

    def _create_job_wrapper(self, job: Job) -> Callable[[], Any]:
        """
        Cria wrapper para o job com logging e tratamento de erros.

        Args:
            job: Job a ser wrapped

        Returns:
            Função wrapper que executa o job com tratamento de erros
        """

        def wrapped() -> None:
            logger.info(f"Iniciando job: {job.name}")
            try:
                # Executa o job async em um event loop
                asyncio.run(job.execute())
                logger.info(f"Job finalizado com sucesso: {job.name}")
            except Exception as e:
                logger.error(f"Erro no job {job.name}: {e}", exc_info=True)
                # Não propaga a exceção para não parar o scheduler

        return wrapped

    def start(self) -> None:
        """Inicia o scheduler."""
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Scheduler iniciado")

    def stop(self) -> None:
        """Para o scheduler."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Scheduler parado")

    def is_running(self) -> bool:
        """
        Verifica se scheduler está rodando.

        Returns:
            True se scheduler está rodando, False caso contrário
        """
        return bool(self._scheduler.running)

    def get_jobs_status(self) -> dict[str, Any]:
        """
        Retorna status de todos os jobs registrados.

        Returns:
            Dicionário com status do scheduler e lista de jobs
        """
        jobs_info = []
        for job in self._scheduler.get_jobs():
            next_run = None
            if hasattr(job, "next_run_time") and job.next_run_time:
                next_run = str(job.next_run_time)

            jobs_info.append(
                {
                    "name": job.id,
                    "next_run": next_run,
                }
            )

        return {
            "running": self.is_running(),
            "jobs": jobs_info,
        }

    def remove_job(self, job_name: str) -> None:
        """
        Remove um job do scheduler.

        Args:
            job_name: Nome do job a remover
        """
        try:
            self._scheduler.remove_job(job_name)
            self._jobs.pop(job_name, None)
            logger.info(f"Job removido: {job_name}")
        except Exception as e:
            logger.warning(f"Falha ao remover job {job_name}: {e}")


# Singleton para uso global
scheduler_service = SchedulerService()
