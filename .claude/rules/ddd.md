---
paths: backend/**/domain/**/*.py
---

# Domain-Driven Design (DDD) Rules

## Linguagem Ubiqua

### Termos do Dominio RADAR
| Termo | Significado | Classe |
|-------|-------------|--------|
| Interrupcao | Evento de desligamento | Entity |
| Interrupcao Programada | Desligamento planejado (com PLAN_ID) | Value Object (enum) |
| Interrupcao Nao Programada | Desligamento emergencial | Value Object (enum) |
| Municipio/CodigoIBGE | Codigo de 7 digitos | Value Object |
| Conjunto Eletrico | Agrupamento de UCs | Property |
| UC (Unidade Consumidora) | Ponto de consumo | Property |
| Demanda | Solicitacao/reclamacao | Entity |

### Uso no Codigo
- Use termos em portugues para conceitos de dominio
- Nao use abreviacoes tecnicas (NAO: `get_int_agg`, SIM: `get_interrupcoes_agregadas`)

## Value Objects

### Caracteristicas Obrigatorias
- Imutavel: `@dataclass(frozen=True)`
- Comparado por valor
- Validacao no `__post_init__` ou factory method
- Factory method `create()` retorna `Result`

### Template
```python
from dataclasses import dataclass
from shared.domain.result import Result

@dataclass(frozen=True)
class CodigoIBGE:
    """Value Object para codigo IBGE de municipio."""

    valor: str

    MUNICIPIOS_RORAIMA = frozenset([
        "1400050", "1400027", "1400100", ...
    ])

    def __post_init__(self) -> None:
        if not self._is_valid():
            raise ValueError(f"Codigo IBGE invalido: {self.valor}")

    def _is_valid(self) -> bool:
        return len(self.valor) == 7 and self.valor.isdigit()

    @classmethod
    def create(cls, codigo: str | int) -> "Result[CodigoIBGE]":
        try:
            valor = str(codigo).zfill(7)
            return Result.ok(cls(valor=valor))
        except ValueError as e:
            return Result.fail(str(e))
```

## Entities

### Caracteristicas Obrigatorias
- Identidade unica (id)
- Igualdade por ID, nao por atributos
- Encapsula comportamento de negocio
- Factory method `create()` com validacao de invariantes

### Template
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Interrupcao:
    """Entidade que representa uma interrupcao de fornecimento."""

    _id: int
    _tipo: TipoInterrupcao
    _municipio: CodigoIBGE
    _conjunto: int
    _ucs_afetadas: int
    _data_inicio: datetime
    _data_fim: datetime | None

    @classmethod
    def create(cls, props: dict) -> "Result[Interrupcao]":
        if props.get("ucs_afetadas", 0) < 0:
            return Result.fail("UCs afetadas nao pode ser negativo")
        return Result.ok(cls(...))

    @property
    def id(self) -> int:
        return self._id

    def is_ativa(self) -> bool:
        """Interrupcao ativa quando nao tem data de fim."""
        return self._data_fim is None

    def is_programada(self) -> bool:
        return self._tipo == TipoInterrupcao.PROGRAMADA

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Interrupcao):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
```

## Aggregates

### Caracteristicas
- Grupo de entidades tratado como unidade
- Acesso apenas pela raiz do aggregate
- Transacoes respeitam limites do aggregate

### Template
```python
@dataclass(frozen=True)
class InterrupcaoAgregada:
    """Aggregate de interrupcoes por municipio/conjunto."""

    id_conjunto: int
    municipio: CodigoIBGE
    qtd_ucs_atendidas: int
    qtd_programada: int
    qtd_nao_programada: int

    @property
    def total_interrupcoes(self) -> int:
        return self.qtd_programada + self.qtd_nao_programada
```

## Domain Services

### Quando Usar
- Logica que nao pertence a uma unica entidade
- Operacoes entre multiplas entidades
- Agregacoes e calculos complexos

### Template
```python
class InterrupcaoAggregatorService:
    """Servico de dominio para agregacao de interrupcoes."""

    def agregar(
        self,
        interrupcoes: list[Interrupcao],
    ) -> list[InterrupcaoAgregada]:
        # Logica de agregacao por municipio + conjunto
        ...
```

## Repositories (Protocol)

### Definicao no Dominio
```python
from typing import Protocol

class InterrupcaoRepository(Protocol):
    """Port para repositorio de interrupcoes."""

    async def buscar_ativas(self) -> list[Interrupcao]:
        """Busca todas as interrupcoes ativas."""
        ...

    async def buscar_por_municipio(
        self,
        ibge: CodigoIBGE,
    ) -> list[Interrupcao]:
        ...
```

### Implementacao na Infraestrutura
A implementacao concreta fica em `infrastructure/repositories/`

## Result Pattern

### Uso Obrigatorio para Operacoes que Podem Falhar
```python
class Result(Generic[T]):
    @classmethod
    def ok(cls, value: T) -> "Result[T]": ...

    @classmethod
    def fail(cls, error: str) -> "Result[T]": ...

    @property
    def is_success(self) -> bool: ...

    @property
    def is_failure(self) -> bool: ...

    @property
    def value(self) -> T: ...

    @property
    def error(self) -> str: ...
```
