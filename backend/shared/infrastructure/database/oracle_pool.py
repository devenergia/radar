"""Gerenciador de Pool de Conexoes Oracle."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import oracledb

from backend.shared.domain.errors import DatabaseConnectionError, DatabaseQueryError
from backend.shared.infrastructure.config import Settings


class OraclePool:
    """
    Gerenciador de Pool de Conexoes Oracle.

    Implementa o padrao Singleton para garantir uma unica instancia do pool.
    Suporta health checks e graceful shutdown.
    """

    _instance: OraclePool | None = None
    _pool: oracledb.AsyncConnectionPool | None = None

    def __new__(cls) -> OraclePool:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self, settings: Settings) -> None:
        """
        Inicializa o pool de conexoes.

        Args:
            settings: Configuracoes da aplicacao
        """
        if self._pool is not None:
            return

        try:
            self._pool = oracledb.create_pool_async(
                user=settings.oracle_user,
                password=settings.oracle_password,
                dsn=settings.oracle_dsn,
                min=settings.pool_min,
                max=settings.pool_max,
                increment=settings.pool_increment,
                timeout=settings.pool_timeout,
            )
        except Exception as e:
            raise DatabaseConnectionError(e, "RADAR") from e

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[oracledb.AsyncConnection, None]:
        """
        Context manager para obter uma conexao do pool.

        Yields:
            Conexao Oracle

        Raises:
            DatabaseConnectionError: Se falhar ao obter conexao
        """
        if self._pool is None:
            raise DatabaseConnectionError(
                Exception("Pool nao inicializado"), "RADAR"
            )

        conn: oracledb.AsyncConnection | None = None
        try:
            conn = await self._pool.acquire()
            yield conn
        except Exception as e:
            raise DatabaseConnectionError(e, "RADAR") from e
        finally:
            if conn is not None:
                await self._pool.release(conn)

    async def execute(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Executa uma query e retorna os resultados como lista de dicionarios.

        Args:
            sql: Query SQL
            params: Parametros bind

        Returns:
            Lista de dicionarios com os resultados

        Raises:
            DatabaseQueryError: Se falhar ao executar query
        """
        async with self.connection() as conn:
            try:
                cursor = await conn.cursor()
                await cursor.execute(sql, params or {})

                columns = [col[0].lower() for col in cursor.description or []]
                rows = await cursor.fetchall()

                return [dict(zip(columns, row)) for row in rows]
            except Exception as e:
                raise DatabaseQueryError(e, sql) from e

    async def execute_one(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Executa uma query e retorna apenas o primeiro resultado.

        Args:
            sql: Query SQL
            params: Parametros bind

        Returns:
            Dicionario com o resultado ou None
        """
        results = await self.execute(sql, params)
        return results[0] if results else None

    async def health_check(self) -> dict[str, Any]:
        """
        Verifica se o pool esta saudavel.

        Returns:
            Dicionario com status e latencia
        """
        import time

        start = time.perf_counter()
        try:
            await self.execute("SELECT 1 FROM DUAL")
            latency_ms = (time.perf_counter() - start) * 1000
            return {"healthy": True, "latency_ms": round(latency_ms, 2)}
        except Exception:
            latency_ms = (time.perf_counter() - start) * 1000
            return {"healthy": False, "latency_ms": round(latency_ms, 2)}

    async def close(self) -> None:
        """Fecha o pool de conexoes."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    def is_ready(self) -> bool:
        """Verifica se o pool esta inicializado."""
        return self._pool is not None


# Instancia singleton
oracle_pool = OraclePool()


async def get_oracle_pool() -> OraclePool:
    """Dependency injection para FastAPI."""
    return oracle_pool
