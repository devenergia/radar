# Oracle Database - Guia de Conexão e Boas Práticas

Este documento descreve as melhores práticas para conexão com banco de dados Oracle no projeto RADAR.

## Visão Geral

O projeto RADAR utiliza Oracle Database como banco de dados principal, conectando-se via DBLinks aos sistemas INSERVICE e INDICADORES.

## Stack de Tecnologias

- **Driver**: `oracledb` (python-oracledb)
- **ORM**: SQLAlchemy 2.0+
- **Dialect**: `oracle+oracledb`

## Configuração de Conexão

### Variáveis de Ambiente

```env
# Configuração Multi-Ambiente
# O sistema detecta automaticamente o ambiente e usa o prefixo correto

# Desenvolvimento
DEV_ORACLE_USER=radar_api
DEV_ORACLE_PASSWORD=senha_dev
DEV_ORACLE_DSN=localhost:1521/RADARDEV

# Homologação
HM_ORACLE_USER=radar_api
HM_ORACLE_PASSWORD=senha_hm
HM_ORACLE_DSN=servidor_hm:1521/RADARHM

# Produção
PRD_ORACLE_USER=radar_api
PRD_ORACLE_PASSWORD=senha_prd
PRD_ORACLE_DSN=servidor_prd:1521/RADARPRD

# Fallback (quando não há prefixo de ambiente)
ORACLE_USER=radar_api
ORACLE_PASSWORD=senha
ORACLE_DSN=localhost:1521/RADARDB
```

### Estrutura do DSN

O DSN (Data Source Name) pode ser configurado de duas formas:

1. **Easy Connect**: `host:port/service_name`
   ```
   ORACLE_DSN=dbserver.empresa.com:1521/RADARDB
   ```

2. **TNS Names**: Nome configurado no `tnsnames.ora`
   ```
   ORACLE_DSN=RADARDB
   ```

## Implementação

### Engine Factory

```python
from sqlalchemy import create_engine, Engine
from typing import Optional
import os

def get_environment() -> str:
    """Detecta o ambiente atual baseado em variáveis de ambiente."""
    env = os.getenv('ENVIRONMENT', 'development').lower()

    env_map = {
        'development': 'DEV',
        'dev': 'DEV',
        'homologation': 'HM',
        'hm': 'HM',
        'staging': 'HM',
        'production': 'PRD',
        'prd': 'PRD',
        'prod': 'PRD'
    }

    return env_map.get(env, 'DEV')

def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Busca variável de ambiente com suporte a prefixo de ambiente.

    Ordem de prioridade:
    1. {ENV}_{NAME} (ex: PRD_ORACLE_DSN)
    2. {NAME} (ex: ORACLE_DSN)
    3. default
    """
    env_prefix = get_environment()

    # Tenta com prefixo do ambiente
    prefixed_value = os.getenv(f'{env_prefix}_{name}')
    if prefixed_value:
        return prefixed_value

    # Fallback para variável sem prefixo
    return os.getenv(name, default)

def create_oracle_engine(
    pool_size: int = 20,
    max_overflow: int = 10,
    pool_timeout: int = 30,
    pool_recycle: int = 1800
) -> Engine:
    """
    Cria engine SQLAlchemy para Oracle com pool de conexões otimizado.

    Args:
        pool_size: Número de conexões mantidas no pool (default: 20)
        max_overflow: Conexões extras permitidas além do pool_size (default: 10)
        pool_timeout: Segundos para aguardar conexão disponível (default: 30)
        pool_recycle: Segundos para reciclar conexões (default: 1800 = 30min)

    Returns:
        Engine SQLAlchemy configurado para Oracle
    """
    user = get_env_var('ORACLE_USER')
    password = get_env_var('ORACLE_PASSWORD')
    dsn = get_env_var('ORACLE_DSN')

    if not all([user, password, dsn]):
        raise ValueError(
            "Configuração Oracle incompleta. "
            "Defina ORACLE_USER, ORACLE_PASSWORD e ORACLE_DSN"
        )

    # URL de conexão usando dialect oracle+oracledb
    database_url = f"oracle+oracledb://{user}:{password}@{dsn}"

    # Configuração do debug baseado no ambiente
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'

    engine = create_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        pool_pre_ping=True,  # Valida conexões antes de usar
        echo=debug_mode      # SQL logging em modo debug
    )

    return engine
```

## Pool de Conexões

