---
description: Cria uma Entity DDD seguindo os padroes do projeto
argument-hint: [NomeDaEntidade]
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Criar Entity DDD

Crie uma Entity chamada `$ARGUMENTS` seguindo RIGOROSAMENTE os padroes DDD do projeto RADAR.

## Regras Obrigatorias

1. **Localizacao**: `backend/shared/domain/entities/$ARGUMENTS.py` (nome em snake_case)

2. **Estrutura**:
   - Use `@dataclass` (NAO frozen, entities podem mudar estado)
   - Atributos privados com prefixo `_`
   - Properties para acesso
   - Factory method `create()` retornando `Result`
   - Validacao de invariantes no `create()`
   - Igualdade por ID (`__eq__` e `__hash__`)
   - Metodos de comportamento de negocio

3. **Template**:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.result import Result


@dataclass
class NomeDaEntidade:
    """Entidade que representa [descricao]."""

    _id: int
    # outros atributos privados

    @classmethod
    def create(cls, props: dict[str, Any]) -> "Result[NomeDaEntidade]":
        """Factory method com validacao de invariantes."""
        # validacoes
        if props.get("campo") < 0:
            return Result.fail("Campo nao pode ser negativo")

        return Result.ok(cls(
            _id=props["id"],
            # ...
        ))

    @property
    def id(self) -> int:
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NomeDaEntidade):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
```

4. **Apos criar a entity**, crie tambem o teste em `backend/tests/unit/domain/entities/test_$ARGUMENTS.py`

## Referencias
- @docs/development/03-domain-driven-design.md
- @.claude/rules/ddd.md
