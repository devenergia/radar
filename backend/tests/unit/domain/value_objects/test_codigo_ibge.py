"""Testes TDD para Value Object CodigoIBGE (RAD-117).

Testes unitarios para o Value Object CodigoIBGE que representa
codigos IBGE de municipios de Roraima.

Conforme especificacao ANEEL: ideMunicipio deve ser int de 7 digitos.
"""

import pytest

from backend.shared.domain.value_objects.codigo_ibge import CodigoIBGE


class TestCodigoIBGE:
    """Testes para Value Object CodigoIBGE."""

    class TestCreate:
        """Testes do factory method create(int)."""

        @pytest.mark.unit
        def test_deve_criar_codigo_ibge_valido_para_boa_vista(self) -> None:
            """Codigo 1400100 (Boa Vista) deve ser valido."""
            # Arrange
            codigo_bv = 1400100

            # Act
            result = CodigoIBGE.create(codigo_bv)

            # Assert
            assert result.is_success
            assert result.value.valor == 1400100

        @pytest.mark.unit
        @pytest.mark.parametrize(
            "codigo,nome",
            [
                (1400050, "Alto Alegre"),
                (1400027, "Amajari"),
                (1400100, "Boa Vista"),
                (1400159, "Bonfim"),
                (1400175, "Canta"),
                (1400209, "Caracarai"),
                (1400233, "Caroebe"),
                (1400282, "Iracema"),
                (1400308, "Mucajai"),
                (1400407, "Normandia"),
                (1400456, "Pacaraima"),
                (1400472, "Rorainopolis"),
                (1400506, "Sao Joao da Baliza"),
                (1400605, "Sao Luiz"),
                (1400704, "Uiramuta"),
            ],
        )
        def test_deve_aceitar_todos_municipios_roraima(
            self, codigo: int, nome: str
        ) -> None:
            """Todos os 15 municipios de Roraima devem ser aceitos."""
            result = CodigoIBGE.create(codigo)
            assert result.is_success, f"Falhou para {nome} ({codigo})"

        @pytest.mark.unit
        def test_deve_rejeitar_codigo_com_menos_de_7_digitos(self) -> None:
            """Codigo com menos de 7 digitos deve ser rejeitado (< 1000000)."""
            # Arrange
            codigo_invalido = 140010  # 6 digitos

            # Act
            result = CodigoIBGE.create(codigo_invalido)

            # Assert
            assert result.is_failure
            assert "invalido" in result.error.lower()

        @pytest.mark.unit
        def test_deve_rejeitar_codigo_com_mais_de_7_digitos(self) -> None:
            """Codigo com mais de 7 digitos deve ser rejeitado (> 9999999)."""
            # Arrange
            codigo_invalido = 14001001  # 8 digitos

            # Act
            result = CodigoIBGE.create(codigo_invalido)

            # Assert
            assert result.is_failure

        @pytest.mark.unit
        def test_deve_rejeitar_codigo_de_outro_estado(self) -> None:
            """Codigo de outro estado deve ser rejeitado."""
            # Arrange
            codigo_sp = 3550308  # Sao Paulo

            # Act
            result = CodigoIBGE.create(codigo_sp)

            # Assert
            assert result.is_failure
            assert "Roraima" in result.error

        @pytest.mark.unit
        def test_deve_rejeitar_codigo_amazonas(self) -> None:
            """Codigo do Amazonas (13) deve ser rejeitado."""
            # Arrange
            codigo_am = 1300000

            # Act
            result = CodigoIBGE.create(codigo_am)

            # Assert
            assert result.is_failure
            assert "Roraima" in result.error

        @pytest.mark.unit
        def test_deve_rejeitar_codigo_roraima_inexistente(self) -> None:
            """Codigo com prefixo 14 mas inexistente deve ser rejeitado."""
            # Arrange
            codigo_inexistente = 1499999

            # Act
            result = CodigoIBGE.create(codigo_inexistente)

            # Assert
            assert result.is_failure
            assert "Roraima" in result.error

    class TestCreateUnsafe:
        """Testes do factory method create_unsafe(int)."""

        @pytest.mark.unit
        def test_deve_criar_codigo_sem_validacao(self) -> None:
            """create_unsafe() cria sem validar (para dados vindos do banco)."""
            # Act
            ibge = CodigoIBGE.create_unsafe(1400100)

            # Assert
            assert ibge.valor == 1400100

        @pytest.mark.unit
        def test_create_unsafe_aceita_qualquer_valor(self) -> None:
            """create_unsafe() nao valida - aceita qualquer int."""
            # Act - valor invalido mas aceito
            ibge = CodigoIBGE.create_unsafe(9999999)

            # Assert
            assert ibge.valor == 9999999

    class TestGetAllRoraimaCodes:
        """Testes do metodo get_all_roraima_codes()."""

        @pytest.mark.unit
        def test_deve_retornar_15_municipios(self) -> None:
            """Roraima tem exatamente 15 municipios."""
            codes = CodigoIBGE.get_all_roraima_codes()

            assert len(codes) == 15

        @pytest.mark.unit
        def test_deve_retornar_tupla_de_inteiros(self) -> None:
            """Retorna tuple[int, ...] (imutavel e tipado)."""
            codes = CodigoIBGE.get_all_roraima_codes()

            assert isinstance(codes, tuple)
            assert all(isinstance(c, int) for c in codes)

        @pytest.mark.unit
        def test_deve_incluir_boa_vista(self) -> None:
            """Lista deve incluir Boa Vista (1400100)."""
            codes = CodigoIBGE.get_all_roraima_codes()

            assert 1400100 in codes

    class TestEquals:
        """Testes de igualdade (Value Object)."""

        @pytest.mark.unit
        def test_deve_ser_igual_quando_valores_iguais(self) -> None:
            """Dois CodigoIBGE com mesmo valor devem ser iguais."""
            # Arrange
            ibge1 = CodigoIBGE.create(1400100).value
            ibge2 = CodigoIBGE.create(1400100).value

            # Assert
            assert ibge1 == ibge2

        @pytest.mark.unit
        def test_deve_ser_diferente_quando_valores_diferentes(self) -> None:
            """Dois CodigoIBGE com valores diferentes nao devem ser iguais."""
            # Arrange
            ibge1 = CodigoIBGE.create(1400100).value
            ibge2 = CodigoIBGE.create(1400050).value

            # Assert
            assert ibge1 != ibge2

        @pytest.mark.unit
        def test_deve_ter_mesmo_hash_quando_valores_iguais(self) -> None:
            """CodigoIBGE iguais devem ter mesmo hash (para uso em sets/dicts)."""
            # Arrange
            ibge1 = CodigoIBGE.create(1400100).value
            ibge2 = CodigoIBGE.create(1400100).value

            # Assert
            assert hash(ibge1) == hash(ibge2)

        @pytest.mark.unit
        def test_pode_ser_usado_em_set(self) -> None:
            """CodigoIBGE pode ser usado em set (hashable)."""
            # Arrange
            ibge1 = CodigoIBGE.create(1400100).value
            ibge2 = CodigoIBGE.create(1400100).value
            ibge3 = CodigoIBGE.create(1400050).value

            # Act
            s = {ibge1, ibge2, ibge3}

            # Assert - ibge1 e ibge2 sao iguais, entao set tem 2 elementos
            assert len(s) == 2

        @pytest.mark.unit
        def test_pode_ser_usado_como_chave_dict(self) -> None:
            """CodigoIBGE pode ser chave de dicionario."""
            # Arrange
            ibge = CodigoIBGE.create(1400100).value

            # Act
            d = {ibge: "Boa Vista"}

            # Assert
            assert d[ibge] == "Boa Vista"

    class TestImutabilidade:
        """Testes de imutabilidade (frozen dataclass)."""

        @pytest.mark.unit
        def test_nao_deve_permitir_alteracao_de_valor(self) -> None:
            """Value Object deve ser imutavel."""
            # Arrange
            ibge = CodigoIBGE.create(1400100).value

            # Act & Assert
            with pytest.raises(AttributeError):
                ibge.valor = 1400050  # type: ignore

    class TestStringRepresentation:
        """Testes de representacao string/int."""

        @pytest.mark.unit
        def test_str_retorna_valor_como_string(self) -> None:
            """__str__ retorna o valor como string."""
            ibge = CodigoIBGE.create(1400100).value

            assert str(ibge) == "1400100"

        @pytest.mark.unit
        def test_int_retorna_valor_como_inteiro(self) -> None:
            """__int__ retorna o valor como int."""
            ibge = CodigoIBGE.create(1400100).value

            assert int(ibge) == 1400100
