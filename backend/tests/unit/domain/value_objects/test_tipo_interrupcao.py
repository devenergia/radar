"""Testes TDD para Value Object TipoInterrupcao (RAD-117).

Testes unitarios para o Value Object TipoInterrupcao que representa
o tipo de interrupcao de fornecimento de energia.

Conforme especificacao ANEEL (Oficio Circular 14/2025-SFE):
- PROGRAMADA: quando existe PLAN_ID
- NAO_PROGRAMADA: quando nao existe PLAN_ID
"""

import pytest

from backend.shared.domain.value_objects.tipo_interrupcao import TipoInterrupcao


class TestTipoInterrupcao:
    """Testes para Value Object TipoInterrupcao."""

    class TestFromPlanId:
        """Testes do factory method from_plan_id()."""

        @pytest.mark.unit
        def test_deve_retornar_programada_quando_plan_id_existe(self) -> None:
            """Se PLAN_ID != None, interrupcao e programada."""
            # Arrange
            plan_id = 12345

            # Act
            tipo = TipoInterrupcao.from_plan_id(plan_id)

            # Assert
            assert tipo == TipoInterrupcao.PROGRAMADA

        @pytest.mark.unit
        def test_deve_retornar_nao_programada_quando_plan_id_none(self) -> None:
            """Se PLAN_ID == None, interrupcao e nao programada."""
            # Arrange
            plan_id = None

            # Act
            tipo = TipoInterrupcao.from_plan_id(plan_id)

            # Assert
            assert tipo == TipoInterrupcao.NAO_PROGRAMADA

        @pytest.mark.unit
        def test_deve_retornar_programada_quando_plan_id_zero(self) -> None:
            """PLAN_ID = 0 ainda e um valor valido (programada)."""
            # Arrange
            plan_id = 0

            # Act
            tipo = TipoInterrupcao.from_plan_id(plan_id)

            # Assert
            assert tipo == TipoInterrupcao.PROGRAMADA

        @pytest.mark.unit
        @pytest.mark.parametrize("plan_id", [1, 100, 99999, 1000000])
        def test_deve_retornar_programada_para_qualquer_plan_id_valido(
            self, plan_id: int
        ) -> None:
            """Qualquer PLAN_ID nao-nulo indica programada."""
            tipo = TipoInterrupcao.from_plan_id(plan_id)
            assert tipo == TipoInterrupcao.PROGRAMADA

    class TestFromCodigo:
        """Testes do factory method from_codigo()."""

        @pytest.mark.unit
        def test_codigo_1_retorna_programada(self) -> None:
            """Codigo 1 = PROGRAMADA (padrao ANEEL)."""
            tipo = TipoInterrupcao.from_codigo(1)

            assert tipo == TipoInterrupcao.PROGRAMADA

        @pytest.mark.unit
        def test_codigo_2_retorna_nao_programada(self) -> None:
            """Codigo 2 = NAO_PROGRAMADA (padrao ANEEL)."""
            tipo = TipoInterrupcao.from_codigo(2)

            assert tipo == TipoInterrupcao.NAO_PROGRAMADA

        @pytest.mark.unit
        def test_codigo_invalido_lanca_value_error(self) -> None:
            """Codigos diferentes de 1 ou 2 lancam erro."""
            with pytest.raises(ValueError) as exc_info:
                TipoInterrupcao.from_codigo(3)

            assert "invalido" in str(exc_info.value).lower()

        @pytest.mark.unit
        def test_codigo_zero_lanca_value_error(self) -> None:
            """Codigo 0 e invalido."""
            with pytest.raises(ValueError):
                TipoInterrupcao.from_codigo(0)

        @pytest.mark.unit
        def test_codigo_negativo_lanca_value_error(self) -> None:
            """Codigos negativos sao invalidos."""
            with pytest.raises(ValueError):
                TipoInterrupcao.from_codigo(-1)

    class TestCodigo:
        """Testes da property codigo."""

        @pytest.mark.unit
        def test_programada_retorna_1(self) -> None:
            """PROGRAMADA.codigo == 1."""
            assert TipoInterrupcao.PROGRAMADA.codigo == 1

        @pytest.mark.unit
        def test_nao_programada_retorna_2(self) -> None:
            """NAO_PROGRAMADA.codigo == 2."""
            assert TipoInterrupcao.NAO_PROGRAMADA.codigo == 2

    class TestIsProgramada:
        """Testes do metodo is_programada()."""

        @pytest.mark.unit
        def test_programada_deve_retornar_true(self) -> None:
            """TipoInterrupcao.PROGRAMADA.is_programada() == True."""
            assert TipoInterrupcao.PROGRAMADA.is_programada() is True

        @pytest.mark.unit
        def test_nao_programada_deve_retornar_false(self) -> None:
            """TipoInterrupcao.NAO_PROGRAMADA.is_programada() == False."""
            assert TipoInterrupcao.NAO_PROGRAMADA.is_programada() is False

    class TestIsNaoProgramada:
        """Testes do metodo is_nao_programada()."""

        @pytest.mark.unit
        def test_nao_programada_deve_retornar_true(self) -> None:
            """TipoInterrupcao.NAO_PROGRAMADA.is_nao_programada() == True."""
            assert TipoInterrupcao.NAO_PROGRAMADA.is_nao_programada() is True

        @pytest.mark.unit
        def test_programada_deve_retornar_false(self) -> None:
            """TipoInterrupcao.PROGRAMADA.is_nao_programada() == False."""
            assert TipoInterrupcao.PROGRAMADA.is_nao_programada() is False

    class TestEnumValues:
        """Testes dos valores do Enum."""

        @pytest.mark.unit
        def test_deve_ter_valor_programada(self) -> None:
            """Enum deve ter valor PROGRAMADA."""
            assert TipoInterrupcao.PROGRAMADA.value == "PROGRAMADA"

        @pytest.mark.unit
        def test_deve_ter_valor_nao_programada(self) -> None:
            """Enum deve ter valor NAO_PROGRAMADA."""
            assert TipoInterrupcao.NAO_PROGRAMADA.value == "NAO_PROGRAMADA"

        @pytest.mark.unit
        def test_deve_ter_apenas_dois_valores(self) -> None:
            """Enum deve ter exatamente 2 valores."""
            assert len(TipoInterrupcao) == 2

    class TestStrEnum:
        """Testes de heranca de str (para serializacao JSON)."""

        @pytest.mark.unit
        def test_enum_herda_de_str(self) -> None:
            """TipoInterrupcao deve ser instancia de str."""
            assert isinstance(TipoInterrupcao.PROGRAMADA, str)
            assert isinstance(TipoInterrupcao.NAO_PROGRAMADA, str)

        @pytest.mark.unit
        def test_pode_comparar_com_string(self) -> None:
            """Enum pode ser comparado diretamente com string."""
            assert TipoInterrupcao.PROGRAMADA == "PROGRAMADA"
            assert TipoInterrupcao.NAO_PROGRAMADA == "NAO_PROGRAMADA"

        @pytest.mark.unit
        def test_pode_ser_serializado_como_json(self) -> None:
            """Enum pode ser usado diretamente em JSON."""
            import json

            # Act
            json_str = json.dumps({"tipo": TipoInterrupcao.PROGRAMADA})

            # Assert
            assert json_str == '{"tipo": "PROGRAMADA"}'
