"""SQLAlchemy Models for RADAR Database.

Este modulo define os modelos SQLAlchemy para as tabelas do banco RADAR.
Os modelos sao usados tanto pelo Alembic (migrations) quanto pelo
codigo de aplicacao (repositories).

Nomenclatura:
    - Tabelas: SNAKE_CASE_MAIUSCULO (padrao Oracle)
    - Colunas: SNAKE_CASE_MAIUSCULO (padrao Oracle)
    - Classes: PascalCase (padrao Python)

Schema: RADAR_API
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class para todos os models SQLAlchemy."""

    pass


# ============================================================================
# Tabela: TOKEN_ACESSO
# Gerenciamento de API Keys para autenticacao ANEEL
# ============================================================================


class TokenAcesso(Base):
    """Model para tabela TOKEN_ACESSO.

    Armazena os tokens de acesso (API Keys) utilizados pela ANEEL
    para autenticar nas APIs do RADAR.

    Attributes:
        id: Identificador unico (UUID)
        nome: Nome descritivo do cliente/sistema
        descricao: Descricao detalhada do proposito do token
        chave: API Key para autenticacao via header x-api-key
        ativo: Flag indicando se o token esta ativo (S/N)
        data_criacao: Data de criacao do token
        data_expiracao: Data de expiracao (NULL = sem expiracao)
        ultimo_acesso: Data/hora do ultimo acesso
        total_acessos: Contador de acessos realizados
        ip_origem_permitido: Lista de IPs permitidos (separados por virgula)
    """

    __tablename__ = "TOKEN_ACESSO"
    __table_args__ = (
        UniqueConstraint("CHAVE", name="TOKEN_ACESSO_CHAVE_UK"),
        CheckConstraint("ATIVO IN ('S', 'N')", name="TOKEN_ACESSO_ATIVO_CK"),
        Index("IDX_TOKEN_ACESSO_CHAVE", "CHAVE"),
        Index("IDX_TOKEN_ACESSO_ATIVO", "ATIVO"),
        {"schema": "RADAR_API"},
    )

    id = Column("ID", String(100), primary_key=True, default=lambda: str(uuid4()))
    nome = Column("NOME", String(300), nullable=False)
    descricao = Column("DESCRICAO", String(500), nullable=True)
    chave = Column("CHAVE", String(100), nullable=False, unique=True)
    ativo = Column("ATIVO", String(1), nullable=False, default="S")
    data_criacao = Column("DATA_CRIACAO", DateTime, nullable=False, default=datetime.now)
    data_expiracao = Column("DATA_EXPIRACAO", DateTime, nullable=True)
    ultimo_acesso = Column("ULTIMO_ACESSO", DateTime, nullable=True)
    total_acessos = Column("TOTAL_ACESSOS", Integer, nullable=False, default=0)
    ip_origem_permitido = Column("IP_ORIGEM_PERMITIDO", String(500), nullable=True)

    # Relacionamentos
    consultas = relationship("Consulta", back_populates="token")

    def is_ativo(self) -> bool:
        """Verifica se o token esta ativo e nao expirado."""
        if self.ativo != "S":
            return False
        if self.data_expiracao and datetime.now() > self.data_expiracao:
            return False
        return True

    def registrar_acesso(self) -> None:
        """Registra um novo acesso com este token."""
        self.ultimo_acesso = datetime.now()
        self.total_acessos = (self.total_acessos or 0) + 1


# ============================================================================
# Tabela: TIPO_CONSULTA
# Tipos de consulta disponiveis na API
# ============================================================================


class TipoConsulta(Base):
    """Model para tabela TIPO_CONSULTA.

    Define os tipos de consulta disponiveis na API RADAR.

    Attributes:
        id: Identificador numerico do tipo
        codigo: Codigo unico do tipo (ex: 'INTERRUPCAO_ATIVA')
        descricao: Descricao do tipo de consulta
        ativo: Flag indicando se o tipo esta ativo
    """

    __tablename__ = "TIPO_CONSULTA"
    __table_args__ = (
        UniqueConstraint("CODIGO", name="TIPO_CONSULTA_CODIGO_UK"),
        {"schema": "RADAR_API"},
    )

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    codigo = Column("CODIGO", String(50), nullable=False, unique=True)
    descricao = Column("DESCRICAO", String(200), nullable=False)
    ativo = Column("ATIVO", String(1), nullable=False, default="S")

    # Relacionamentos
    consultas = relationship("Consulta", back_populates="tipo")


# ============================================================================
# Tabela: CONSULTA
# Auditoria de todas as consultas realizadas
# ============================================================================


