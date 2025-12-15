---
paths: backend/**/*.py
---

# SOLID Principles Rules

## S - Single Responsibility Principle

### Regra
Uma classe deve ter apenas UMA razao para mudar.

### Validacao
- Classes com mais de 200 linhas provavelmente violam SRP
- Metodos que fazem mais de uma coisa devem ser divididos
- Se o nome da classe contem "And" ou "Manager", reconsidere

### Exemplo Correto
```python
# Cada classe tem uma responsabilidade
class InterrupcaoRepository(Protocol):
    """Responsabilidade: Acesso a dados"""
    async def buscar_ativas(self) -> list[Interrupcao]: ...

class InterrupcaoMapper:
    """Responsabilidade: Conversao de dados"""
    def to_entity(self, row: tuple) -> Interrupcao: ...

class InterrupcaoAggregatorService:
    """Responsabilidade: Logica de agregacao"""
    def agregar(self, items: list[Interrupcao]) -> list[InterrupcaoAgregada]: ...
```

## O - Open/Closed Principle

### Regra
Aberto para extensao, fechado para modificacao.

### Validacao
- Use Protocol para definir interfaces
- Novas implementacoes NAO devem exigir alteracao de codigo existente
- Evite `if/elif` chains para tipos - use polimorfismo

### Exemplo Correto
```python
class ResponseFormatter(Protocol):
    def format(self, data: list) -> str: ...

class AneelFormatter:
    def format(self, data: list) -> str:
        return json.dumps({"idcStatusRequisicao": 1, ...})

class CsvFormatter:  # Extensao sem modificar existente
    def format(self, data: list) -> str:
        return "header\n" + "\n".join(...)
```

## L - Liskov Substitution Principle

### Regra
Subtipos devem ser substituiveis por seus tipos base.

### Validacao
- Implementacoes de Protocol devem respeitar o contrato
- NAO lance excecoes diferentes das esperadas
- NAO retorne tipos diferentes dos especificados

### Exemplo
```python
class CacheService(Protocol):
    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, ttl: int) -> None: ...

# Ambas implementacoes sao intercambiaveis
class MemoryCacheService:
    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, ttl: int) -> None: ...

class RedisCacheService:
    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, ttl: int) -> None: ...
```

## I - Interface Segregation Principle

### Regra
Interfaces pequenas e focadas.

### Validacao
- Protocols NAO devem ter mais de 5-7 metodos
- Se uma classe usa apenas parte do Protocol, divida-o
- Evite "god interfaces"

### Exemplo Correto
```python
# CORRETO: Interfaces segregadas
class InterrupcaoReader(Protocol):
    async def buscar_ativas(self) -> list[Interrupcao]: ...
    async def buscar_por_municipio(self, ibge: CodigoIBGE) -> list[Interrupcao]: ...

class InterrupcaoWriter(Protocol):
    async def salvar(self, interrupcao: Interrupcao) -> None: ...

# INCORRETO: Interface muito grande
class InterrupcaoRepository(Protocol):
    async def buscar_ativas(self) -> list[Interrupcao]: ...
    async def buscar_por_municipio(self, ibge: CodigoIBGE) -> list[Interrupcao]: ...
    async def salvar(self, interrupcao: Interrupcao) -> None: ...
    async def deletar(self, id: int) -> None: ...
    async def atualizar(self, interrupcao: Interrupcao) -> None: ...
    async def buscar_historico(self, params: dict) -> list[Interrupcao]: ...
    async def contar(self) -> int: ...
    async def existir(self, id: int) -> bool: ...
```

## D - Dependency Inversion Principle

### Regra
Dependa de abstracoes (Protocol), NAO de implementacoes concretas.

### Validacao
- Use Cases recebem Protocols via construtor
- NAO instancie dependencias diretamente
- Imports de classes concretas apenas na composicao (main/factory)

### Exemplo Correto
```python
# Use Case depende de Protocol
class GetInterrupcoesUseCase:
    def __init__(
        self,
        repository: InterrupcaoRepository,  # Protocol
        cache: CacheService,  # Protocol
    ) -> None:
        self._repository = repository
        self._cache = cache

# Composicao na factory/main
def create_use_case(session: AsyncSession) -> GetInterrupcoesUseCase:
    return GetInterrupcoesUseCase(
        repository=OracleInterrupcaoRepository(session),  # Implementacao
        cache=MemoryCacheService(),  # Implementacao
    )
```
