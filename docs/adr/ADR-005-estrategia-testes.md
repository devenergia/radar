# ADR-005: Estratégia de Testes (TDD)

## Status

Aceito

## Data

2025-12-12

## Contexto

O Projeto RADAR é uma API regulatória crítica que deve:

1. Atender requisitos específicos da ANEEL com precisão
2. Garantir disponibilidade 24x7
3. Retornar dados corretos e consistentes
4. Ser auditável e rastreável

Erros podem resultar em penalidades regulatórias e impacto na imagem da empresa.

## Decisão

Adotaremos **Test-Driven Development (TDD)** como prática de desenvolvimento, com foco em:

### Pirâmide de Testes

```
                    ┌───────────┐
                    │   E2E     │  10%
                    │  Tests    │
                 ┌──┴───────────┴──┐
                 │  Integration    │  30%
                 │     Tests       │
              ┌──┴─────────────────┴──┐
              │      Unit Tests       │  60%
              │                       │
              └───────────────────────┘
```

### Ferramentas

| Ferramenta | Uso |
|------------|-----|
| **pytest** | Test runner e assertions |
| **pytest-asyncio** | Testes assíncronos |
| **httpx** | Cliente HTTP para testes de API |
| **testcontainers** | Banco Oracle para testes de integração |
| **respx** | Mock de APIs externas (se houver) |
| **pytest-cov** | Cobertura de código |

### Estrutura de Testes

```
tests/
├── unit/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── test_interrupcao_entity.py
│   │   └── services/
│   │       └── test_calcular_tipo_interrupcao.py
│   ├── application/
│   │   └── use_cases/
│   │       └── test_get_interrupcoes_ativas.py
│   └── shared/
│       └── utils/
│           └── test_date_formatter.py
│
├── integration/
│   ├── repositories/
│   │   └── test_interrupcao_repository.py
│   └── database/
│       └── test_oracle_connection.py
│
└── e2e/
    ├── test_interrupcoes_e2e.py
    ├── test_demandas_e2e.py
    └── test_health_e2e.py
```

### Convenções de Nomenclatura

```python
# Arquivo: test_get_interrupcoes_ativas.py

import pytest
from app.application.use_cases import GetInterrupcoesAtivasUseCase

class TestGetInterrupcoesAtivasUseCase:
    """Testes para o caso de uso GetInterrupcoesAtivas"""

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_no_interrupcoes_are_active(self):
        # Arrange
        use_case = GetInterrupcoesAtivasUseCase(mock_repository)

        # Act
        result = await use_case.execute()

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_should_classify_interrupcao_as_programada_when_plan_id_exists(self):
        # Arrange, Act, Assert
        ...

    @pytest.mark.asyncio
    async def test_should_return_ibge_code_from_ind_universos(self):
        # Arrange, Act, Assert
        ...

    @pytest.mark.asyncio
    async def test_should_raise_when_database_connection_fails(self):
        # Arrange, Act, Assert
        with pytest.raises(DatabaseError):
            await use_case.execute()
```

### Metas de Cobertura

| Métrica | Meta Mínima |
|---------|-------------|
| **Statements** | 80% |
| **Branches** | 75% |
| **Functions** | 85% |
| **Lines** | 80% |

### Configuração Pytest

```python
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = """
    -v
    --strict-markers
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=json
    --cov-fail-under=80
"""

markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow running tests",
]

[tool.coverage.run]
source = ["app"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]

fail_under = 80
precision = 2
show_missing = true

[tool.coverage.html]
directory = "htmlcov"
```

### Configuração conftest.py

```python
# tests/conftest.py

import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from app.main import app
from app.infrastructure.database import get_db

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP para testes E2E"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def db_session():
    """Sessão de banco de dados para testes"""
    # Setup
    session = create_test_session()

    yield session

    # Teardown
    await session.rollback()
    await session.close()

@pytest.fixture
def mock_repository():
    """Mock do repositório para testes unitários"""
    from unittest.mock import AsyncMock
    return AsyncMock()
```

## Ciclo TDD

```
┌─────────────────────────────────────────────────────────┐
│                     CICLO TDD                            │
└─────────────────────────────────────────────────────────┘

    ┌──────────┐
    │  RED     │  1. Escrever teste que falha
    │  (Fail)  │
    └────┬─────┘
         │
         ▼
    ┌──────────┐
    │  GREEN   │  2. Escrever código mínimo para passar
    │  (Pass)  │
    └────┬─────┘
         │
         ▼
    ┌──────────┐
    │ REFACTOR │  3. Refatorar mantendo testes verdes
    │          │
    └────┬─────┘
         │
         └──────► Repetir
```

## Consequências

### Positivas

- **Confiança**: Mudanças podem ser feitas com segurança
- **Documentação Viva**: Testes documentam comportamento esperado
- **Design Melhor**: TDD força design desacoplado e testável
- **Debugging Rápido**: Falhas são detectadas imediatamente
- **Conformidade ANEEL**: Requisitos testados automaticamente
- **Regressão**: Evita quebrar funcionalidades existentes

### Negativas

- **Tempo Inicial**: Desenvolvimento mais lento no início
- **Manutenção**: Testes precisam ser mantidos junto com código
- **Curva de Aprendizado**: TDD requer prática para fazer bem

### Neutras

- Necessidade de ambiente de teste configurado
- CI/CD deve executar testes em cada push

## Alternativas Consideradas

### Alternativa 1: Testes Apenas de Integração/E2E

Testar apenas o sistema completo end-to-end.

**Rejeitado porque**: Testes lentos, difíceis de debugar, não testam edge cases adequadamente.

### Alternativa 2: Testes Manuais

Testar manualmente antes de cada release.

**Rejeitado porque**: Não escala, propenso a erros humanos, não detecta regressões.

### Alternativa 3: Testes Apenas Pós-Desenvolvimento

Escrever testes depois do código.

**Rejeitado porque**: Código tende a ser menos testável, cobertura geralmente menor, testes viram afterthought.

## Referências

- Kent Beck - Test-Driven Development by Example
- Martin Fowler - [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
