---
name: radar-repository
description: Cria Repositories seguindo o padrao Ports and Adapters para o projeto RADAR. Use quando o usuario pedir para criar um repositorio, repository, acesso a dados, ou implementar persistencia com Oracle, banco de dados, ou queries SQL.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Criacao de Repositories - Projeto RADAR

## Quando Usar

Esta skill e ativada automaticamente quando:
- Usuario pede para criar um "repositorio" ou "repository"
- Usuario quer implementar acesso a dados
- Menciona Oracle, SQL, banco de dados, queries
- Precisa de persistencia ou busca de dados

## Arquitetura

```
Domain (Protocol)          Infrastructure (Implementacao)
     │                              │
     ▼                              ▼
InterrupcaoRepository  ◄──── OracleInterrupcaoRepository
    (Interface)                 (Concreto)
```

## Arquivos a Criar

### 1. Protocol no Domain

**Localizacao**: `backend/shared/domain/repositories/<nome>_repository.py`

```python
from typing import Protocol

from shared.domain.entities.entidade import Entidade
from shared.domain.value_objects.codigo_ibge import CodigoIBGE


class EntidadeRepository(Protocol):
    """Port para repositorio de [descricao]."""

    async def buscar_todos(self) -> list[Entidade]:
        """Busca todos os registros."""
        ...

    async def buscar_ativos(self) -> list[Entidade]:
        """Busca registros ativos."""
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

    async def salvar(self, entidade: Entidade) -> None:
        """Persiste uma entidade."""
        ...
```

### 2. Implementacao Oracle na Infrastructure

**Localizacao**: `backend/apps/<api>/infrastructure/repositories/oracle_<nome>_repository.py`

```python
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.entities.entidade import Entidade
from shared.domain.value_objects.codigo_ibge import CodigoIBGE


class OracleEntidadeRepository:
    """Implementacao Oracle do repositorio de [descricao]."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def buscar_todos(self) -> list[Entidade]:
        """Busca todos os registros."""
        query = """
            SELECT
                id,
                campo1,
                campo2,
                data_criacao
            FROM SCHEMA.TABELA@DBLINK
            ORDER BY data_criacao DESC
        """
        result = await self._session.execute(text(query))
        return [self._map_to_entity(row) for row in result.fetchall()]

    async def buscar_ativos(self) -> list[Entidade]:
        """Busca registros ativos (is_open = 'T')."""
        query = """
            SELECT
                id,
                campo1,
                campo2,
                data_criacao
            FROM SCHEMA.TABELA@DBLINK
            WHERE is_open = 'T'
        """
        result = await self._session.execute(text(query))
        return [self._map_to_entity(row) for row in result.fetchall()]

    async def buscar_por_id(self, id: int) -> Entidade | None:
        """Busca registro por ID."""
        query = """
            SELECT
                id,
                campo1,
                campo2,
                data_criacao
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
            SELECT
                t.id,
                t.campo1,
                t.campo2,
                t.data_criacao
            FROM SCHEMA.TABELA@DBLINK t
            INNER JOIN INDICADORES.IND_UNIVERSOS@DBLINK_INDICADORES u
                ON u.ID_DISPOSITIVO = t.dev_id
                AND u.CD_TIPO_UNIVERSO = 2
            WHERE u.CD_UNIVERSO = :codigo_ibge
        """
        result = await self._session.execute(
            text(query),
            {"codigo_ibge": municipio.valor},
        )
        return [self._map_to_entity(row) for row in result.fetchall()]

    async def salvar(self, entidade: Entidade) -> None:
        """Persiste uma entidade."""
        query = """
            INSERT INTO SCHEMA.TABELA (id, campo1, campo2)
            VALUES (:id, :campo1, :campo2)
        """
        await self._session.execute(
            text(query),
            {
                "id": entidade.id,
                "campo1": entidade.campo1,
                "campo2": entidade.campo2,
            },
        )
        await self._session.commit()

    def _map_to_entity(self, row: tuple) -> Entidade:
        """Converte row do banco para Entity."""
        return Entidade.create({
            "id": row[0],
            "campo1": row[1],
            "campo2": row[2],
            "data_criacao": row[3],
        }).value
```

## Padroes de Query Oracle

### Query com DBLink
```sql
SELECT * FROM SCHEMA.TABELA@DBLINK_NOME
```

### Query com JOIN entre DBLinks
```sql
SELECT ae.*, iu.CD_UNIVERSO
FROM INSERVICE.AGENCY_EVENT@DBLINK_INSERVICE ae
INNER JOIN INDICADORES.IND_UNIVERSOS@DBLINK_INDICADORES iu
    ON iu.ID_DISPOSITIVO = ae.dev_id
```

### Query com Parametros
```python
await self._session.execute(
    text("SELECT * FROM T WHERE id = :id AND status = :status"),
    {"id": 123, "status": "ATIVO"},
)
```

## Dependency Injection

Adicionar em `backend/apps/<api>/dependencies.py`:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .infrastructure.repositories.oracle_entidade_repository import OracleEntidadeRepository


async def get_entidade_repository(
    session: AsyncSession = Depends(get_session),
) -> OracleEntidadeRepository:
    """Factory function para o repositorio."""
    return OracleEntidadeRepository(session)
```

## Checklist de Validacao

### Protocol
- [ ] Arquivo em `backend/shared/domain/repositories/`
- [ ] Usa `Protocol` (nao ABC)
- [ ] Metodos sao async
- [ ] Retorna entidades de dominio (nao dicts)
- [ ] Usa Value Objects nos parametros (CodigoIBGE, etc)

### Implementacao
- [ ] Arquivo em `backend/apps/<api>/infrastructure/repositories/`
- [ ] Construtor recebe `AsyncSession`
- [ ] Queries usam `text()` do SQLAlchemy
- [ ] Parametros passados como dict (evita SQL injection)
- [ ] `_map_to_entity` converte para Entity

## Teste de Integracao

Criar em `backend/tests/integration/repositories/test_oracle_<nome>_repository.py`:

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
class TestOracleEntidadeRepository:
    @pytest.fixture
    async def repository(self, db_session: AsyncSession):
        return OracleEntidadeRepository(db_session)

    async def test_deve_retornar_lista_vazia_quando_nao_ha_dados(
        self,
        repository,
    ):
        result = await repository.buscar_todos()
        assert isinstance(result, list)

    async def test_deve_mapear_campos_corretamente(
        self,
        repository,
    ):
        result = await repository.buscar_ativos()
        if result:
            entidade = result[0]
            assert hasattr(entidade, "id")
            assert isinstance(entidade, Entidade)
```
