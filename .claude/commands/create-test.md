---
description: Cria um teste seguindo TDD (escreva o teste PRIMEIRO)
argument-hint: [tipo] [modulo] - tipo: unit|integration|e2e
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Criar Teste TDD

Crie um teste para `$ARGUMENTS` seguindo RIGOROSAMENTE o ciclo TDD: RED -> GREEN -> REFACTOR.

## Estrutura de Diretorios

```
backend/tests/
├── unit/                    # Testes unitarios (70%)
│   ├── domain/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   └── services/
│   └── application/
├── integration/             # Testes de integracao (20%)
│   ├── repositories/
│   └── use_cases/
└── e2e/                     # Testes E2E (10%)
    └── api/
```

## Templates por Tipo

### Teste Unitario - Value Object
```python
# tests/unit/domain/value_objects/test_nome.py
import pytest

from shared.domain.value_objects.nome import Nome


class TestNome:
    """Testes para Value Object Nome."""

    class TestCreate:
        def test_deve_criar_valor_valido(self):
            # Arrange
            valor = "valor_valido"

            # Act
            result = Nome.create(valor)

            # Assert
            assert result.is_success
            assert result.value.valor == valor

        def test_deve_rejeitar_valor_invalido(self):
            # Arrange
            valor_invalido = ""

            # Act
            result = Nome.create(valor_invalido)

            # Assert
            assert result.is_failure
            assert "invalido" in result.error.lower()

    class TestEquality:
        def test_deve_ser_igual_quando_valores_iguais(self):
            nome1 = Nome.create("valor").value
            nome2 = Nome.create("valor").value

            assert nome1 == nome2

        def test_deve_ser_diferente_quando_valores_diferentes(self):
            nome1 = Nome.create("valor1").value
            nome2 = Nome.create("valor2").value

            assert nome1 != nome2
```

### Teste Unitario - Entity
```python
# tests/unit/domain/entities/test_entidade.py
import pytest
from datetime import datetime

from shared.domain.entities.entidade import Entidade


class TestEntidade:
    """Testes para Entity Entidade."""

    class TestCreate:
        def test_deve_criar_entidade_valida(self):
            # Arrange
            props = {
                "id": 1,
                "campo": "valor",
            }

            # Act
            result = Entidade.create(props)

            # Assert
            assert result.is_success
            assert result.value.id == 1

        def test_deve_rejeitar_quando_invariante_violada(self):
            # Arrange
            props = {"id": 1, "campo_obrigatorio": None}

            # Act
            result = Entidade.create(props)

            # Assert
            assert result.is_failure

    class TestBehavior:
        @pytest.fixture
        def entidade(self):
            return Entidade.create({"id": 1, "campo": "valor"}).value

        def test_deve_retornar_true_quando_condicao(self, entidade):
            assert entidade.metodo_de_negocio() is True
```

### Teste de Integracao - Use Case
```python
# tests/integration/use_cases/test_get_algo.py
import pytest
from unittest.mock import AsyncMock

from apps.api.application.use_cases.get_algo import GetAlgoUseCase


@pytest.mark.integration
class TestGetAlgoUseCase:
    @pytest.fixture
    def mock_repository(self):
        repo = AsyncMock()
        repo.buscar_ativas.return_value = []
        return repo

    @pytest.fixture
    def mock_cache(self):
        cache = AsyncMock()
        cache.get.return_value = None
        return cache

    @pytest.fixture
    def use_case(self, mock_repository, mock_cache):
        return GetAlgoUseCase(mock_repository, mock_cache)

    async def test_deve_buscar_do_cache_primeiro(
        self,
        use_case,
        mock_cache,
        mock_repository,
    ):
        # Arrange
        dados_cached = [{"id": 1}]
        mock_cache.get.return_value = dados_cached

        # Act
        result = await use_case.execute()

        # Assert
        assert result.is_success
        mock_repository.buscar_ativas.assert_not_called()

    async def test_deve_buscar_do_repo_quando_cache_vazio(
        self,
        use_case,
        mock_cache,
        mock_repository,
    ):
        # Arrange
        mock_cache.get.return_value = None

        # Act
        result = await use_case.execute()

        # Assert
        mock_repository.buscar_ativas.assert_called_once()
```

### Teste E2E - API
```python
# tests/e2e/api/test_endpoint.py
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.e2e
class TestEndpoint:
    async def test_deve_retornar_200_com_dados(
        self,
        client: AsyncClient,
        api_key: str,
    ):
        response = await client.get(
            "/endpoint",
            headers={"x-api-key": api_key},
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert "campo" in body

    async def test_deve_retornar_401_sem_api_key(
        self,
        client: AsyncClient,
    ):
        response = await client.get("/endpoint")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

## Padrao AAA (Arrange-Act-Assert)

SEMPRE siga o padrao AAA com comentarios:
```python
def test_nome_descritivo(self):
    # Arrange - Preparar dados e mocks

    # Act - Executar a acao

    # Assert - Verificar resultado
```

## Nomenclatura

- Arquivo: `test_<modulo>.py`
- Classe: `Test<Classe>`
- Metodo: `test_deve_<comportamento>_quando_<condicao>`

## Referencias
- @docs/development/04-tdd-test-driven-development.md
- @.claude/rules/tdd.md
