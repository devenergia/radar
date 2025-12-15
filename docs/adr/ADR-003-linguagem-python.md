# ADR-003: Python como Linguagem Principal

## Status

Aceito

## Data

2025-12-12 (Atualizado: 2025-12-15)

## Contexto

Precisamos escolher a linguagem de programacao para desenvolver a API RADAR. Requisitos:

1. Boa integracao com Oracle Database
2. Performance adequada para API de tempo real
3. Tipagem para evitar erros em tempo de execucao
4. Ecossistema maduro para desenvolvimento de APIs
5. Facilidade de manutencao e onboarding de novos desenvolvedores

## Decisao

Utilizaremos **Python** como linguagem principal do projeto.

### Versao

- Python: ^3.11
- Type Hints: PEP 484, PEP 604 (Union com |)

### Configuracao Base (pyproject.toml)

```toml
[project]
requires-python = ">=3.11"

[tool.mypy]
python_version = "3.11"
strict = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
strict_equality = true

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM"]

[tool.black]
line-length = 100
target-version = ["py311"]
```

### Convencoes de Codigo

- **Naming**: snake_case para variaveis/funcoes, PascalCase para classes
- **Arquivos**: snake_case para nomes de arquivos
- **Imports**: Organizados com isort (stdlib, third-party, local)
- **Type Hints**: Obrigatorios em todas as funcoes publicas
- **Docstrings**: Google style para funcoes complexas

### Exemplo de Codigo

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class CodigoIBGE:
    """Value Object para codigo IBGE de 7 digitos."""

    valor: str

    def __post_init__(self) -> None:
        if not self.valor.isdigit() or len(self.valor) != 7:
            raise ValueError(f"Codigo IBGE invalido: {self.valor}")


class InterrupcaoRepository(Protocol):
    """Interface (Port) para repositorio de interrupcoes."""

    async def buscar_ativas(self, data_referencia: str) -> list[Interrupcao]:
        """Busca interrupcoes ativas na data de referencia."""
        ...
```

## Consequencias

### Positivas

- **Type Hints**: Tipagem estatica com mypy em modo strict
- **Legibilidade**: Sintaxe clara e concisa
- **Async/Await**: Suporte nativo a programacao assincrona
- **Oracle Driver**: oracledb e um driver maduro e performatico
- **Ecossistema**: Vasto ecossistema para APIs (FastAPI, Pydantic, SQLAlchemy)
- **Onboarding**: Python e amplamente conhecido e facil de aprender

### Negativas

- **Performance**: Mais lento que linguagens compiladas (mitigado com async)
- **GIL**: Global Interpreter Lock limita paralelismo (mitigado com asyncio)
- **Tipagem Opcional**: Type hints podem ser ignorados (mitigado com mypy strict)

### Neutras

- Necessidade de ambiente virtual para isolamento de dependencias
- Curva de aprendizado para async/await e type hints avancados

## Alternativas Consideradas

### Alternativa 1: TypeScript com Node.js

Framework moderno com tipagem estatica.

**Rejeitado porque**: Equipe tem mais experiencia com Python, driver Oracle (oracledb) mais maduro em Python, FastAPI oferece validacao automatica superior.

### Alternativa 2: Java com Spring Boot

Framework enterprise consolidado.

**Rejeitado porque**: Mais verboso, maior consumo de recursos, tempo de desenvolvimento maior.

### Alternativa 3: Go

Linguagem compilada de alta performance.

**Rejeitado porque**: Menor ecossistema para APIs REST, driver Oracle menos maduro, curva de aprendizado maior para a equipe.

## Referencias

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [oracledb Driver](https://python-oracledb.readthedocs.io/)
