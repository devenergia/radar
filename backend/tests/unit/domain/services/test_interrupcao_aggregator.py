"""Testes para InterrupcaoAggregatorService.

TDD - Estes testes devem ser escritos ANTES da implementacao.
"""

from datetime import datetime

import pytest

from backend.shared.domain.entities.interrupcao import Interrupcao
from backend.shared.domain.services.interrupcao_aggregator import (
    InterrupcaoAgregada,
    InterrupcaoAggregatorService,
)
from backend.shared.domain.value_objects.codigo_ibge import CodigoIBGE
from backend.shared.domain.value_objects.tipo_interrupcao import TipoInterrupcao


def criar_interrupcao(
    id: int,
    municipio: CodigoIBGE,
    conjunto: int,
    tipo: TipoInterrupcao,
    ucs: int,
) -> Interrupcao:
    """Helper para criar interrupcao de teste."""
    result = Interrupcao.create(
        id=id,
        tipo=tipo,
        municipio=municipio,
        conjunto=conjunto,
        ucs_afetadas=ucs,
        data_inicio=datetime.now(),
        data_fim=None,
    )
    return result.value


@pytest.mark.unit
class TestInterrupcaoAgregada:
    """Testes para dataclass InterrupcaoAgregada."""

    @pytest.fixture
    def codigo_ibge_boa_vista(self) -> CodigoIBGE:
        return CodigoIBGE.create(1400100).value

    def test_deve_ser_frozen(self, codigo_ibge_boa_vista: CodigoIBGE) -> None:
        """Agregado deve ser imutavel."""
        agregado = InterrupcaoAgregada(
            id_conjunto=1,
            municipio=codigo_ibge_boa_vista,
            qtd_ucs_atendidas=10000,
            qtd_programada=100,
            qtd_nao_programada=50,
        )

        with pytest.raises(AttributeError):
            agregado.qtd_programada = 999  # type: ignore

    def test_total_interrupcoes_soma_programada_e_nao_programada(
        self, codigo_ibge_boa_vista: CodigoIBGE
    ) -> None:
        """total_interrupcoes soma programada + nao programada."""
        agregado = InterrupcaoAgregada(
            id_conjunto=1,
            municipio=codigo_ibge_boa_vista,
            qtd_ucs_atendidas=10000,
            qtd_programada=100,
            qtd_nao_programada=50,
        )

        assert agregado.total_interrupcoes == 150

    def test_has_interrupcoes_retorna_true_quando_ha_interrupcoes(
        self, codigo_ibge_boa_vista: CodigoIBGE
    ) -> None:
        """has_interrupcoes retorna True quando ha interrupcoes."""
        agregado = InterrupcaoAgregada(
            id_conjunto=1,
            municipio=codigo_ibge_boa_vista,
            qtd_ucs_atendidas=10000,
            qtd_programada=100,
            qtd_nao_programada=0,
        )

        assert agregado.has_interrupcoes() is True

    def test_has_interrupcoes_retorna_false_quando_nao_ha_interrupcoes(
        self, codigo_ibge_boa_vista: CodigoIBGE
    ) -> None:
        """has_interrupcoes retorna False quando nao ha interrupcoes."""
        agregado = InterrupcaoAgregada(
            id_conjunto=1,
            municipio=codigo_ibge_boa_vista,
            qtd_ucs_atendidas=10000,
            qtd_programada=0,
            qtd_nao_programada=0,
        )

        assert agregado.has_interrupcoes() is False


