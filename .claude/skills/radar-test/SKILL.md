---
name: radar-test
description: Cria testes seguindo TDD para o projeto RADAR. Use quando o usuario pedir para criar testes, testar codigo, escrever testes unitarios, testes de integracao, testes e2e, ou quando mencionar pytest, cobertura de testes, ou TDD.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Criacao de Testes TDD - Projeto RADAR

## Quando Usar

Esta skill e ativada automaticamente quando:
- Usuario pede para criar "testes" ou "test"
- Usuario menciona TDD, pytest, cobertura
- Usuario quer testar uma funcionalidade
- Menciona "unit test", "integration test", "e2e"

## Principio Fundamental: TDD

```
RED → GREEN → REFACTOR
 │       │         │
 │       │         └── Melhorar codigo mantendo testes verdes
 │       └── Implementar minimo para passar
 └── Escrever teste que FALHA primeiro
```

## Estrutura de Diretorios

```
backend/tests/
├── unit/                    # 70% - Rapidos, sem I/O
│   ├── domain/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   └── services/
│   └── application/
├── integration/             # 20% - Com mocks de infra
│   ├── repositories/
│   └── use_cases/
├── e2e/                     # 10% - HTTP completo
│   └── api/
├── fixtures/
├── helpers/
└── conftest.py
```

## Templates por Tipo

### Teste Unitario - Value Object

```python
# tests/unit/domain/value_objects/test_codigo_ibge.py
import pytest
from dataclasses import FrozenInstanceError

from shared.domain.value_objects.codigo_ibge import CodigoIBGE


class TestCodigoIBGE:
    """Testes para Value Object CodigoIBGE."""

    class TestCreate:
        def test_deve_criar_codigo_valido_para_boa_vista(self):
            # Arrange
            codigo = "1400100"

            # Act
            result = CodigoIBGE.create(codigo)

            # Assert
            assert result.is_success
            assert result.value.valor == "1400100"

        def test_deve_criar_codigo_com_padding_de_zeros(self):
            # Arrange
            codigo = 1400100  # int sem zeros a esquerda

            # Act
            result = CodigoIBGE.create(codigo)

            # Assert
            assert result.is_success
            assert result.value.valor == "1400100"

        def test_deve_rejeitar_codigo_com_menos_de_7_digitos(self):
            # Arrange
            codigo = "140010"  # 6 digitos

            # Act
            result = CodigoIBGE.create(codigo)

            # Assert
            assert result.is_failure
            assert "7 digitos" in result.error.lower()

        def test_deve_rejeitar_codigo_de_outro_estado(self):
            # Arrange
            codigo = "3550308"  # Sao Paulo

            # Act
            result = CodigoIBGE.create(codigo)

            # Assert
            assert result.is_failure
            assert "Roraima" in result.error

    class TestEquality:
        def test_deve_ser_igual_quando_valores_iguais(self):
            ibge1 = CodigoIBGE.create("1400100").value
            ibge2 = CodigoIBGE.create("1400100").value

            assert ibge1 == ibge2

        def test_deve_ser_diferente_quando_valores_diferentes(self):
            ibge1 = CodigoIBGE.create("1400100").value
            ibge2 = CodigoIBGE.create("1400159").value

            assert ibge1 != ibge2

    class TestImmutability:
        def test_deve_ser_imutavel(self):
            ibge = CodigoIBGE.create("1400100").value

            with pytest.raises(FrozenInstanceError):
                ibge.valor = "1400159"
```

### Teste Unitario - Entity

```python
# tests/unit/domain/entities/test_interrupcao.py
import pytest
from datetime import datetime

from shared.domain.entities.interrupcao import Interrupcao
from shared.domain.value_objects.tipo_interrupcao import TipoInterrupcao
from shared.domain.value_objects.codigo_ibge import CodigoIBGE


class TestInterrupcao:
    """Testes para Entity Interrupcao."""

    @pytest.fixture
    def props_validas(self):
        return {
            "id": 12345,
            "tipo": TipoInterrupcao.PROGRAMADA,
            "municipio": CodigoIBGE.create("1400100").value,
            "conjunto": 1,
            "ucs_afetadas": 150,
            "data_inicio": datetime.now(),
        }

    class TestCreate:
        def test_deve_criar_interrupcao_valida(self, props_validas):
            # Act
            result = Interrupcao.create(props_validas)

            # Assert
            assert result.is_success
            assert result.value.id == 12345

        def test_deve_rejeitar_ucs_negativas(self, props_validas):
            # Arrange
            props_validas["ucs_afetadas"] = -1

            # Act
            result = Interrupcao.create(props_validas)

            # Assert
            assert result.is_failure
            assert "negativo" in result.error.lower()

    class TestBehavior:
        def test_deve_ser_ativa_quando_sem_data_fim(self, props_validas):
            interrupcao = Interrupcao.create(props_validas).value

            assert interrupcao.is_ativa() is True

        def test_deve_ser_inativa_quando_tem_data_fim(self, props_validas):
            props_validas["data_fim"] = datetime.now()
            interrupcao = Interrupcao.create(props_validas).value

            assert interrupcao.is_ativa() is False

    class TestEquality:
        def test_deve_ser_igual_por_id(self, props_validas):
            int1 = Interrupcao.create(props_validas).value
            int2 = Interrupcao.create(props_validas).value

            assert int1 == int2
            assert hash(int1) == hash(int2)
```

