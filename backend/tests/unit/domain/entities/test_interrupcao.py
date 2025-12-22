"""Testes TDD para Entity Interrupcao (RAD-118).

Testes unitarios para a entidade Interrupcao que representa
um evento de interrupcao no fornecimento de energia.

Conforme especificacao ANEEL (Oficio Circular 14/2025-SFE):
- ideMunicipio: int de 7 digitos
- PROGRAMADA: quando existe PLAN_ID
- NAO_PROGRAMADA: quando nao existe PLAN_ID
"""

from datetime import datetime, timedelta

import pytest

from backend.shared.domain.entities.interrupcao import Interrupcao
from backend.shared.domain.value_objects.codigo_ibge import CodigoIBGE
from backend.shared.domain.value_objects.tipo_interrupcao import TipoInterrupcao


class TestInterrupcao:
    """Testes para entidade Interrupcao."""

    @pytest.fixture
    def municipio_boa_vista(self) -> CodigoIBGE:
        """Fixture para codigo IBGE de Boa Vista (int)."""
        return CodigoIBGE.create(1400100).value

    @pytest.fixture
    def data_inicio(self) -> datetime:
        """Fixture para data de inicio."""
        return datetime(2025, 1, 15, 10, 0, 0)

    class TestCreate:
        """Testes para factory method create()."""

        @pytest.fixture
        def municipio_boa_vista(self) -> CodigoIBGE:
            """Fixture para codigo IBGE de Boa Vista."""
            return CodigoIBGE.create(1400100).value

        @pytest.fixture
        def data_inicio(self) -> datetime:
            """Fixture para data de inicio."""
            return datetime(2025, 1, 15, 10, 0, 0)

        @pytest.mark.unit
        def test_deve_criar_interrupcao_com_dados_validos(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Criacao com dados validos retorna sucesso."""
            result = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            )

            assert result.is_success
            assert result.value.id == 12345
            assert result.value.tipo == TipoInterrupcao.PROGRAMADA
            assert result.value.municipio.valor == 1400100  # int conforme ANEEL
            assert result.value.conjunto == 1
            assert result.value.ucs_afetadas == 150

        @pytest.mark.unit
        def test_deve_rejeitar_ucs_afetadas_negativas(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """UCs afetadas negativas retorna erro."""
            result = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=-10,
                data_inicio=data_inicio,
            )

            assert result.is_failure
            assert "negativ" in result.error.lower()

        @pytest.mark.unit
        def test_deve_rejeitar_conjunto_negativo(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Conjunto negativo retorna erro."""
            result = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=-1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            )

            assert result.is_failure
            assert "conjunto" in result.error.lower()

        @pytest.mark.unit
        def test_deve_aceitar_ucs_afetadas_zero(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """UCs afetadas pode ser zero."""
            result = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=0,
                data_inicio=data_inicio,
            )

            assert result.is_success

        @pytest.mark.unit
        def test_deve_aceitar_conjunto_zero(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Conjunto zero e valido."""
            result = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=0,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            )

            assert result.is_success

        @pytest.mark.unit
        def test_deve_rejeitar_data_fim_anterior_a_data_inicio(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Data fim anterior a data inicio retorna erro."""
            result = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
                data_fim=data_inicio - timedelta(hours=1),
            )

            assert result.is_failure
            assert "data" in result.error.lower()

        @pytest.mark.unit
        def test_deve_aceitar_data_fim_igual_a_data_inicio(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Data fim igual a data inicio e valido."""
            result = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
                data_fim=data_inicio,
            )

            assert result.is_success

        @pytest.mark.unit
        def test_deve_criar_interrupcao_sem_data_fim(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Interrupcao ativa pode nao ter data_fim."""
            result = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            )

            assert result.is_success
            assert result.value.data_fim is None

    class TestIsAtiva:
        """Testes para metodo is_ativa()."""

        @pytest.fixture
        def municipio_boa_vista(self) -> CodigoIBGE:
            """Fixture para codigo IBGE de Boa Vista."""
            return CodigoIBGE.create(1400100).value

        @pytest.fixture
        def data_inicio(self) -> datetime:
            """Fixture para data de inicio."""
            return datetime(2025, 1, 15, 10, 0, 0)

        @pytest.mark.unit
        def test_deve_retornar_true_quando_data_fim_e_none(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Interrupcao sem data_fim e ativa."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            assert interrupcao.is_ativa() is True

        @pytest.mark.unit
        def test_deve_retornar_false_quando_data_fim_existe(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Interrupcao com data_fim nao e ativa."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
                data_fim=data_inicio + timedelta(hours=2),
            ).value

            assert interrupcao.is_ativa() is False

    class TestIsProgramada:
        """Testes para metodo is_programada()."""

        @pytest.fixture
        def municipio_boa_vista(self) -> CodigoIBGE:
            """Fixture para codigo IBGE de Boa Vista."""
            return CodigoIBGE.create(1400100).value

        @pytest.fixture
        def data_inicio(self) -> datetime:
            """Fixture para data de inicio."""
            return datetime(2025, 1, 15, 10, 0, 0)

        @pytest.mark.unit
        def test_deve_retornar_true_para_tipo_programada(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Interrupcao PROGRAMADA retorna True."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            assert interrupcao.is_programada() is True

        @pytest.mark.unit
        def test_deve_retornar_false_para_tipo_nao_programada(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Interrupcao NAO_PROGRAMADA retorna False."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.NAO_PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            assert interrupcao.is_programada() is False

    class TestIsNaoProgramada:
        """Testes para metodo is_nao_programada()."""

        @pytest.fixture
        def municipio_boa_vista(self) -> CodigoIBGE:
            """Fixture para codigo IBGE de Boa Vista."""
            return CodigoIBGE.create(1400100).value

        @pytest.fixture
        def data_inicio(self) -> datetime:
            """Fixture para data de inicio."""
            return datetime(2025, 1, 15, 10, 0, 0)

        @pytest.mark.unit
        def test_deve_retornar_true_para_tipo_nao_programada(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Interrupcao NAO_PROGRAMADA retorna True."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.NAO_PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            assert interrupcao.is_nao_programada() is True

        @pytest.mark.unit
        def test_deve_retornar_false_para_tipo_programada(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Interrupcao PROGRAMADA retorna False."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            assert interrupcao.is_nao_programada() is False

    class TestGetDuracaoMinutos:
        """Testes para metodo get_duracao_minutos()."""

        @pytest.fixture
        def municipio_boa_vista(self) -> CodigoIBGE:
            """Fixture para codigo IBGE de Boa Vista."""
            return CodigoIBGE.create(1400100).value

        @pytest.fixture
        def data_inicio(self) -> datetime:
            """Fixture para data de inicio."""
            return datetime(2025, 1, 15, 10, 0, 0)

        @pytest.mark.unit
        def test_deve_retornar_none_para_interrupcao_ativa(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Interrupcao sem data_fim retorna None."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            assert interrupcao.get_duracao_minutos() is None

        @pytest.mark.unit
        def test_deve_calcular_duracao_em_minutos(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Calcula corretamente duracao em minutos."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
                data_fim=data_inicio + timedelta(hours=2, minutes=30),
            ).value

            duracao = interrupcao.get_duracao_minutos()

            assert duracao == 150  # 2h30 = 150 minutos

        @pytest.mark.unit
        def test_deve_retornar_zero_para_mesma_data(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Data inicio igual a data fim retorna 0."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
                data_fim=data_inicio,
            ).value

            assert interrupcao.get_duracao_minutos() == 0

    class TestToDict:
        """Testes para metodo to_dict()."""

        @pytest.fixture
        def municipio_boa_vista(self) -> CodigoIBGE:
            """Fixture para codigo IBGE de Boa Vista."""
            return CodigoIBGE.create(1400100).value

        @pytest.fixture
        def data_inicio(self) -> datetime:
            """Fixture para data de inicio."""
            return datetime(2025, 1, 15, 10, 0, 0)

        @pytest.mark.unit
        def test_deve_serializar_para_dicionario(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """to_dict() retorna dicionario com todos os campos."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            d = interrupcao.to_dict()

            assert d["id"] == 12345
            assert d["tipo"] == "PROGRAMADA"
            assert d["municipio"] == 1400100  # int conforme ANEEL
            assert d["conjunto"] == 1
            assert d["ucs_afetadas"] == 150
            assert d["is_ativa"] is True

        @pytest.mark.unit
        def test_deve_incluir_data_fim_quando_existe(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """to_dict() inclui data_fim quando existe."""
            data_fim = data_inicio + timedelta(hours=2)
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
                data_fim=data_fim,
            ).value

            d = interrupcao.to_dict()

            assert d["data_fim"] == data_fim.isoformat()
            assert d["is_ativa"] is False

        @pytest.mark.unit
        def test_deve_retornar_data_fim_none_quando_ativa(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """to_dict() retorna data_fim None quando ativa."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            d = interrupcao.to_dict()

            assert d["data_fim"] is None

    class TestEquality:
        """Testes para igualdade e hash."""

        @pytest.fixture
        def municipio_boa_vista(self) -> CodigoIBGE:
            """Fixture para codigo IBGE de Boa Vista."""
            return CodigoIBGE.create(1400100).value

        @pytest.fixture
        def data_inicio(self) -> datetime:
            """Fixture para data de inicio."""
            return datetime(2025, 1, 15, 10, 0, 0)

        @pytest.mark.unit
        def test_interrupcoes_com_mesmo_id_sao_iguais(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Igualdade baseada em ID (frozen dataclass)."""
            int1 = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            int2 = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            assert int1 == int2

        @pytest.mark.unit
        def test_interrupcoes_com_ids_diferentes_sao_diferentes(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Interrupcoes com IDs diferentes nao sao iguais."""
            int1 = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            int2 = Interrupcao.create(
                id=99999,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            assert int1 != int2

        @pytest.mark.unit
        def test_hash_permite_uso_em_set(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Hash permite uso em sets e dicts."""
            int1 = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            int2 = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            # Pode ser usado em set
            s = {int1, int2}
            assert len(s) == 1

        @pytest.mark.unit
        def test_pode_ser_usado_como_chave_dict(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Pode ser usado como chave de dicionario."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            d = {interrupcao: "teste"}
            assert d[interrupcao] == "teste"

    class TestImutabilidade:
        """Testes de imutabilidade (frozen dataclass)."""

        @pytest.fixture
        def municipio_boa_vista(self) -> CodigoIBGE:
            """Fixture para codigo IBGE de Boa Vista."""
            return CodigoIBGE.create(1400100).value

        @pytest.fixture
        def data_inicio(self) -> datetime:
            """Fixture para data de inicio."""
            return datetime(2025, 1, 15, 10, 0, 0)

        @pytest.mark.unit
        def test_nao_deve_permitir_alteracao_de_atributos(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """Entity deve ser imutavel."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            with pytest.raises(AttributeError):
                interrupcao.ucs_afetadas = 999  # type: ignore

        @pytest.mark.unit
        def test_nao_deve_permitir_alteracao_de_id(
            self, municipio_boa_vista: CodigoIBGE, data_inicio: datetime
        ) -> None:
            """ID nao pode ser alterado."""
            interrupcao = Interrupcao.create(
                id=12345,
                tipo=TipoInterrupcao.PROGRAMADA,
                municipio=municipio_boa_vista,
                conjunto=1,
                ucs_afetadas=150,
                data_inicio=data_inicio,
            ).value

            with pytest.raises(AttributeError):
                interrupcao.id = 99999  # type: ignore