@pytest.mark.unit
class TestInterrupcaoAggregatorService:
    """Testes para servico de agregacao."""

    @pytest.fixture
    def service(self) -> InterrupcaoAggregatorService:
        return InterrupcaoAggregatorService()

    @pytest.fixture
    def boa_vista(self) -> CodigoIBGE:
        return CodigoIBGE.create(1400100).value

    @pytest.fixture
    def caracarai(self) -> CodigoIBGE:
        return CodigoIBGE.create(1400209).value

    def test_deve_retornar_lista_vazia_para_entrada_vazia(
        self, service: InterrupcaoAggregatorService
    ) -> None:
        """Lista vazia de entrada retorna lista vazia."""
        resultado = service.agregar([])

        assert resultado == []

    def test_deve_agregar_por_municipio_e_conjunto(
        self,
        service: InterrupcaoAggregatorService,
        boa_vista: CodigoIBGE,
    ) -> None:
        """Agrega interrupcoes do mesmo municipio/conjunto."""
        interrupcoes = [
            criar_interrupcao(1, boa_vista, 1, TipoInterrupcao.PROGRAMADA, 50),
            criar_interrupcao(2, boa_vista, 1, TipoInterrupcao.PROGRAMADA, 30),
        ]

        resultado = service.agregar(interrupcoes)

        assert len(resultado) == 1
        assert resultado[0].qtd_programada == 80

    def test_deve_separar_por_tipo_programada_e_nao_programada(
        self,
        service: InterrupcaoAggregatorService,
        boa_vista: CodigoIBGE,
    ) -> None:
        """Separa contagem por tipo de interrupcao."""
        interrupcoes = [
            criar_interrupcao(1, boa_vista, 1, TipoInterrupcao.PROGRAMADA, 50),
            criar_interrupcao(2, boa_vista, 1, TipoInterrupcao.NAO_PROGRAMADA, 30),
        ]

        resultado = service.agregar(interrupcoes)

        assert len(resultado) == 1
        assert resultado[0].qtd_programada == 50
        assert resultado[0].qtd_nao_programada == 30

    def test_deve_separar_por_conjunto_diferente(
        self,
        service: InterrupcaoAggregatorService,
        boa_vista: CodigoIBGE,
    ) -> None:
        """Conjuntos diferentes geram agregados separados."""
        interrupcoes = [
            criar_interrupcao(1, boa_vista, 1, TipoInterrupcao.PROGRAMADA, 50),
            criar_interrupcao(2, boa_vista, 2, TipoInterrupcao.PROGRAMADA, 30),
        ]

        resultado = service.agregar(interrupcoes)

        assert len(resultado) == 2

    def test_deve_separar_por_municipio_diferente(
        self,
        service: InterrupcaoAggregatorService,
        boa_vista: CodigoIBGE,
        caracarai: CodigoIBGE,
    ) -> None:
        """Municipios diferentes geram agregados separados."""
        interrupcoes = [
            criar_interrupcao(1, boa_vista, 1, TipoInterrupcao.PROGRAMADA, 50),
            criar_interrupcao(2, caracarai, 1, TipoInterrupcao.PROGRAMADA, 30),
        ]

        resultado = service.agregar(interrupcoes)

        assert len(resultado) == 2

    def test_deve_incluir_dados_de_universo_quando_fornecido(
        self,
        service: InterrupcaoAggregatorService,
        boa_vista: CodigoIBGE,
    ) -> None:
        """Inclui qtd_ucs_atendidas do universo."""
        interrupcoes = [
            criar_interrupcao(1, boa_vista, 1, TipoInterrupcao.PROGRAMADA, 50),
        ]
        universo = {(1, 1400100): 10000}

        resultado = service.agregar(interrupcoes, universo)

        assert resultado[0].qtd_ucs_atendidas == 10000

    def test_deve_usar_zero_quando_universo_nao_tem_dados(
        self,
        service: InterrupcaoAggregatorService,
        boa_vista: CodigoIBGE,
    ) -> None:
        """Usa 0 quando universo nao tem dados para combinacao."""
        interrupcoes = [
            criar_interrupcao(1, boa_vista, 1, TipoInterrupcao.PROGRAMADA, 50),
        ]
        universo: dict[tuple[int, int], int] = {}  # Vazio

        resultado = service.agregar(interrupcoes, universo)

        assert resultado[0].qtd_ucs_atendidas == 0

    def test_deve_agregar_cenario_completo(
        self,
        service: InterrupcaoAggregatorService,
        boa_vista: CodigoIBGE,
        caracarai: CodigoIBGE,
    ) -> None:
        """Cenario completo: multiplas interrupcoes, municipios e conjuntos."""
        interrupcoes = [
            # Boa Vista, Conjunto 1: 50 + 30 = 80 programadas
            criar_interrupcao(1, boa_vista, 1, TipoInterrupcao.PROGRAMADA, 50),
            criar_interrupcao(2, boa_vista, 1, TipoInterrupcao.PROGRAMADA, 30),
            # Boa Vista, Conjunto 1: 20 nao programadas
            criar_interrupcao(3, boa_vista, 1, TipoInterrupcao.NAO_PROGRAMADA, 20),
            # Boa Vista, Conjunto 2: 100 programadas
            criar_interrupcao(4, boa_vista, 2, TipoInterrupcao.PROGRAMADA, 100),
            # Caracarai, Conjunto 1: 40 nao programadas
            criar_interrupcao(5, caracarai, 1, TipoInterrupcao.NAO_PROGRAMADA, 40),
        ]
        universo = {
            (1, 1400100): 5000,  # BV, Conj 1
            (2, 1400100): 3000,  # BV, Conj 2
            (1, 1400209): 2000,  # Caracarai, Conj 1
        }

        resultado = service.agregar(interrupcoes, universo)

        assert len(resultado) == 3

        # Encontrar cada agregado
        bv_conj1 = next(
            r for r in resultado if r.id_conjunto == 1 and r.municipio.valor == 1400100
        )
        bv_conj2 = next(
            r for r in resultado if r.id_conjunto == 2 and r.municipio.valor == 1400100
        )
        car_conj1 = next(
            r for r in resultado if r.id_conjunto == 1 and r.municipio.valor == 1400209
        )

        assert bv_conj1.qtd_programada == 80
        assert bv_conj1.qtd_nao_programada == 20
        assert bv_conj1.qtd_ucs_atendidas == 5000

        assert bv_conj2.qtd_programada == 100
        assert bv_conj2.qtd_nao_programada == 0
        assert bv_conj2.qtd_ucs_atendidas == 3000

        assert car_conj1.qtd_programada == 0
        assert car_conj1.qtd_nao_programada == 40
        assert car_conj1.qtd_ucs_atendidas == 2000


