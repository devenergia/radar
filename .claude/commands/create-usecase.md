---
description: Cria um Use Case seguindo Clean Architecture
argument-hint: [NomeDoUseCase]
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Criar Use Case

Crie um Use Case chamado `$ARGUMENTS` seguindo RIGOROSAMENTE os padroes de Clean Architecture do projeto RADAR.

## Regras Obrigatorias

1. **Localizacao**: `backend/apps/<api>/application/use_cases/$ARGUMENTS.py` (nome em snake_case)

2. **Caracteristicas**:
   - Depende APENAS de abstracoes (Protocol)
   - Recebe dependencias via construtor (DI)
   - Metodo principal: `async execute() -> Result[T]`
   - NAO importa de infrastructure
   - Orquestra chamadas, NAO implementa logica de infra

3. **Template**:
```python
from typing import Generic, TypeVar

from shared.domain.repositories.algum_repository import AlgumRepository
from shared.domain.services.cache_service import CacheService
from shared.domain.result import Result

T = TypeVar("T")


class NomeDoUseCase:
    """Use case para [descricao da acao]."""

    def __init__(
        self,
        repository: AlgumRepository,
        cache: CacheService,
    ) -> None:
        self._repository = repository
        self._cache = cache

    async def execute(self) -> Result[list[Entidade]]:
        """Executa o caso de uso."""
        # 1. Tentar cache primeiro
        cached = await self._cache.get(self._cache_key)
        if cached:
            return Result.ok(cached)

        # 2. Buscar dados
        dados = await self._repository.buscar()

        # 3. Processar/transformar
        processados = self._processar(dados)

        # 4. Salvar em cache
        await self._cache.set(self._cache_key, processados, self._ttl)

        return Result.ok(processados)

    def _processar(self, dados: list) -> list:
        """Processa os dados (metodo privado)."""
        # logica de processamento
        return dados

    @property
    def _cache_key(self) -> str:
        return "minha_chave_cache"

    @property
    def _ttl(self) -> int:
        return 300  # segundos
```

4. **Com Parametros de Input**:
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NomeDoUseCaseInput:
    """Input para o use case."""
    codigo_ibge: str
    data_inicio: str | None = None


class NomeDoUseCase:
    async def execute(self, input_dto: NomeDoUseCaseInput) -> Result[T]:
        # usar input_dto.codigo_ibge etc
        ...
```

5. **Apos criar o Use Case**, crie:
   - Teste em `backend/tests/integration/use_cases/test_$ARGUMENTS.py`
   - Factory function para DI em `backend/apps/<api>/dependencies.py`

## Factory Function para FastAPI
```python
from fastapi import Depends

async def get_$ARGUMENTS_use_case(
    repository: AlgumRepository = Depends(get_repository),
    cache: CacheService = Depends(get_cache),
) -> NomeDoUseCase:
    return NomeDoUseCase(repository, cache)
```

## Referencias
- @docs/development/01-clean-architecture.md
- @docs/development/02-solid-principles.md
- @.claude/rules/clean-architecture.md
