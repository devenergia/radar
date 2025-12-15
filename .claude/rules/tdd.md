---
paths: backend/**/*.py
---

# Test-Driven Development (TDD) Rules

## Ciclo Red-Green-Refactor

### OBRIGATORIO
1. **RED**: Escreva o teste PRIMEIRO (deve falhar)
2. **GREEN**: Implemente o MINIMO para passar
3. **REFACTOR**: Melhore o codigo mantendo testes verdes

## Estrutura de Testes

### Organizacao de Arquivos
```
backend/tests/
├── unit/                    # 70% dos testes
│   ├── domain/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   └── services/
│   └── application/
├── integration/             # 20% dos testes
│   ├── repositories/
│   └── use_cases/
└── e2e/                     # 10% dos testes
    └── api/
```

### Nomenclatura
- Arquivo: `test_<modulo>.py`
- Classe: `Test<Classe>`
- Metodo: `test_deve_<comportamento>_quando_<condicao>`

```python
# tests/unit/domain/value_objects/test_codigo_ibge.py
class TestCodigoIBGE:
    class TestCreate:
        def test_deve_criar_codigo_valido_para_boa_vista(self):
            ...

        def test_deve_rejeitar_codigo_com_menos_de_7_digitos(self):
            ...
```

## Markers pytest

### Uso Obrigatorio
```python
import pytest

@pytest.mark.unit
class TestCodigoIBGE:
    ...

@pytest.mark.integration
class TestOracleInterrupcaoRepository:
    ...

@pytest.mark.e2e
class TestQuantitativoInterrupcoesAtivas:
    ...
```

## Padrao AAA (Arrange-Act-Assert)

### Estrutura Obrigatoria
```python
def test_deve_agregar_interrupcoes_por_municipio(self):
    # Arrange - Preparar dados
    municipio = CodigoIBGE.create("1400100").value
    interrupcoes = [
        create_interrupcao(municipio=municipio, tipo="PROGRAMADA", ucs=50),
        create_interrupcao(municipio=municipio, tipo="PROGRAMADA", ucs=30),
    ]
    service = InterrupcaoAggregatorService()

    # Act - Executar acao
    agregadas = service.agregar(interrupcoes)

    # Assert - Verificar resultado
    assert len(agregadas) == 1
    assert agregadas[0].qtd_programada == 80
```

## Fixtures

### Uso de Fixtures
```python
# conftest.py
@pytest.fixture
def codigo_ibge_boa_vista() -> CodigoIBGE:
    return CodigoIBGE.create("1400100").value

@pytest.fixture
def interrupcao_programada(codigo_ibge_boa_vista) -> Interrupcao:
    return create_interrupcao(
        municipio=codigo_ibge_boa_vista,
        tipo=TipoInterrupcao.PROGRAMADA,
    )
```

## Cobertura

### Requisitos Minimos
- Cobertura de linhas: >= 80%
- Cobertura de branches: >= 80%

### Comando
```bash
pytest --cov=backend --cov-report=html --cov-fail-under=80
```

## O que Testar

### Testes Unitarios (OBRIGATORIO)
- Value Objects: validacao, igualdade, imutabilidade
- Entities: comportamento de negocio, invariantes
- Domain Services: logica de agregacao/calculo
- Use Cases: orquestracao (com mocks)

### Testes de Integracao
- Repositories: queries reais (com banco de teste)
- Use Cases: fluxo completo sem mocks de infra

### Testes E2E
- Endpoints HTTP: request/response completo
- Autenticacao, validacao, formato de resposta

## Mocks e Stubs

### Quando Usar
- Mocks: Para verificar interacoes (foi chamado?)
- Stubs: Para fornecer dados de teste

```python
from unittest.mock import AsyncMock

@pytest.fixture
def mock_repository():
    repo = AsyncMock(spec=InterrupcaoRepository)
    repo.buscar_ativas.return_value = [create_interrupcao()]
    return repo

async def test_deve_buscar_do_cache_primeiro(mock_repository, mock_cache):
    mock_cache.get.return_value = [create_agregada()]
    use_case = GetInterrupcoesUseCase(mock_repository, mock_cache)

    result = await use_case.execute()

    mock_repository.buscar_ativas.assert_not_called()  # Nao buscou do repo
    mock_cache.get.assert_called_once_with("interrupcoes:ativas")
```
