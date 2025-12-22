"""Repository Protocols (Ports) do dominio.

Estes Protocols definem contratos que devem ser implementados
pela camada de infraestrutura. O dominio depende destas interfaces,
NAO de implementacoes concretas (Dependency Inversion Principle).
"""

from backend.shared.domain.repositories.interrupcao_repository import (
    InterrupcaoRepository,
)

__all__ = ["InterrupcaoRepository"]
