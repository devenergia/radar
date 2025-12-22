"""Domain Service para agregacao de interrupcoes.

Agrega interrupcoes por Municipio + Conjunto + Tipo,
totalizando as UCs afetadas em cada categoria.

Regra de Negocio ANEEL:
- Dados agregados por municipio (IBGE) + conjunto eletrico
- Separacao entre programada e nao programada
- Totalizacao de UCs afetadas
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from backend.shared.domain.value_objects.codigo_ibge import CodigoIBGE

if TYPE_CHECKING:
    from backend.shared.domain.entities.interrupcao import Interrupcao


@dataclass(frozen=True, slots=True)
class InterrupcaoAgregada:
    """Aggregate que representa interrupcoes agregadas por municipio/conjunto.

    Imutavel (frozen) para garantir integridade dos dados agregados.

    Attributes:
        id_conjunto: Codigo do conjunto eletrico
        municipio: Codigo IBGE do municipio
        qtd_ucs_atendidas: Total de UCs atendidas no conjunto/municipio
        qtd_programada: Total de UCs afetadas por interrupcoes programadas
        qtd_nao_programada: Total de UCs afetadas por interrupcoes nao programadas
    """

    id_conjunto: int
    municipio: CodigoIBGE
    qtd_ucs_atendidas: int
    qtd_programada: int
    qtd_nao_programada: int

    @property
    def total_interrupcoes(self) -> int:
        """Total de UCs com interrupcao (programada + nao programada)."""
        return self.qtd_programada + self.qtd_nao_programada

    def has_interrupcoes(self) -> bool:
        """Verifica se ha interrupcoes neste agregado."""
        return self.total_interrupcoes > 0


class InterrupcaoAggregatorService:
    """Servico de dominio para agregacao de interrupcoes.

    Responsabilidade unica: agregar interrupcoes individuais em totais
    por municipio e conjunto eletrico.

    Exemplo de uso:
        aggregator = InterrupcaoAggregatorService()
        agregadas = aggregator.agregar(interrupcoes)
    """

    def agregar(
        self,
        interrupcoes: list[Interrupcao],
        universo: dict[tuple[int, int], int] | None = None,
    ) -> list[InterrupcaoAgregada]:
        """Agrega interrupcoes por municipio e conjunto.

        Args:
            interrupcoes: Lista de interrupcoes individuais
            universo: Mapa (conjunto, ibge) -> qtd_ucs_atendidas

        Returns:
            Lista de interrupcoes agregadas por municipio/conjunto
        """
        if not interrupcoes:
            return []

        # Estrutura: {(conjunto, ibge): {prog: int, nao_prog: int}}
        agrupadas: dict[tuple[int, int], dict[str, int]] = defaultdict(
            lambda: {"programada": 0, "nao_programada": 0}
        )

        for interrupcao in interrupcoes:
            chave = (interrupcao.conjunto, interrupcao.municipio.valor)

            if interrupcao.is_programada():
                agrupadas[chave]["programada"] += interrupcao.ucs_afetadas
            else:
                agrupadas[chave]["nao_programada"] += interrupcao.ucs_afetadas

        universo = universo or {}

        return [
            InterrupcaoAgregada(
                id_conjunto=conjunto,
                municipio=CodigoIBGE.create_unsafe(ibge),
                qtd_ucs_atendidas=universo.get((conjunto, ibge), 0),
                qtd_programada=dados["programada"],
                qtd_nao_programada=dados["nao_programada"],
            )
            for (conjunto, ibge), dados in agrupadas.items()
        ]

    def agregar_por_municipio(
        self,
        interrupcoes: list[Interrupcao],
    ) -> dict[int, dict[str, int]]:
        """Agrega apenas por municipio (sem considerar conjunto).

        Util para relatorios resumidos por municipio.

        Args:
            interrupcoes: Lista de interrupcoes individuais

        Returns:
            Dict com ibge -> {programada, nao_programada, total_ucs}
        """
        if not interrupcoes:
            return {}

        resultado: dict[int, dict[str, int]] = defaultdict(
            lambda: {"programada": 0, "nao_programada": 0, "total_ucs": 0}
        )

        for interrupcao in interrupcoes:
            ibge = interrupcao.municipio.valor

            if interrupcao.is_programada():
                resultado[ibge]["programada"] += interrupcao.ucs_afetadas
            else:
                resultado[ibge]["nao_programada"] += interrupcao.ucs_afetadas

            resultado[ibge]["total_ucs"] += interrupcao.ucs_afetadas

        return dict(resultado)