class Consulta(Base):
    """Model para tabela CONSULTA.

    Registra todas as consultas realizadas na API para auditoria.
    Cada consulta e vinculada a um token de acesso e um tipo.

    Attributes:
        id: Identificador unico da consulta (UUID)
        id_token: FK para TOKEN_ACESSO
        id_tipo_consulta: FK para TIPO_CONSULTA
        data_brasilia: Data/hora da consulta em horario de Brasilia
        data_inicio: Timestamp de inicio do processamento
        data_fim: Timestamp de fim do processamento
        parametros: JSON com parametros da requisicao
        ip_origem: IP de origem da requisicao
        status: Status da consulta (SUCESSO, ERRO, PARCIAL)
        mensagem_erro: Mensagem de erro (se houver)
    """

    __tablename__ = "CONSULTA"
    __table_args__ = (
        Index("IDX_CONSULTA_DATA_BRASILIA", "DATA_BRASILIA"),
        Index("IDX_CONSULTA_TOKEN", "ID_TOKEN"),
        Index("IDX_CONSULTA_STATUS", "STATUS"),
        {"schema": "RADAR_API"},
    )

    id = Column("ID", String(100), primary_key=True, default=lambda: str(uuid4()))
    id_token = Column(
        "ID_TOKEN",
        String(100),
        ForeignKey("RADAR_API.TOKEN_ACESSO.ID"),
        nullable=True,
    )
    id_tipo_consulta = Column(
        "ID_TIPO_CONSULTA",
        Integer,
        ForeignKey("RADAR_API.TIPO_CONSULTA.ID"),
        nullable=False,
    )
    data_brasilia = Column("DATA_BRASILIA", DateTime, nullable=False)
    data_inicio = Column("DATA_INICIO", DateTime, nullable=False, default=datetime.now)
    data_fim = Column("DATA_FIM", DateTime, nullable=True)
    parametros = Column("PARAMETROS", Text, nullable=True)
    ip_origem = Column("IP_ORIGEM", String(50), nullable=True)
    status = Column("STATUS", String(20), nullable=False, default="PROCESSANDO")
    mensagem_erro = Column("MENSAGEM_ERRO", Text, nullable=True)

    # Relacionamentos
    token = relationship("TokenAcesso", back_populates="consultas")
    tipo = relationship("TipoConsulta", back_populates="consultas")
    interrupcoes = relationship("InterrupcaoAtiva", back_populates="consulta")

    def finalizar_sucesso(self) -> None:
        """Marca a consulta como finalizada com sucesso."""
        self.data_fim = datetime.now()
        self.status = "SUCESSO"

    def finalizar_erro(self, mensagem: str) -> None:
        """Marca a consulta como finalizada com erro."""
        self.data_fim = datetime.now()
        self.status = "ERRO"
        self.mensagem_erro = mensagem


# ============================================================================
# Tabela: INTERRUPCAO_ATIVA
# Snapshot de interrupcoes para cada consulta (historico)
# ============================================================================


class InterrupcaoAtiva(Base):
    """Model para tabela INTERRUPCAO_ATIVA.

    Armazena um snapshot dos dados de interrupcao para cada consulta
    realizada. Permite auditoria e historico completo.

    Attributes:
        id: Identificador unico do registro
        id_consulta: FK para CONSULTA
        id_conjunto_uc: Identificador do conjunto de UCs
        id_municipio: Codigo IBGE do municipio (7 digitos)
        qtd_ucs_atendidas: Total de UCs atendidas no conjunto/municipio
        qtd_programada: UCs afetadas por interrupcoes programadas
        qtd_nao_programada: UCs afetadas por interrupcoes nao programadas
    """

    __tablename__ = "INTERRUPCAO_ATIVA"
    __table_args__ = (
        Index("IDX_INTERRUPCAO_CONSULTA", "ID_CONSULTA"),
        Index("IDX_INTERRUPCAO_MUNICIPIO", "ID_MUNICIPIO"),
        {"schema": "RADAR_API"},
    )

    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    id_consulta = Column(
        "ID_CONSULTA",
        String(100),
        ForeignKey("RADAR_API.CONSULTA.ID"),
        nullable=False,
    )
    id_conjunto_uc = Column("ID_CONJUNTO_UC", Integer, nullable=False)
    id_municipio = Column("ID_MUNICIPIO", Integer, nullable=False)
    qtd_ucs_atendidas = Column("QTD_UCS_ATENDIDAS", Integer, nullable=False, default=0)
    qtd_programada = Column("QTD_PROGRAMADA", Integer, nullable=False, default=0)
    qtd_nao_programada = Column("QTD_NAO_PROGRAMADA", Integer, nullable=False, default=0)

    # Relacionamentos
    consulta = relationship("Consulta", back_populates="interrupcoes")

    @property
    def total_interrupcoes(self) -> int:
        """Retorna o total de interrupcoes (programadas + nao programadas)."""
        return (self.qtd_programada or 0) + (self.qtd_nao_programada or 0)
