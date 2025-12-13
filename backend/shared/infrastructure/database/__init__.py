"""
Modulo de banco de dados.

Fornece conexao com Oracle Database via SQLAlchemy.
"""

from backend.shared.infrastructure.database.oracle_connection import (
    OracleConnection,
    get_engine,
    get_oracle_connection,
    run_in_executor,
)
from backend.shared.infrastructure.database.oracle_pool import OraclePool

__all__ = [
    "OraclePool",
    "OracleConnection",
    "get_oracle_connection",
    "get_engine",
    "run_in_executor",
]