### Parâmetros Recomendados

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `pool_size` | 20 | Conexões mantidas abertas |
| `max_overflow` | 10 | Conexões extras em pico |
| `pool_timeout` | 30 | Timeout para obter conexão |
| `pool_recycle` | 1800 | Recicla após 30 minutos |
| `pool_pre_ping` | True | **Obrigatório** - Valida conexões |

### Por que `pool_pre_ping=True`?

Este parâmetro é **essencial** para ambientes de produção:

1. **Detecta conexões mortas**: Conexões podem ser fechadas pelo firewall ou pelo banco
2. **Evita erros de "stale connection"**: Garante que a conexão está ativa antes de usar
3. **Custo mínimo**: Adiciona apenas um `SELECT 1` antes de cada operação
4. **Auto-recuperação**: SQLAlchemy automaticamente reconecta se necessário

```python
# Sem pool_pre_ping - ERRO em produção
engine = create_engine(url)  # Conexão pode estar morta

# Com pool_pre_ping - SEGURO
engine = create_engine(url, pool_pre_ping=True)  # Sempre valida
```

## Execução de Queries

### Query Síncrona

```python
from sqlalchemy import text

def execute_query(engine: Engine, sql: str, params: dict = None):
    """Executa query síncrona com tratamento de erro."""
    with engine.connect() as connection:
        result = connection.execute(text(sql), params or {})
        return result.fetchall()
```

### Query com DBLink

```python
# Exemplo de query usando DBLink para INSERVICE
SQL_INTERRUPCOES = """
    SELECT
        i.id_conjunto,
        i.cod_municipio_ibge,
        i.qtd_ucs,
        i.qtd_programada,
        i.qtd_nao_programada
    FROM
        interrupcoes_ativas i
    WHERE
        i.data_referencia = :data_ref

    UNION ALL

    SELECT
        ins.id_conjunto,
        ins.cod_municipio,
        ins.total_ucs,
        ins.prog,
        ins.nao_prog
    FROM
        tab_ocorrencias@INSERVICE ins
    WHERE
        ins.dt_ref = :data_ref
"""
```

## Wrapper Assíncrono

Para uso com FastAPI (que é assíncrono), utilize um wrapper:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# Pool de threads para operações de banco
_executor = ThreadPoolExecutor(max_workers=10)

async def run_in_executor(func, *args, **kwargs):
    """Executa função síncrona em thread separada."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        partial(func, *args, **kwargs)
    )

# Uso no FastAPI
async def get_interrupcoes_async(engine: Engine):
    def _query():
        with engine.connect() as conn:
            result = conn.execute(text(SQL_INTERRUPCOES))
            return result.fetchall()

    return await run_in_executor(_query)
```

## Tratamento de Erros

```python
from sqlalchemy.exc import (
    OperationalError,
    DatabaseError,
    InterfaceError
)

def execute_with_retry(engine: Engine, sql: str, max_retries: int = 3):
    """Executa query com retry automático."""
    last_error = None

    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                return result.fetchall()

        except (OperationalError, InterfaceError) as e:
            last_error = e
            logger.warning(
                f"Tentativa {attempt + 1}/{max_retries} falhou: {e}"
            )
            continue

        except DatabaseError as e:
            # Erros de SQL não devem fazer retry
            raise

    raise last_error
```

## Health Check

```python
def check_database_health(engine: Engine) -> dict:
    """Verifica saúde da conexão com o banco."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM DUAL"))
            result.fetchone()

        return {
            "status": "healthy",
            "database": "oracle",
            "pool_size": engine.pool.size(),
            "checked_out": engine.pool.checkedout()
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "oracle",
            "error": str(e)
        }
```

## Segurança

### Proteção contra SQL Injection

**SEMPRE** use parâmetros nomeados:

```python
# ERRADO - Vulnerável a SQL Injection
sql = f"SELECT * FROM users WHERE id = {user_id}"

# CORRETO - Parâmetros seguros
sql = "SELECT * FROM users WHERE id = :user_id"
result = conn.execute(text(sql), {"user_id": user_id})
```

### Credenciais

1. **Nunca** commite credenciais no código
2. Use variáveis de ambiente ou vault
3. Rotacione senhas periodicamente
4. Use usuários com **mínimo privilégio**

## Referências

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [python-oracledb Documentation](https://python-oracledb.readthedocs.io/)
- [Oracle Connection Pooling Best Practices](https://docs.oracle.com/en/database/)
