---
description: Cria um Value Object DDD seguindo os padroes do projeto
argument-hint: [NomeDoValueObject]
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Criar Value Object DDD

Crie um Value Object chamado `$ARGUMENTS` seguindo RIGOROSAMENTE os padroes DDD do projeto RADAR.

## Regras Obrigatorias

1. **Localizacao**: `backend/shared/domain/value_objects/$ARGUMENTS.py` (nome em snake_case)

2. **Caracteristicas**:
   - IMUTAVEL: `@dataclass(frozen=True)`
   - Comparado por VALOR (nao por identidade)
   - Validacao no `__post_init__` (lanca ValueError)
   - Factory method `create()` retornando `Result` (NAO lanca excecao)

3. **Template**:
```python
from dataclasses import dataclass

from shared.domain.result import Result


@dataclass(frozen=True)
class NomeDoValueObject:
    """Value Object para [descricao]."""

    valor: str  # ou outro tipo

    def __post_init__(self) -> None:
        """Validacao no momento da criacao."""
        if not self._is_valid():
            raise ValueError(f"Valor invalido: {self.valor}")

    def _is_valid(self) -> bool:
        """Verifica se o valor e valido."""
        # implementar validacao
        return True

    @classmethod
    def create(cls, valor: str) -> "Result[NomeDoValueObject]":
        """Factory method com validacao segura."""
        try:
            return Result.ok(cls(valor=valor))
        except ValueError as e:
            return Result.fail(str(e))

    def __str__(self) -> str:
        return str(self.valor)
```

4. **Para Enums**:
```python
from enum import Enum


class TipoAlgo(Enum):
    """Value Object enum para tipo de algo."""

    TIPO_A = "TIPO_A"
    TIPO_B = "TIPO_B"

    @classmethod
    def from_valor(cls, valor: str | None) -> "TipoAlgo":
        """Factory method baseado em valor."""
        return cls.TIPO_A if valor else cls.TIPO_B

    def is_tipo_a(self) -> bool:
        return self == TipoAlgo.TIPO_A
```

5. **Apos criar o Value Object**, crie tambem o teste em `backend/tests/unit/domain/value_objects/test_$ARGUMENTS.py`

## Testes Obrigatorios para Value Objects
- Criacao com valor valido
- Rejeicao com valor invalido
- Igualdade entre instancias com mesmo valor
- Imutabilidade (frozen=True)

## Referencias
- @docs/development/03-domain-driven-design.md
- @.claude/rules/ddd.md
