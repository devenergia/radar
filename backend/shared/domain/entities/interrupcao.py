"""Entidade Interrupcao."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from backend.shared.domain.result import Result
from backend.shared.domain.value_objects.codigo_ibge import CodigoIBGE
from backend.shared.domain.value_objects.tipo_interrupcao import TipoInterrupcao


@dataclass(frozen=True, slots=True)
class Interrupcao:
    """
    Entidade Interrupcao.

    Representa um evento de interrupcao no fornecimento de energia.
    Possui identidade unica (id) e encapsula regras de negocio.
    """

    id: int
    tipo: TipoInterrupcao
    municipio: CodigoIBGE
    conjunto: int
    ucs_afetadas: int
    data_inicio: datetime
    data_fim: datetime | None = None

    @classmethod
    def create(
        cls,
        id: int,
        tipo: TipoInterrupcao,
        municipio: CodigoIBGE,
        conjunto: int,
        ucs_afetadas: int,
        data_inicio: datetime,
        data_fim: datetime | None = None,
    ) -> Result[Interrupcao]:
        """
        Factory method com validacoes.

        Args:
            id: Identificador unico da interrupcao
            tipo: Tipo da interrupcao (PROGRAMADA ou NAO_PROGRAMADA)
            municipio: Codigo IBGE do municipio
            conjunto: Codigo do conjunto eletrico
            ucs_afetadas: Quantidade de unidades consumidoras afetadas
            data_inicio: Data/hora de inicio da interrupcao
            data_fim: Data/hora de fim da interrupcao (None se ainda ativa)

        Returns:
            Result com Interrupcao valida ou mensagem de erro
        """
        # Validar UCs afetadas
        if ucs_afetadas < 0:
            return Result.fail("Quantidade de UCs afetadas nao pode ser negativa")

        # Validar conjunto
        if conjunto < 0:
            return Result.fail("Codigo do conjunto nao pode ser negativo")

        # Validar datas
        if data_fim is not None and data_fim < data_inicio:
            return Result.fail("Data fim nao pode ser anterior a data inicio")

        return Result.ok(
            cls(
                id=id,
                tipo=tipo,
                municipio=municipio,
                conjunto=conjunto,
                ucs_afetadas=ucs_afetadas,
                data_inicio=data_inicio,
                data_fim=data_fim,
            )
        )

    def is_ativa(self) -> bool:
        """
        Uma interrupcao e ativa quando nao possui data de fim.

        Corresponde a is_open = 'T' na tabela AGENCY_EVENT.
        """
        return self.data_fim is None

    def is_programada(self) -> bool:
        """Verifica se a interrupcao e programada."""
        return self.tipo.is_programada()

    def is_nao_programada(self) -> bool:
        """Verifica se a interrupcao e nao programada."""
        return self.tipo.is_nao_programada()

    def get_duracao_minutos(self) -> int | None:
        """
        Calcula a duracao da interrupcao em minutos.

        Returns:
            Duracao em minutos ou None se ainda estiver ativa
        """
        if self.data_fim is None:
            return None

        diff = self.data_fim - self.data_inicio
        return int(diff.total_seconds() / 60)

    def to_dict(self) -> dict:
        """Converte para dicionario."""
        return {
            "id": self.id,
            "tipo": self.tipo.value,
            "municipio": self.municipio.valor,
            "conjunto": self.conjunto,
            "ucs_afetadas": self.ucs_afetadas,
            "data_inicio": self.data_inicio.isoformat(),
            "data_fim": self.data_fim.isoformat() if self.data_fim else None,
            "is_ativa": self.is_ativa(),
        }
