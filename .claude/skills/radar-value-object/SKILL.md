---
name: radar-value-object
description: Cria Value Objects imutaveis para o projeto RADAR seguindo DDD. Use quando o usuario pedir para criar um value object, VO, tipo de valor, ou modelar conceitos como CodigoIBGE, TipoInterrupcao, Email, CPF, ou qualquer objeto comparado por valor.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Criacao de Value Objects - Projeto RADAR

## Quando Usar

Esta skill e ativada automaticamente quando:
- Usuario pede para criar um "value object" ou "VO"
- Usuario quer modelar codigos, tipos, ou identificadores
- Menciona termos como "CodigoIBGE", "TipoInterrupcao", "Email"
- Precisa de objeto imutavel comparado por valor

## Regras Obrigatorias

### Localizacao
```
backend/shared/domain/value_objects/<nome_snake_case>.py
```

### Caracteristicas de um Value Object
1. **IMUTAVEL**: `@dataclass(frozen=True)`
2. Comparado por VALOR (nao por identidade)
3. Validacao no `__post_init__` (lanca ValueError)
4. Factory method `create()` retorna `Result` (nao lanca excecao)
5. Sem efeitos colaterais

## Templates

### Value Object Simples

```python
from dataclasses import dataclass

from shared.domain.result import Result


@dataclass(frozen=True)
class NomeDoValueObject:
    """Value Object para [descricao]."""

    valor: str

    def __post_init__(self) -> None:
        """Validacao no momento da criacao."""
        if not self._is_valid():
            raise ValueError(f"Valor invalido: {self.valor}")

    def _is_valid(self) -> bool:
        """Verifica se o valor e valido."""
        return bool(self.valor) and len(self.valor) > 0

    @classmethod
    def create(cls, valor: str) -> "Result[NomeDoValueObject]":
        """Factory method com validacao segura (nao lanca excecao)."""
        try:
            return Result.ok(cls(valor=valor))
        except ValueError as e:
            return Result.fail(str(e))

    def __str__(self) -> str:
        return self.valor
```

### Value Object com Validacao Complexa (ex: CodigoIBGE)

```python
from dataclasses import dataclass

from shared.domain.result import Result


@dataclass(frozen=True)
class CodigoIBGE:
    """Value Object para codigo IBGE de municipio de Roraima."""

    valor: str

    # Constantes de validacao
    MUNICIPIOS_RORAIMA = frozenset([
        "1400050",  # Alto Alegre
        "1400027",  # Amajari
        "1400100",  # Boa Vista
        "1400159",  # Bonfim
        "1400175",  # Canta
        "1400209",  # Caracarai
        "1400233",  # Caroebe
        "1400282",  # Iracema
        "1400308",  # Mucajai
        "1400407",  # Normandia
        "1400456",  # Pacaraima
        "1400472",  # Rorainopolis
        "1400506",  # Sao Joao da Baliza
        "1400605",  # Sao Luiz
        "1400704",  # Uiramuta
    ])

    def __post_init__(self) -> None:
        if not self._has_seven_digits():
            raise ValueError(f"Codigo IBGE deve ter 7 digitos: {self.valor}")
        if not self._is_roraima():
            raise ValueError(f"Codigo IBGE nao pertence a Roraima: {self.valor}")

    def _has_seven_digits(self) -> bool:
        return len(self.valor) == 7 and self.valor.isdigit()

    def _is_roraima(self) -> bool:
        return self.valor in self.MUNICIPIOS_RORAIMA

    @classmethod
    def create(cls, codigo: str | int) -> "Result[CodigoIBGE]":
        try:
            valor = str(codigo).zfill(7)
            return Result.ok(cls(valor=valor))
        except ValueError as e:
            return Result.fail(str(e))

    def __str__(self) -> str:
        return self.valor
```

### Value Object Enum

```python
from enum import Enum


class TipoInterrupcao(Enum):
    """Value Object enum para tipo de interrupcao."""

    PROGRAMADA = "PROGRAMADA"
    NAO_PROGRAMADA = "NAO_PROGRAMADA"

    @classmethod
    def from_plan_id(cls, plan_id: int | None) -> "TipoInterrupcao":
        """
        Determina tipo baseado na existencia de PLAN_ID.
        Regra: Se existe PLAN_ID, e programada.
        """
        return cls.PROGRAMADA if plan_id is not None else cls.NAO_PROGRAMADA

    def is_programada(self) -> bool:
        return self == TipoInterrupcao.PROGRAMADA
```

## Checklist de Validacao

- [ ] Arquivo em `backend/shared/domain/value_objects/`
- [ ] Usa `@dataclass(frozen=True)` para imutabilidade
- [ ] Validacao no `__post_init__`
- [ ] Factory method `create()` retorna `Result`
- [ ] `__str__` implementado
- [ ] Type hints completos

## Testes Obrigatorios

Criar em `backend/tests/unit/domain/value_objects/test_<nome>.py`:

```python
class TestNomeDoValueObject:
    class TestCreate:
        def test_deve_criar_valor_valido(self):
            result = NomeDoValueObject.create("valor_valido")
            assert result.is_success

        def test_deve_rejeitar_valor_invalido(self):
            result = NomeDoValueObject.create("")
            assert result.is_failure

    class TestEquality:
        def test_deve_ser_igual_quando_valores_iguais(self):
            vo1 = NomeDoValueObject.create("valor").value
            vo2 = NomeDoValueObject.create("valor").value
            assert vo1 == vo2

    class TestImmutability:
        def test_deve_ser_imutavel(self):
            vo = NomeDoValueObject.create("valor").value
            with pytest.raises(FrozenInstanceError):
                vo.valor = "outro"
```

## Exemplos do Projeto

- `CodigoIBGE` - Codigo de municipio (7 digitos, Roraima)
- `TipoInterrupcao` - PROGRAMADA ou NAO_PROGRAMADA
