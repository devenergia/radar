"""Value Object para Codigo IBGE de Municipio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from backend.shared.domain.result import Result


@dataclass(frozen=True, slots=True)
class CodigoIBGE:
    """
    Value Object para Codigo IBGE de Municipio.

    Imutavel e validado na criacao.

    Regras:
    - Deve ter 7 digitos
    - Deve pertencer a Roraima (14xxxxx)
    """

    valor: int

    # Lista de codigos IBGE dos 15 municipios de Roraima
    MUNICIPIOS_RORAIMA: ClassVar[tuple[int, ...]] = (
        1400050,  # Alto Alegre
        1400027,  # Amajari
        1400100,  # Boa Vista
        1400159,  # Bonfim
        1400175,  # Canta
        1400209,  # Caracarai
        1400233,  # Caroebe
        1400282,  # Iracema
        1400308,  # Mucajai
        1400407,  # Normandia
        1400456,  # Pacaraima
        1400472,  # Rorainopolis
        1400506,  # Sao Joao da Baliza
        1400605,  # Sao Luiz
        1400704,  # Uiramuta
    )

    MIN_VALUE: ClassVar[int] = 1000000
    MAX_VALUE: ClassVar[int] = 9999999

    @classmethod
    def create(cls, codigo: int) -> Result[CodigoIBGE]:
        """
        Factory method para criar CodigoIBGE validado.

        Args:
            codigo: Codigo IBGE do municipio (7 digitos)

        Returns:
            Result com CodigoIBGE valido ou mensagem de erro
        """
        if not cls._has_seven_digits(codigo):
            return Result.fail(
                f"Codigo IBGE invalido: {codigo}. Deve ter 7 digitos."
            )

        if not cls._belongs_to_roraima(codigo):
            return Result.fail(
                f"Codigo IBGE {codigo} nao pertence a Roraima. "
                f"Codigos validos: {', '.join(map(str, cls.MUNICIPIOS_RORAIMA))}"
            )

        return Result.ok(cls(valor=codigo))

    @classmethod
    def create_unsafe(cls, codigo: int) -> CodigoIBGE:
        """
        Cria CodigoIBGE sem validacao.

        Use apenas quando os dados ja foram validados (ex: vindos do banco).

        Args:
            codigo: Codigo IBGE do municipio

        Returns:
            CodigoIBGE
        """
        return cls(valor=codigo)

    @classmethod
    def _has_seven_digits(cls, codigo: int) -> bool:
        """Verifica se o codigo tem 7 digitos."""
        return cls.MIN_VALUE <= codigo <= cls.MAX_VALUE

    @classmethod
    def _belongs_to_roraima(cls, codigo: int) -> bool:
        """Verifica se o codigo pertence a Roraima."""
        return codigo in cls.MUNICIPIOS_RORAIMA

    @classmethod
    def get_all_roraima_codes(cls) -> tuple[int, ...]:
        """Retorna lista de todos os codigos IBGE de Roraima."""
        return cls.MUNICIPIOS_RORAIMA

    def __str__(self) -> str:
        return str(self.valor)

    def __int__(self) -> int:
        return self.valor