### Teste de Integracao - Use Case

```python
# tests/integration/use_cases/test_get_interrupcoes_ativas.py
import pytest
from unittest.mock import AsyncMock

from apps.api_interrupcoes.application.use_cases.get_interrupcoes_ativas import (
    GetInterrupcoesAtivasUseCase,
)
from shared.domain.repositories.interrupcao_repository import InterrupcaoRepository
from shared.domain.services.cache_service import CacheService
from tests.helpers.factories import create_interrupcao, create_agregada


@pytest.mark.integration
class TestGetInterrupcoesAtivasUseCase:
    @pytest.fixture
    def mock_repository(self):
        repo = AsyncMock(spec=InterrupcaoRepository)
        repo.buscar_ativas.return_value = []
        return repo

    @pytest.fixture
    def mock_cache(self):
        cache = AsyncMock(spec=CacheService)
        cache.get.return_value = None
        return cache

    @pytest.fixture
    def use_case(self, mock_repository, mock_cache):
        return GetInterrupcoesAtivasUseCase(mock_repository, mock_cache)

    async def test_deve_buscar_do_cache_primeiro(
        self,
        use_case,
        mock_cache,
        mock_repository,
    ):
        # Arrange
        dados_cached = [create_agregada()]
        mock_cache.get.return_value = dados_cached

        # Act
        result = await use_case.execute()

        # Assert
        assert result.is_success
        assert result.value == dados_cached
        mock_repository.buscar_ativas.assert_not_called()

    async def test_deve_buscar_do_repo_quando_cache_vazio(
        self,
        use_case,
        mock_repository,
        mock_cache,
    ):
        # Arrange
        mock_cache.get.return_value = None
        mock_repository.buscar_ativas.return_value = [create_interrupcao()]

        # Act
        result = await use_case.execute()

        # Assert
        assert result.is_success
        mock_repository.buscar_ativas.assert_called_once()
        mock_cache.set.assert_called_once()
```

### Teste E2E - API

```python
# tests/e2e/api/test_interrupcoes.py
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.e2e
class TestQuantitativoInterrupcoesAtivas:
    async def test_deve_retornar_200_com_formato_aneel(
        self,
        client: AsyncClient,
        api_key: str,
    ):
        # Act
        response = await client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": api_key},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["idcStatusRequisicao"] == 1
        assert body["desStatusRequisicao"] == "Sucesso"
        assert isinstance(body["listaInterrupcoes"], list)

    async def test_deve_retornar_401_sem_api_key(
        self,
        client: AsyncClient,
    ):
        # Act
        response = await client.get("/quantitativointerrupcoesativas")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_deve_incluir_campos_obrigatorios(
        self,
        client: AsyncClient,
        api_key: str,
    ):
        # Act
        response = await client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": api_key},
        )

        # Assert
        body = response.json()
        if body["listaInterrupcoes"]:
            item = body["listaInterrupcoes"][0]
            assert "ideConjuntoUnidadeConsumidora" in item
            assert "ideMunicipio" in item
            assert "qtdUCsAtendidas" in item
```

## Padrao AAA (Arrange-Act-Assert)

**SEMPRE** use comentarios AAA:

```python
def test_nome_descritivo(self):
    # Arrange - Preparar dados e mocks

    # Act - Executar a acao

    # Assert - Verificar resultado
```

## Nomenclatura

| Elemento | Padrao | Exemplo |
|----------|--------|---------|
| Arquivo | `test_<modulo>.py` | `test_codigo_ibge.py` |
| Classe | `Test<Classe>` | `TestCodigoIBGE` |
| Metodo | `test_deve_<comportamento>_quando_<condicao>` | `test_deve_rejeitar_quando_invalido` |

## Comandos pytest

```bash
# Todos os testes
pytest

# Por tipo
pytest -m unit
pytest -m integration
pytest -m e2e

# Com cobertura
pytest --cov=backend --cov-report=html --cov-fail-under=80

# Arquivo especifico
pytest backend/tests/unit/domain/value_objects/test_codigo_ibge.py

# Verbose
pytest -v -s
```

## Meta de Cobertura

- **Minimo**: 80% de linhas
- **Recomendado**: 80% de branches
