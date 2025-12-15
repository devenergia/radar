---
description: Cria um Repository (Protocol + Implementacao) seguindo Clean Architecture
argument-hint: [NomeDoRepository]
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Criar Repository Pattern

Crie um Repository chamado `$ARGUMENTS` com Protocol no dominio e implementacao na infraestrutura.

## Arquivos a Criar

### 1. Protocol (Domain Layer)
**Localizacao**: `backend/shared/domain/repositories/$ARGUMENTS.py`

```python
from typing import Protocol

from shared.domain.entities.entidade import Entidade
from shared.domain.value_objects.codigo_ibge import CodigoIBGE


class $ARGUMENTSRepository(Protocol):
    """Port para repositorio de [descricao]."""

    async def buscar_ativas(self) -> list[Entidade]:
        """Busca todos os registros ativos."""
        ...

    async def buscar_por_id(self, id: int) -> Entidade | None:
        """Busca registro por ID."""
        ...

    async def buscar_por_municipio(
        self,
        municipio: CodigoIBGE,
    ) -> list[Entidade]:
        """Busca registros por municipio."""
        ...
```

### 2. Implementacao Oracle (Infrastructure Layer)
**Localizacao**: `backend/apps/<api>/infrastructure/repositories/oracle_$ARGUMENTS.py`

```python
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.entities.entidade import Entidade
from shared.domain.value_objects.codigo_ibge import CodigoIBGE


class Oracle$ARGUMENTSRepository:
    """Implementacao Oracle do repositorio."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def buscar_ativas(self) -> list[Entidade]:
        """Busca todos os registros ativos."""
        query = """
            SELECT id, campo1, campo2
            FROM SCHEMA.TABELA@DBLINK
            WHERE is_open = 'T'
        """
        result = await self._session.execute(text(query))
        return [self._map_to_entity(row) for row in result.fetchall()]

    async def buscar_por_id(self, id: int) -> Entidade | None:
        """Busca registro por ID."""
        query = """
            SELECT id, campo1, campo2
            FROM SCHEMA.TABELA@DBLINK
            WHERE id = :id
        """
        result = await self._session.execute(text(query), {"id": id})
        row = result.fetchone()
        return self._map_to_entity(row) if row else None

    async def buscar_por_municipio(
        self,
        municipio: CodigoIBGE,
    ) -> list[Entidade]:
        """Busca registros por municipio."""
        query = """
            SELECT id, campo1, campo2
            FROM SCHEMA.TABELA@DBLINK
            WHERE codigo_ibge = :ibge
        """
        result = await self._session.execute(
            text(query),
            {"ibge": municipio.valor},
        )
        return [self._map_to_entity(row) for row in result.fetchall()]

    def _map_to_entity(self, row: tuple) -> Entidade:
        """Converte row do banco para Entity."""
        return Entidade.create({
            "id": row[0],
            "campo1": row[1],
            "campo2": row[2],
        }).value
```

### 3. Teste de Integracao
**Localizacao**: `backend/tests/integration/repositories/test_oracle_$ARGUMENTS.py`

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
class TestOracle$ARGUMENTSRepository:
    @pytest.fixture
    async def repository(self, db_session: AsyncSession):
        return Oracle$ARGUMENTSRepository(db_session)

    async def test_deve_retornar_lista_vazia_quando_nao_ha_dados(
        self,
        repository,
    ):
        result = await repository.buscar_ativas()
        assert isinstance(result, list)

    async def test_deve_mapear_corretamente_campos_do_banco(
        self,
        repository,
    ):
        result = await repository.buscar_ativas()
        if result:
            assert hasattr(result[0], "id")
```

## Dependency Injection
Adicione em `backend/apps/<api>/dependencies.py`:

```python
async def get_$ARGUMENTS_repository(
    session: AsyncSession = Depends(get_session),
) -> Oracle$ARGUMENTSRepository:
    return Oracle$ARGUMENTSRepository(session)
```

## Referencias
- @docs/development/01-clean-architecture.md
- @docs/development/03-domain-driven-design.md
- @.claude/rules/clean-architecture.md
