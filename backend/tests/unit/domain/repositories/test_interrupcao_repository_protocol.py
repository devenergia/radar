"""Testes do Protocol InterrupcaoRepository.

NOTA: O Protocol usa metodos SINCRONOS (nao async) conforme padrao
do projeto de referencia (MJQEE-GFUZ).
"""

import ast
from datetime import datetime
from pathlib import Path
from typing import Protocol
from unittest.mock import MagicMock

import pytest

from backend.shared.domain.entities.interrupcao import Interrupcao
from backend.shared.domain.repositories.interrupcao_repository import (
    InterrupcaoRepository,
)
from backend.shared.domain.value_objects.codigo_ibge import CodigoIBGE


@pytest.mark.unit
class TestInterrupcaoRepositoryProtocol:
    """Testes para verificar que InterrupcaoRepository e um Protocol valido."""

    def test_deve_ser_um_protocol(self) -> None:
        """Verifica que InterrupcaoRepository e um Protocol."""
        assert issubclass(InterrupcaoRepository, Protocol)

    def test_protocol_deve_ter_metodo_buscar_ativas(self) -> None:
        """Verifica que Protocol tem metodo buscar_ativas."""
        assert hasattr(InterrupcaoRepository, "buscar_ativas")

    def test_protocol_deve_ter_metodo_buscar_por_municipio(self) -> None:
        """Verifica que Protocol tem metodo buscar_por_municipio."""
        assert hasattr(InterrupcaoRepository, "buscar_por_municipio")

    def test_protocol_deve_ter_metodo_buscar_por_conjunto(self) -> None:
        """Verifica que Protocol tem metodo buscar_por_conjunto."""
        assert hasattr(InterrupcaoRepository, "buscar_por_conjunto")

    def test_protocol_deve_ter_metodo_buscar_historico(self) -> None:
        """Verifica que Protocol tem metodo buscar_historico."""
        assert hasattr(InterrupcaoRepository, "buscar_historico")


@pytest.mark.unit
class TestInterrupcaoRepositoryArquitetura:
    """Testes para validar arquitetura Clean do Protocol."""

    def test_protocol_nao_deve_importar_sqlalchemy(self) -> None:
        """Protocol nao deve importar SQLAlchemy (violaria Clean Architecture)."""
        file_path = Path(
            "backend/shared/domain/repositories/interrupcao_repository.py"
        )
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        forbidden_modules = ["sqlalchemy", "oracledb", "fastapi", "pydantic"]

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_root = alias.name.split(".")[0]
                    assert module_root not in forbidden_modules, (
                        f"Protocol importa {alias.name} - viola Clean Architecture"
                    )
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    module_root = node.module.split(".")[0]
                    assert module_root not in forbidden_modules, (
                        f"Protocol importa de {node.module} - viola Clean Architecture"
                    )

    def test_protocol_deve_estar_no_dominio(self) -> None:
        """Protocol deve estar em shared/domain/repositories/."""
        file_path = Path(
            "backend/shared/domain/repositories/interrupcao_repository.py"
        )
        assert file_path.exists(), (
            f"Protocol deve estar em {file_path}"
        )


@pytest.mark.unit
class TestInterrupcaoRepositoryContrato:
    """Testes para verificar contrato do Protocol via mock.

    NOTA: Metodos sao SINCRONOS (nao async) conforme padrao do projeto.
    """

    @pytest.fixture
    def mock_repository(self) -> MagicMock:
        """Cria mock que implementa o Protocol."""
        mock = MagicMock(spec=InterrupcaoRepository)
        return mock

    def test_buscar_ativas_deve_retornar_lista_de_interrupcoes(
        self,
        mock_repository: MagicMock,
        interrupcao_programada: Interrupcao,
    ) -> None:
        """buscar_ativas() deve retornar list[Interrupcao]."""
        mock_repository.buscar_ativas.return_value = [interrupcao_programada]

        resultado = mock_repository.buscar_ativas()

        assert isinstance(resultado, list)
        assert len(resultado) == 1
        assert isinstance(resultado[0], Interrupcao)

    def test_buscar_por_municipio_deve_aceitar_codigo_ibge(
        self,
        mock_repository: MagicMock,
        codigo_ibge_boa_vista: CodigoIBGE,
        interrupcao_programada: Interrupcao,
    ) -> None:
        """buscar_por_municipio() deve aceitar CodigoIBGE como parametro."""
        mock_repository.buscar_por_municipio.return_value = [interrupcao_programada]

        resultado = mock_repository.buscar_por_municipio(codigo_ibge_boa_vista)

        mock_repository.buscar_por_municipio.assert_called_once_with(
            codigo_ibge_boa_vista
        )
        assert isinstance(resultado, list)

    def test_buscar_por_conjunto_deve_aceitar_id_conjunto(
        self,
        mock_repository: MagicMock,
        interrupcao_programada: Interrupcao,
    ) -> None:
        """buscar_por_conjunto() deve aceitar int como parametro."""
        mock_repository.buscar_por_conjunto.return_value = [interrupcao_programada]

        resultado = mock_repository.buscar_por_conjunto(1)

        mock_repository.buscar_por_conjunto.assert_called_once_with(1)
        assert isinstance(resultado, list)

    def test_buscar_historico_deve_aceitar_periodo(
        self,
        mock_repository: MagicMock,
        interrupcao_finalizada: Interrupcao,
    ) -> None:
        """buscar_historico() deve aceitar data_inicio e data_fim."""
        mock_repository.buscar_historico.return_value = [interrupcao_finalizada]

        data_inicio = datetime(2025, 12, 18, 0, 0, 0)
        data_fim = datetime(2025, 12, 19, 0, 0, 0)

        resultado = mock_repository.buscar_historico(data_inicio, data_fim)

        mock_repository.buscar_historico.assert_called_once_with(data_inicio, data_fim)
        assert isinstance(resultado, list)

    def test_buscar_ativas_deve_retornar_lista_vazia_quando_nao_ha_interrupcoes(
        self,
        mock_repository: MagicMock,
    ) -> None:
        """buscar_ativas() deve retornar lista vazia quando nao ha interrupcoes."""
        mock_repository.buscar_ativas.return_value = []

        resultado = mock_repository.buscar_ativas()

        assert resultado == []
