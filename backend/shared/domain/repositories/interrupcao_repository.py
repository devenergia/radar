"""Protocol para repositorio de interrupcoes.

Este Protocol define o contrato (Port) que deve ser implementado
pela camada de infraestrutura. Segue o Dependency Inversion Principle:
o dominio define a interface, a infraestrutura implementa.

Regras:
- NAO importar SQLAlchemy, oracledb ou outros frameworks
- Retornar entidades de dominio (Interrupcao)
- Metodos SINCRONOS (padrao do projeto de referencia MJQEE-GFUZ)
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from backend.shared.domain.entities.interrupcao import Interrupcao
    from backend.shared.domain.value_objects.codigo_ibge import CodigoIBGE


class InterrupcaoRepository(Protocol):
    """
    Port para repositorio de interrupcoes.

    Define contrato que deve ser implementado pela camada de infraestrutura.
    O dominio depende desta interface, nao de implementacoes concretas (DIP).

    PADRAO: Metodos SINCRONOS (nao async) conforme projeto de referencia.
    Endpoints que usam este repositorio devem ser `def`, nao `async def`.

    Implementacoes concretas:
    - OracleInterrupcaoRepository (backend/apps/api_interrupcoes/repositories/)

    Exemplo de uso:
        class GetInterrupcoesUseCase:
            def __init__(self, repository: InterrupcaoRepository) -> None:
                self._repository = repository

            def execute(self) -> list[Interrupcao]:
                return self._repository.buscar_ativas()
    """

    def buscar_ativas(self) -> list[Interrupcao]:
        """
        Busca todas as interrupcoes ativas no momento.

        Uma interrupcao e considerada ativa quando:
        - is_open = 'T' no banco INSERVICE.AGENCY_EVENT
        - data_fim e None na entidade

        Returns:
            Lista de interrupcoes ativas (pode ser vazia se nao houver)

        Raises:
            Implementacao pode levantar excecoes de infraestrutura
            que devem ser tratadas pelo Use Case
        """
        ...

    def buscar_por_municipio(
        self,
        codigo_ibge: CodigoIBGE,
    ) -> list[Interrupcao]:
        """
        Busca interrupcoes ativas por municipio.

        Filtra interrupcoes pelo codigo IBGE do municipio.
        Usado para consultas geograficas.

        Args:
            codigo_ibge: Codigo IBGE do municipio (Value Object validado)

        Returns:
            Lista de interrupcoes ativas no municipio especificado
        """
        ...

    def buscar_por_conjunto(
        self,
        id_conjunto: int,
    ) -> list[Interrupcao]:
        """
        Busca interrupcoes ativas por conjunto eletrico.

        Filtra interrupcoes pelo ID do conjunto eletrico.
        Conjuntos sao agrupamentos tecnicos de UCs.

        Args:
            id_conjunto: ID do conjunto eletrico

        Returns:
            Lista de interrupcoes ativas no conjunto especificado
        """
        ...

    def buscar_historico(
        self,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> list[Interrupcao]:
        """
        Busca historico de interrupcoes em um periodo.

        Usado para o parametro dthRecuperacao da API ANEEL.
        Conforme especificacao, dados devem estar disponiveis por 7 dias.
        Funcionalidade de recuperacao ativa a partir de 01/04/2026.

        Args:
            data_inicio: Inicio do periodo de busca (inclusive)
            data_fim: Fim do periodo de busca (inclusive)

        Returns:
            Lista de interrupcoes no periodo (ativas e finalizadas)

        Note:
            Esta funcionalidade sera obrigatoria a partir de 01/04/2026
            conforme Oficio Circular 14/2025-SMA/ANEEL
        """
        ...
