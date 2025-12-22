"""Domain Services.

Servicos de dominio encapsulam logica que nao pertence
a uma entidade especifica.
"""

from backend.shared.domain.services.interrupcao_aggregator import (
    InterrupcaoAggregatorService,
    InterrupcaoAgregada,
)

__all__ = [
    "InterrupcaoAgregada",
    "InterrupcaoAggregatorService",
]
