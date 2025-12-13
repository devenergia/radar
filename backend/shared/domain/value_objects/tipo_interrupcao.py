"""Value Object para Tipo de Interrupcao."""

from __future__ import annotations

from enum import Enum


class TipoInterrupcao(str, Enum):
    """
    Value Object para Tipo de Interrupcao.

    Regras de negocio:
    - PROGRAMADA: Quando existe PLAN_ID na tabela SWITCH_PLAN_TASKS
    - NAO_PROGRAMADA: Quando NAO existe PLAN_ID

    Fonte: Oficio Circular 14/2025-SFE/ANEEL
    """

    PROGRAMADA = "PROGRAMADA"
    NAO_PROGRAMADA = "NAO_PROGRAMADA"

    @classmethod
    def from_plan_id(cls, plan_id: int | None) -> TipoInterrupcao:
        """
        Factory method baseado na regra de negocio do PLAN_ID.

        Se PLAN_ID existe (nao e None) -> PROGRAMADA
        Se PLAN_ID nao existe (e None) -> NAO_PROGRAMADA

        Args:
            plan_id: ID do plano de interrupcao

        Returns:
            TipoInterrupcao
        """
        return cls.PROGRAMADA if plan_id is not None else cls.NAO_PROGRAMADA

    @classmethod
    def from_codigo(cls, codigo: int) -> TipoInterrupcao:
        """
        Factory method a partir do codigo numerico.

        Args:
            codigo: 1 para PROGRAMADA, 2 para NAO_PROGRAMADA

        Returns:
            TipoInterrupcao

        Raises:
            ValueError: Se codigo invalido
        """
        if codigo == 1:
            return cls.PROGRAMADA
        if codigo == 2:
            return cls.NAO_PROGRAMADA
        raise ValueError(f"Codigo de tipo de interrupcao invalido: {codigo}")

    @property
    def codigo(self) -> int:
        """Retorna o codigo numerico do tipo."""
        return 1 if self == TipoInterrupcao.PROGRAMADA else 2

    def is_programada(self) -> bool:
        """Verifica se e programada."""
        return self == TipoInterrupcao.PROGRAMADA

    def is_nao_programada(self) -> bool:
        """Verifica se e nao programada."""
        return self == TipoInterrupcao.NAO_PROGRAMADA
