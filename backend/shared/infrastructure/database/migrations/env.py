"""Alembic environment configuration for RADAR project.

Este arquivo configura o ambiente de migracao do Alembic para trabalhar
com Oracle Database via SQLAlchemy.

Uso:
    # Criar nova migracao
    alembic revision --autogenerate -m "descricao"

    # Aplicar migracoes pendentes
    alembic upgrade head

    # Reverter ultima migracao
    alembic downgrade -1

    # Ver historico
    alembic history
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from backend.shared.infrastructure.config import get_settings

# Importar todos os models para autogenerate detectar
from backend.shared.infrastructure.database.models import Base

# ============================================================================
# Alembic Config object
# ============================================================================

config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData para autogenerate
target_metadata = Base.metadata

# ============================================================================
# Helper Functions
# ============================================================================


def get_url() -> str:
    """Retorna URL de conexao Oracle formatada para SQLAlchemy.

    Formato: oracle+oracledb://user:password@host:port/?service_name=SERVICE

    Returns:
        URL de conexao SQLAlchemy
    """
    settings = get_settings()

    # Formato para Oracle com oracledb driver
    return (
        f"oracle+oracledb://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}"
        f"/?service_name={settings.db_service}"
    )


def run_migrations_offline() -> None:
    """Executa migrations em modo 'offline'.

    Neste modo, ao inves de conectar ao banco, gera SQL puro
    que pode ser executado manualmente.

    Util para:
    - Revisar SQL antes de executar
    - Ambientes sem acesso direto ao banco
    - Documentacao
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Oracle specific
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrations em modo 'online'.

    Conecta diretamente ao banco e aplica as migrations.
    Este e o modo padrao para desenvolvimento e producao.
    """
    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
        # Oracle specific options
        thick_mode=False,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Comparacoes mais precisas para Oracle
            compare_type=True,
            compare_server_default=True,
            # Incluir schema nas migrations
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ============================================================================
# Main
# ============================================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
