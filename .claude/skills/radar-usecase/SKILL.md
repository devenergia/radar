---
name: radar-usecase
description: Cria Use Cases seguindo Clean Architecture para o projeto RADAR. Use quando o usuario pedir para criar um use case, caso de uso, implementar uma funcionalidade, ou criar logica de aplicacao como buscar interrupcoes, processar demandas, ou orquestrar operacoes.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Criacao de Use Cases - Projeto RADAR

## Quando Usar

Esta skill e ativada automaticamente quando:
- Usuario pede para criar um "use case" ou "caso de uso"
- Usuario quer implementar uma funcionalidade de negocio
- Menciona operacoes como "buscar", "processar", "calcular"
- Precisa orquestrar chamadas entre repositorios e servicos

## Regras Obrigatorias

### Localizacao
```
backend/apps/<api>/application/use_cases/<nome_snake_case>.py
```

### Caracteristicas de um Use Case
1. Depende APENAS de abstracoes (Protocol)
2. Recebe dependencias via construtor (DI)
3. Metodo principal: `async execute() -> Result[T]`
4. NAO importa de infrastructure
5. Orquestra chamadas, NAO implementa logica de infra

## Template Principal

```python
from dataclasses import dataclass
from typing import Any

from shared.domain.entities.entidade import Entidade
from shared.domain.repositories.entidade_repository import EntidadeRepository
from shared.domain.services.cache_service import CacheService
from shared.domain.result import Result


@dataclass(frozen=True)
class NomeUseCaseInput:
    """Input DTO para o use case (opcional)."""
    filtro: str | None = None


class NomeUseCase:
    """
    Use case para [descricao da operacao].

    Responsabilidades:
    - Buscar dados do repositorio
    - Aplicar regras de negocio
    - Gerenciar cache
    """

    CACHE_KEY = "nome_use_case:dados"
    CACHE_TTL_SECONDS = 300

    def __init__(
        self,
        repository: EntidadeRepository,
        cache: CacheService,
    ) -> None:
        self._repository = repository
        self._cache = cache

    async def execute(
        self,
        input_dto: NomeUseCaseInput | None = None,
    ) -> Result[list[Entidade]]:
        """Executa o caso de uso."""
        # 1. Tentar buscar do cache
        cached = await self._try_get_from_cache()
        if cached is not None:
            return Result.ok(cached)

        # 2. Buscar do repositorio
        dados = await self._fetch_from_repository(input_dto)

        # 3. Aplicar regras de negocio/transformacoes
        processados = self._process(dados)

        # 4. Salvar no cache
        await self._save_to_cache(processados)

        return Result.ok(processados)

    async def _try_get_from_cache(self) -> list[Entidade] | None:
        """Tenta buscar dados do cache."""
        return await self._cache.get(self.CACHE_KEY)

    async def _fetch_from_repository(
        self,
        input_dto: NomeUseCaseInput | None,
    ) -> list[Entidade]:
        """Busca dados do repositorio."""
        if input_dto and input_dto.filtro:
            return await self._repository.buscar_por_filtro(input_dto.filtro)
        return await self._repository.buscar_todos()

    def _process(self, dados: list[Entidade]) -> list[Entidade]:
        """Aplica regras de negocio."""
        # Exemplo: filtrar apenas ativos
        return [d for d in dados if d.is_ativo()]

    async def _save_to_cache(self, dados: list[Entidade]) -> None:
        """Salva dados no cache."""
        await self._cache.set(self.CACHE_KEY, dados, self.CACHE_TTL_SECONDS)
```

## Imports Permitidos/Proibidos

```python
# PERMITIDO - Domain layer
from shared.domain.entities.interrupcao import Interrupcao
from shared.domain.repositories.interrupcao_repository import InterrupcaoRepository
from shared.domain.services.aggregator_service import AggregatorService
from shared.domain.result import Result

# PROIBIDO - Infrastructure layer
# from infrastructure.repositories.oracle_repository import OracleRepository  # NUNCA!
# from sqlalchemy import Session  # NUNCA!
# from fastapi import Depends  # NUNCA!
```

## Factory Function para DI

Adicionar em `backend/apps/<api>/dependencies.py`:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .application.use_cases.nome_use_case import NomeUseCase
from .infrastructure.repositories.oracle_entidade_repository import OracleEntidadeRepository
from shared.infrastructure.cache.memory_cache import MemoryCacheService


async def get_nome_use_case(
    session: AsyncSession = Depends(get_session),
    cache: CacheService = Depends(get_cache),
) -> NomeUseCase:
    """Factory function para injecao de dependencias."""
    return NomeUseCase(
        repository=OracleEntidadeRepository(session),
        cache=cache,
    )
```

## Checklist de Validacao

- [ ] Arquivo em `backend/apps/<api>/application/use_cases/`
- [ ] Depende apenas de Protocols (nao de implementacoes)
- [ ] Metodo `execute()` e async e retorna `Result`
- [ ] Construtor recebe dependencias (DI)
- [ ] NAO importa de infrastructure
- [ ] Metodos privados bem nomeados
- [ ] Cache key e TTL definidos como constantes

## Teste de Integracao

Criar em `backend/tests/integration/use_cases/test_<nome>.py`:

```python
import pytest
from unittest.mock import AsyncMock


@pytest.mark.integration
class TestNomeUseCase:
    @pytest.fixture
    def mock_repository(self):
        repo = AsyncMock(spec=EntidadeRepository)
        repo.buscar_todos.return_value = []
        return repo

    @pytest.fixture
    def mock_cache(self):
        cache = AsyncMock(spec=CacheService)
        cache.get.return_value = None
        return cache

    @pytest.fixture
    def use_case(self, mock_repository, mock_cache):
        return NomeUseCase(mock_repository, mock_cache)

    async def test_deve_buscar_do_cache_primeiro(self, use_case, mock_cache):
        dados_cached = [create_entidade()]
        mock_cache.get.return_value = dados_cached

        result = await use_case.execute()

        assert result.is_success
        assert result.value == dados_cached

    async def test_deve_buscar_do_repo_quando_cache_vazio(self, use_case, mock_repository):
        result = await use_case.execute()

        mock_repository.buscar_todos.assert_called_once()
```

## Exemplos do Projeto

- `GetInterrupcoesAtivasUseCase` - Busca interrupcoes ativas com cache
- `GetDemandaPorMunicipioUseCase` - Busca demandas filtradas por municipio
