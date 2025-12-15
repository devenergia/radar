---
paths: backend/**/*.py
---

# Clean Code Rules

## Nomes Significativos

### Regras
- Nomes revelam intencao
- Nomes sao pronunciaveis e pesquisaveis
- Classes = substantivos (`Interrupcao`, `CodigoIBGE`)
- Metodos = verbos (`buscar_ativas`, `is_programada`)
- Use nomes em portugues para termos de dominio

### Exemplos
```python
# RUIM
d = datetime.now()
t = 5
def get_int(ibge: int) -> list: ...

# BOM
data_inicio_interrupcao = datetime.now()
ttl_cache_em_minutos = 5
def buscar_interrupcoes_por_municipio(codigo_ibge: CodigoIBGE) -> list[Interrupcao]: ...
```

## Funcoes

### Regras
- Funcoes pequenas: < 20 linhas
- Fazem apenas UMA coisa
- Um nivel de abstracao por funcao
- Poucos argumentos: < 3 (use dataclass para muitos parametros)
- Sem efeitos colaterais ocultos

### Exemplo
```python
# RUIM - Faz muitas coisas
async def processar_requisicao(request):
    # validar
    # buscar dados
    # processar
    # formatar
    # retornar

# BOM - Cada funcao faz uma coisa
async def processar_requisicao(request):
    await self._validar(request)
    dados = await self._buscar_dados()
    processados = self._processar(dados)
    return self._formatar(processados)
```

## Comentarios

### Evitar
- Comentarios obvios
- Comentarios desatualizados
- Codigo comentado (delete!)

### Aceitavel
- Docstrings em APIs publicas
- Explicacao de regras de negocio complexas
- Warnings importantes

```python
# RUIM
# Incrementa contador
contador += 1

# BOM - Explica regra de negocio
def from_plan_id(plan_id: int | None) -> TipoInterrupcao:
    """
    Determina tipo de interrupcao baseado na existencia de PLAN_ID.
    Fonte: Oficio Circular 14/2025-SFE/ANEEL
    """
    return TipoInterrupcao.PROGRAMADA if plan_id else TipoInterrupcao.NAO_PROGRAMADA
```

## Formatacao

### Regras
- Linhas curtas: < 100 caracteres
- Agrupamento logico com espacamento
- Indentacao consistente (4 espacos)
- Use `ruff format` para formatacao automatica

## Tratamento de Erros

### Use Result Pattern
```python
# RUIM - Dict com status
def buscar() -> dict:
    try:
        return {"success": True, "data": ...}
    except:
        return {"success": False, "error": ...}

# BOM - Result Pattern
async def buscar_ativas(self) -> Result[list[Interrupcao]]:
    try:
        dados = await self._fetch()
        return Result.ok(dados)
    except DatabaseError as e:
        return Result.fail(f"Erro ao buscar: {e}")
```

### Exceptions com Contexto
```python
class DomainError(Exception):
    def __init__(self, message: str, code: str, context: dict | None = None):
        super().__init__(message)
        self.code = code
        self.context = context or {}

class CodigoIbgeInvalidoError(DomainError):
    def __init__(self, codigo: str):
        super().__init__(
            message=f"Codigo IBGE invalido: {codigo}",
            code="IBGE_INVALIDO",
            context={"codigo": codigo},
        )
```

## Classes

### Regras
- Pequenas e coesas
- Responsabilidade unica
- Dependencias injetadas via construtor
- Baixo acoplamento

```python
class GetInterrupcoesAtivasUseCase:
    """Use case coeso - faz apenas uma coisa."""

    def __init__(
        self,
        repository: InterrupcaoRepository,
        cache: CacheService,
    ) -> None:
        self._repository = repository
        self._cache = cache

    async def execute(self) -> Result[list[InterrupcaoAgregada]]:
        cached = await self._cache.get("interrupcoes:ativas")
        if cached:
            return Result.ok(cached)

        interrupcoes = await self._repository.buscar_ativas()
        # ... restante da logica
```

## Checklist Pre-Commit

- [ ] Nomes revelam intencao?
- [ ] Funcoes < 20 linhas?
- [ ] Funcoes fazem apenas uma coisa?
- [ ] Sem comentarios obvios?
- [ ] Result Pattern para erros?
- [ ] `ruff check` sem warnings?
- [ ] `mypy` sem erros?
