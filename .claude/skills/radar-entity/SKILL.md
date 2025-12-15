---
name: radar-entity
description: Cria Entities DDD para o projeto RADAR seguindo Clean Architecture. Use quando o usuario pedir para criar uma entidade, entity, ou modelar um conceito de dominio com identidade unica como Interrupcao, Demanda, ou similar.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Criacao de Entities DDD - Projeto RADAR

## Quando Usar

Esta skill e ativada automaticamente quando:
- Usuario pede para criar uma "entidade" ou "entity"
- Usuario quer modelar um conceito de dominio com identidade
- Menciona termos como "Interrupcao", "Demanda", ou similar

## Regras Obrigatorias

### Localizacao
```
backend/shared/domain/entities/<nome_snake_case>.py
```

### Caracteristicas de uma Entity
1. Possui identidade unica (ID)
2. Igualdade comparada por ID (nao por atributos)
3. Pode mudar estado (NAO e frozen)
4. Encapsula comportamento de negocio
5. Factory method `create()` retorna `Result`

### Template Obrigatorio

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.result import Result
from shared.domain.value_objects.tipo_algo import TipoAlgo


@dataclass
class NomeDaEntidade:
    """Entidade que representa [descricao do conceito de dominio]."""

    _id: int
    _tipo: TipoAlgo
    _campo_obrigatorio: str
    _data_criacao: datetime
    _campo_opcional: str | None = None

    @classmethod
    def create(cls, props: dict[str, Any]) -> "Result[NomeDaEntidade]":
        """Factory method com validacao de invariantes."""
        # Validar invariantes de negocio
        if not props.get("campo_obrigatorio"):
            return Result.fail("Campo obrigatorio nao pode ser vazio")

        if props.get("valor_numerico", 0) < 0:
            return Result.fail("Valor numerico nao pode ser negativo")

        return Result.ok(cls(
            _id=props["id"],
            _tipo=props["tipo"],
            _campo_obrigatorio=props["campo_obrigatorio"],
            _data_criacao=props.get("data_criacao", datetime.now()),
            _campo_opcional=props.get("campo_opcional"),
        ))

    # Properties para acesso (encapsulamento)
    @property
    def id(self) -> int:
        return self._id

    @property
    def tipo(self) -> TipoAlgo:
        return self._tipo

    # Metodos de comportamento de negocio
    def is_ativo(self) -> bool:
        """Verifica se a entidade esta ativa."""
        return self._campo_opcional is None

    def pode_ser_processado(self) -> bool:
        """Regra de negocio: verifica se pode ser processado."""
        return self.is_ativo() and self._tipo.is_valido()

    # Igualdade por ID (obrigatorio para Entity)
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NomeDaEntidade):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return f"NomeDaEntidade(id={self._id})"
```

## Checklist de Validacao

Antes de finalizar, verificar:
- [ ] Arquivo em `backend/shared/domain/entities/`
- [ ] Usa `@dataclass` (sem frozen)
- [ ] Atributos privados com prefixo `_`
- [ ] Factory method `create()` retorna `Result`
- [ ] Invariantes validadas no `create()`
- [ ] `__eq__` e `__hash__` implementados por ID
- [ ] Metodos de negocio com nomes claros
- [ ] Type hints em todos os metodos

## Apos Criar a Entity

1. Criar teste unitario em `backend/tests/unit/domain/entities/test_<nome>.py`
2. Testar: criacao valida, invariantes, igualdade, comportamentos

## Exemplos do Projeto

- `Interrupcao` - Evento de desligamento de energia
- `Demanda` - Solicitacao/reclamacao de consumidor

Ver [templates/entity.py](templates/entity.py) para template completo.
