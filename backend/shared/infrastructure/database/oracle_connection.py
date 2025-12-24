"""
Oracle Database Connection Module

Gerencia conexões com Oracle Database usando SQLAlchemy.
Suporta múltiplos ambientes (dev, hm, prd) e pool de conexões otimizado.
"""

from __future__ import annotations

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, Callable, Optional, TypeVar

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import DatabaseError, InterfaceError, OperationalError
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from backend.shared.infrastructure.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

# Pool de threads para operações assíncronas
_executor = ThreadPoolExecutor(max_workers=10)


def get_environment() -> str:
    """
    Detecta o ambiente atual baseado em variáveis de ambiente.

    Returns:
        Prefixo do ambiente (DEV, HM, PRD)
    """
    env = os.getenv("ENVIRONMENT", "development").lower()

    env_map = {
        "development": "DEV",
        "dev": "DEV",
        "homologation": "HM",
        "hm": "HM",
        "staging": "HM",
        "production": "PRD",
        "prd": "PRD",
        "prod": "PRD",
    }

    return env_map.get(env, "DEV")


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Busca variável de ambiente com suporte a prefixo de ambiente.

    Ordem de prioridade:
    1. {ENV}_RADAR_{NAME} (ex: PRD_RADAR_ORACLE_DSN)
    2. {ENV}_{NAME} (ex: PRD_ORACLE_DSN) - fallback legado
    3. {NAME} (ex: ORACLE_DSN)
    4. default

    Args:
        name: Nome da variável (sem prefixo)
        default: Valor padrão se não encontrada

    Returns:
        Valor da variável ou default
    """
    env_prefix = get_environment()

    # Tenta com prefixo completo do ambiente (padrao novo)
    radar_prefixed = os.getenv(f"{env_prefix}_RADAR_{name}")
    if radar_prefixed:
        return radar_prefixed

    # Fallback para prefixo legado
    prefixed_value = os.getenv(f"{env_prefix}_{name}")
    if prefixed_value:
        return prefixed_value

    # Fallback para variável sem prefixo
    return os.getenv(name, default)


class OracleConnection:
    """
    Gerenciador de conexão Oracle com SQLAlchemy.

    Implementa padrão Singleton para garantir uma única instância do engine.
    Suporta operações síncronas e assíncronas.
    """

    _instance: Optional[OracleConnection] = None
    _engine: Optional[Engine] = None

    def __new__(cls) -> OracleConnection:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Evita reinicialização
        if self._engine is not None:
            return

    def _build_connection_url(self) -> str:
        """Constrói URL de conexão Oracle."""
        user = get_env_var("ORACLE_USER")
        password = get_env_var("ORACLE_PASSWORD")
        dsn = get_env_var("ORACLE_DSN")

        if not all([user, password, dsn]):
            raise ValueError(
                "Configuração Oracle incompleta. "
                "Defina ORACLE_USER, ORACLE_PASSWORD e ORACLE_DSN"
            )

        return f"oracle+oracledb://{user}:{password}@{dsn}"

    def create_engine(
        self,
        pool_size: int = 20,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
    ) -> Engine:
        """
        Cria ou retorna engine SQLAlchemy para Oracle.

        Args:
            pool_size: Número de conexões mantidas no pool
            max_overflow: Conexões extras permitidas além do pool_size
            pool_timeout: Segundos para aguardar conexão disponível
            pool_recycle: Segundos para reciclar conexões

        Returns:
            Engine SQLAlchemy configurado
        """
        if self._engine is not None:
            return self._engine

        database_url = self._build_connection_url()
        debug_mode = os.getenv("DEBUG", "false").lower() == "true"

        env = get_environment()
        logger.info(
            "creating_oracle_engine",
            environment=env,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        self._engine = create_engine(
            database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,  # Valida conexões antes de usar
            echo=debug_mode,
        )

        logger.info("oracle_engine_created", environment=env)
        return self._engine

    def get_engine(self) -> Engine:
        """
        Retorna engine existente ou cria novo com configurações padrão.

        Returns:
            Engine SQLAlchemy
        """
        if self._engine is None:
            return self.create_engine()
        return self._engine

    def execute_query(
        self,
        sql: str,
        params: Optional[dict[str, Any]] = None,
    ) -> list[Any]:
        """
        Executa query síncrona.

        Args:
            sql: Query SQL com parâmetros nomeados
            params: Dicionário de parâmetros

        Returns:
            Lista de resultados
        """
        engine = self.get_engine()

        with engine.connect() as connection:
            result = connection.execute(text(sql), params or {})
            return result.fetchall()

    def execute_with_retry(
        self,
        sql: str,
        params: Optional[dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> list[Any]:
        """
        Executa query com retry automático para erros de conexão.

        Args:
            sql: Query SQL
            params: Parâmetros da query
            max_retries: Número máximo de tentativas

        Returns:
            Lista de resultados

        Raises:
            OperationalError: Se todas as tentativas falharem
            DatabaseError: Para erros de SQL (sem retry)
        """
        engine = self.get_engine()
        last_error: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                with engine.connect() as conn:
                    result = conn.execute(text(sql), params or {})
                    return result.fetchall()

            except (OperationalError, InterfaceError) as e:
                last_error = e
                logger.warning(
                    "query_retry",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    error=str(e),
                )
                continue

            except DatabaseError:
                # Erros de SQL não devem fazer retry
                raise

        if last_error:
            raise last_error
        return []

    async def execute_async(
        self,
        sql: str,
        params: Optional[dict[str, Any]] = None,
    ) -> list[Any]:
        """
        Executa query de forma assíncrona usando thread pool.

        Args:
            sql: Query SQL
            params: Parâmetros da query

        Returns:
            Lista de resultados
        """
        return await run_in_executor(self.execute_query, sql, params)

    def health_check(self) -> dict[str, Any]:
        """
        Verifica saúde da conexão com o banco.

        Returns:
            Dicionário com status da conexão
        """
        try:
            engine = self.get_engine()

            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 FROM DUAL"))
                result.fetchone()

            pool = engine.pool

            return {
                "status": "healthy",
                "database": "oracle",
                "environment": get_environment(),
                "pool_size": pool.size(),
                "checked_out": pool.checkedout(),
            }

        except Exception as e:
            logger.error("health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "database": "oracle",
                "environment": get_environment(),
                "error": str(e),
            }

    def close(self) -> None:
        """Fecha engine e libera recursos."""
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
            logger.info("oracle_engine_closed")


async def run_in_executor(
    func: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Executa função síncrona em thread separada.

    Args:
        func: Função a executar
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados

    Returns:
        Resultado da função
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        partial(func, *args, **kwargs),
    )


# Instância global para acesso simplificado
_oracle_connection: Optional[OracleConnection] = None


def get_oracle_connection() -> OracleConnection:
    """
    Retorna instância singleton da conexão Oracle.

    Returns:
        OracleConnection instance
    """
    global _oracle_connection
    if _oracle_connection is None:
        _oracle_connection = OracleConnection()
    return _oracle_connection


def get_engine() -> Engine:
    """
    Atalho para obter engine Oracle.

    Returns:
        SQLAlchemy Engine
    """
    return get_oracle_connection().get_engine()


# ========== Session Factory (Padrao do Projeto de Referencia) ==========

# SessionLocal global (inicializado sob demanda)
_session_local: Optional[sessionmaker] = None


def get_session_factory() -> sessionmaker:
    """
    Retorna session factory singleton.

    Returns:
        sessionmaker configurado com engine Oracle
    """
    global _session_local
    if _session_local is None:
        _session_local = sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
        )
    return _session_local


def get_sync_session() -> Generator[Session, None, None]:
    """
    Dependency injection para sessao SINCRONA.

    Este e o PADRAO RECOMENDADO para endpoints Oracle.
    O projeto de referencia (MJQEE-GFUZ) usa este padrao.

    Usage:
        @router.get("/items")
        def get_items(session: Session = Depends(get_sync_session)):
            result = session.execute(text("SELECT ..."))
            return result.fetchall()

    Yields:
        Session: SQLAlchemy sync session
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
