"""Create audit tables for ANEEL API

Revision ID: 001
Revises:
Create Date: 2025-12-19

Cria as tabelas de auditoria absorvidas do projeto radar-backend:
- TOKEN_ACESSO: Gerenciamento de API Keys
- TIPO_CONSULTA: Tipos de consulta disponiveis
- CONSULTA: Registro de consultas (auditoria)
- INTERRUPCAO_ATIVA: Snapshot de dados por consulta
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Schema padrao do RADAR
SCHEMA = "RADAR_API"


def upgrade() -> None:
    """Aplica a migracao - cria tabelas de auditoria."""

    # ========================================================================
    # Tabela: TOKEN_ACESSO
    # ========================================================================
    op.create_table(
        "TOKEN_ACESSO",
        sa.Column("ID", sa.String(100), nullable=False),
        sa.Column("NOME", sa.String(300), nullable=False),
        sa.Column("DESCRICAO", sa.String(500), nullable=True),
        sa.Column("CHAVE", sa.String(100), nullable=False),
        sa.Column("ATIVO", sa.String(1), nullable=False, server_default="S"),
        sa.Column("DATA_CRIACAO", sa.DateTime(), nullable=False, server_default=sa.func.sysdate()),
        sa.Column("DATA_EXPIRACAO", sa.DateTime(), nullable=True),
        sa.Column("ULTIMO_ACESSO", sa.DateTime(), nullable=True),
        sa.Column("TOTAL_ACESSOS", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("IP_ORIGEM_PERMITIDO", sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint("ID", name="TOKEN_ACESSO_PK"),
        sa.UniqueConstraint("CHAVE", name="TOKEN_ACESSO_CHAVE_UK"),
        sa.CheckConstraint("ATIVO IN ('S', 'N')", name="TOKEN_ACESSO_ATIVO_CK"),
        schema=SCHEMA,
    )

    op.create_index("IDX_TOKEN_ACESSO_CHAVE", "TOKEN_ACESSO", ["CHAVE"], schema=SCHEMA)
    op.create_index("IDX_TOKEN_ACESSO_ATIVO", "TOKEN_ACESSO", ["ATIVO"], schema=SCHEMA)

    # ========================================================================
    # Tabela: TIPO_CONSULTA
    # ========================================================================
    op.create_table(
        "TIPO_CONSULTA",
        sa.Column("ID", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("CODIGO", sa.String(50), nullable=False),
        sa.Column("DESCRICAO", sa.String(200), nullable=False),
        sa.Column("ATIVO", sa.String(1), nullable=False, server_default="S"),
        sa.PrimaryKeyConstraint("ID", name="TIPO_CONSULTA_PK"),
        sa.UniqueConstraint("CODIGO", name="TIPO_CONSULTA_CODIGO_UK"),
        schema=SCHEMA,
    )

    # ========================================================================
    # Tabela: CONSULTA
    # ========================================================================
    op.create_table(
        "CONSULTA",
        sa.Column("ID", sa.String(100), nullable=False),
        sa.Column("ID_TOKEN", sa.String(100), nullable=True),
        sa.Column("ID_TIPO_CONSULTA", sa.Integer(), nullable=False),
        sa.Column("DATA_BRASILIA", sa.DateTime(), nullable=False),
        sa.Column("DATA_INICIO", sa.DateTime(), nullable=False, server_default=sa.func.sysdate()),
        sa.Column("DATA_FIM", sa.DateTime(), nullable=True),
        sa.Column("PARAMETROS", sa.Text(), nullable=True),
        sa.Column("IP_ORIGEM", sa.String(50), nullable=True),
        sa.Column("STATUS", sa.String(20), nullable=False, server_default="PROCESSANDO"),
        sa.Column("MENSAGEM_ERRO", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("ID", name="CONSULTA_PK"),
        sa.ForeignKeyConstraint(
            ["ID_TOKEN"],
            [f"{SCHEMA}.TOKEN_ACESSO.ID"],
            name="FK_CONSULTA_TOKEN",
        ),
        sa.ForeignKeyConstraint(
            ["ID_TIPO_CONSULTA"],
            [f"{SCHEMA}.TIPO_CONSULTA.ID"],
            name="FK_CONSULTA_TIPO",
        ),
        schema=SCHEMA,
    )

    op.create_index("IDX_CONSULTA_DATA_BRASILIA", "CONSULTA", ["DATA_BRASILIA"], schema=SCHEMA)
    op.create_index("IDX_CONSULTA_TOKEN", "CONSULTA", ["ID_TOKEN"], schema=SCHEMA)
    op.create_index("IDX_CONSULTA_STATUS", "CONSULTA", ["STATUS"], schema=SCHEMA)

    # ========================================================================
    # Tabela: INTERRUPCAO_ATIVA
    # ========================================================================
    op.create_table(
        "INTERRUPCAO_ATIVA",
        sa.Column("ID", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("ID_CONSULTA", sa.String(100), nullable=False),
        sa.Column("ID_CONJUNTO_UC", sa.Integer(), nullable=False),
        sa.Column("ID_MUNICIPIO", sa.Integer(), nullable=False),
        sa.Column("QTD_UCS_ATENDIDAS", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("QTD_PROGRAMADA", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("QTD_NAO_PROGRAMADA", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("ID", name="INTERRUPCAO_ATIVA_PK"),
        sa.ForeignKeyConstraint(
            ["ID_CONSULTA"],
            [f"{SCHEMA}.CONSULTA.ID"],
            name="FK_INTERRUPCAO_CONSULTA",
        ),
        schema=SCHEMA,
    )

    op.create_index(
        "IDX_INTERRUPCAO_CONSULTA", "INTERRUPCAO_ATIVA", ["ID_CONSULTA"], schema=SCHEMA
    )
    op.create_index(
        "IDX_INTERRUPCAO_MUNICIPIO", "INTERRUPCAO_ATIVA", ["ID_MUNICIPIO"], schema=SCHEMA
    )

    # ========================================================================
    # Dados Iniciais: Tipos de Consulta
    # ========================================================================
    op.execute(
        f"""
        INSERT INTO {SCHEMA}.TIPO_CONSULTA (ID, CODIGO, DESCRICAO, ATIVO) VALUES
        (1, 'INTERRUPCAO_ATIVA', 'Quantitativo de Interrupcoes Ativas', 'S')
        """
    )

    op.execute(
        f"""
        INSERT INTO {SCHEMA}.TIPO_CONSULTA (ID, CODIGO, DESCRICAO, ATIVO) VALUES
        (2, 'DADOS_DEMANDA', 'Dados de Demanda', 'S')
        """
    )

    op.execute(
        f"""
        INSERT INTO {SCHEMA}.TIPO_CONSULTA (ID, CODIGO, DESCRICAO, ATIVO) VALUES
        (3, 'DEMANDAS_DIVERSAS', 'Quantitativo de Demandas Diversas', 'S')
        """
    )

    op.execute(
        f"""
        INSERT INTO {SCHEMA}.TIPO_CONSULTA (ID, CODIGO, DESCRICAO, ATIVO) VALUES
        (4, 'TEMPO_REAL', 'Dados em Tempo Real', 'S')
        """
    )


def downgrade() -> None:
    """Reverte a migracao - remove tabelas de auditoria."""

    # Remover na ordem inversa (por causa das FKs)
    op.drop_table("INTERRUPCAO_ATIVA", schema=SCHEMA)
    op.drop_table("CONSULTA", schema=SCHEMA)
    op.drop_table("TIPO_CONSULTA", schema=SCHEMA)
    op.drop_table("TOKEN_ACESSO", schema=SCHEMA)