@pytest.mark.unit
class TestInterrupcaoAggregatorServiceAgregarPorMunicipio:
    """Testes para metodo agregar_por_municipio."""

    @pytest.fixture
    def service(self) -> InterrupcaoAggregatorService:
        return InterrupcaoAggregatorService()

    @pytest.fixture
    def boa_vista(self) -> CodigoIBGE:
        return CodigoIBGE.create(1400100).value

    @pytest.fixture
    def caracarai(self) -> CodigoIBGE:
        return CodigoIBGE.create(1400209).value

    def test_deve_retornar_dict_vazio_para_entrada_vazia(
        self, service: InterrupcaoAggregatorService
    ) -> None:
        """Lista vazia retorna dict vazio."""
        resultado = service.agregar_por_municipio([])

        assert resultado == {}

    def test_deve_agregar_apenas_por_municipio_ignorando_conjunto(
        self,
        service: InterrupcaoAggregatorService,
        boa_vista: CodigoIBGE,
    ) -> None:
        """Agrega por municipio independente do conjunto."""
        interrupcoes = [
            criar_interrupcao(1, boa_vista, 1, TipoInterrupcao.PROGRAMADA, 50),
            criar_interrupcao(2, boa_vista, 2, TipoInterrupcao.PROGRAMADA, 30),
        ]

        resultado = service.agregar_por_municipio(interrupcoes)

        assert len(resultado) == 1
        assert resultado[1400100]["programada"] == 80

    def test_deve_separar_por_tipo_e_calcular_total(
        self,
        service: InterrupcaoAggregatorService,
        boa_vista: CodigoIBGE,
    ) -> None:
        """Separa por tipo e calcula total de UCs."""
        interrupcoes = [
            criar_interrupcao(1, boa_vista, 1, TipoInterrupcao.PROGRAMADA, 50),
            criar_interrupcao(2, boa_vista, 1, TipoInterrupcao.NAO_PROGRAMADA, 30),
        ]

        resultado = service.agregar_por_municipio(interrupcoes)

        assert resultado[1400100]["programada"] == 50
        assert resultado[1400100]["nao_programada"] == 30
        assert resultado[1400100]["total_ucs"] == 80

    def test_deve_separar_por_municipio(
        self,
        service: InterrupcaoAggregatorService,
        boa_vista: CodigoIBGE,
        caracarai: CodigoIBGE,
    ) -> None:
        """Municipios diferentes geram entradas separadas."""
        interrupcoes = [
            criar_interrupcao(1, boa_vista, 1, TipoInterrupcao.PROGRAMADA, 50),
            criar_interrupcao(2, caracarai, 1, TipoInterrupcao.PROGRAMADA, 30),
        ]

        resultado = service.agregar_por_municipio(interrupcoes)

        assert len(resultado) == 2
        assert resultado[1400100]["programada"] == 50
        assert resultado[1400209]["programada"] == 30
