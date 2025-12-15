# Clean Code - Projeto RADAR

## Visao Geral

Clean Code sao praticas que tornam o codigo legivel, mantenivel e expressivo. O codigo deve comunicar sua intencao claramente.

> "Qualquer tolo pode escrever codigo que um computador entenda. Bons programadores escrevem codigo que humanos entendem." - Martin Fowler

---

## Nomes Significativos

### Nomes Reveladores de Intencao

```python
# RUIM - O que significa 'd' e 't'?
d = datetime.now()
t = 5

# BOM - Intencao clara
data_inicio_interrupcao = datetime.now()
ttl_cache_em_minutos = 5
```

```python
# RUIM - Abreviacoes confusas
def get_int_agg(ibge: int) -> list:
    pass

# BOM - Nome completo e descritivo
def get_interrupcoes_agregadas_por_municipio(
    codigo_ibge: CodigoIBGE,
) -> list[InterrupcaoAgregada]:
    pass
```

### Nomes Pronunciaveis e Pesquisaveis

```python
# RUIM - Impronunciavel e dificil de buscar
ymdhms = datetime.now()
uc = 150

# BOM - Pronunciavel e facil de encontrar
data_hora_formato_brasilia = datetime.now()
unidades_consumidoras_afetadas = 150
```

### Nomes de Classes e Metodos

```python
# Classes: Substantivos no singular
class Interrupcao:
    pass

class CodigoIBGE:
    pass

class InterrupcaoRepository(Protocol):
    pass


# Metodos: Verbos que descrevem acao
class InterrupcaoRepository(Protocol):
    async def buscar_ativas(self) -> list[Interrupcao]:
        ...

    async def buscar_por_municipio(self, ibge: CodigoIBGE) -> list[Interrupcao]:
        ...


# Use Cases: Verbo + Substantivo
class GetInterrupcoesAtivasUseCase:
    pass

class ValidarCodigoIbgeUseCase:
    pass
```

---

## Funcoes

### Funcoes Pequenas

```python
# RUIM - Funcao faz muitas coisas
async def processar_requisicao(request: Request) -> Response:
    # Validar autenticacao
    api_key = request.headers.get("x-api-key")
    if not api_key:
        raise HTTPException(status_code=401)
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401)

    # Buscar dados
    async with get_connection() as conn:
        result = await conn.execute(text("SELECT ..."))
        rows = result.fetchall()

    # Processar dados
    interrupcoes = [
        {"id": row[0], "tipo": "PROGRAMADA" if row[1] else "NAO_PROGRAMADA"}
        for row in rows
    ]

    # Agregar
    agregadas = {}
    for i in interrupcoes:
        # logica de agregacao...
        pass

    # Formatar resposta
    return {
        "idcStatusRequisicao": 1,
        "listaInterrupcoes": list(agregadas.values()),
    }


# BOM - Cada funcao faz uma coisa
async def processar_requisicao(request: Request) -> Response:
    await self.auth_middleware.validar(request)
    interrupcoes = await self.repository.buscar_ativas()
    agregadas = self.aggregator.agregar(interrupcoes)
    return self.formatter.formatar_resposta(agregadas)
```

### Um Nivel de Abstracao por Funcao

```python
# BOM - Mesmo nivel de abstracao
class GetInterrupcoesAtivasUseCase:
    async def execute(self) -> Result[list[InterrupcaoAgregada]]:
        cacheado = await self._tentar_buscar_do_cache()
        if cacheado:
            return cacheado

        dados = await self._buscar_do_banco()
        agregados = self._agregar(dados)
        await self._salvar_no_cache(agregados)

        return Result.ok(agregados)

    async def _tentar_buscar_do_cache(self) -> list[InterrupcaoAgregada] | None:
        return await self._cache.get("interrupcoes:ativas")

    async def _buscar_do_banco(self) -> list[Interrupcao]:
        return await self._repository.buscar_ativas()

    def _agregar(self, interrupcoes: list[Interrupcao]) -> list[InterrupcaoAgregada]:
        return self._aggregator_service.agregar(interrupcoes)

    async def _salvar_no_cache(self, dados: list[InterrupcaoAgregada]) -> None:
        await self._cache.set("interrupcoes:ativas", dados, self._ttl_em_segundos)
```

### Poucos Argumentos

```python
# RUIM - Muitos argumentos
def criar_interrupcao(
    id: int,
    tipo: str,
    municipio: int,
    conjunto: int,
    ucs: int,
    data_inicio: datetime,
    data_fim: datetime | None,
    ativa: bool,
) -> Interrupcao:
    pass


# BOM - Dataclass para parametros
@dataclass
class CriarInterrupcaoParams:
    id: int
    tipo: TipoInterrupcao
    municipio: CodigoIBGE
    conjunto: int
    ucs_afetadas: int
    data_inicio: datetime
    data_fim: datetime | None = None


def criar_interrupcao(params: CriarInterrupcaoParams) -> Interrupcao:
    pass


# Uso
interrupcao = criar_interrupcao(
    CriarInterrupcaoParams(
        id=12345,
        tipo=TipoInterrupcao.PROGRAMADA,
        municipio=CodigoIBGE.create("1400100").value,
        conjunto=1,
        ucs_afetadas=150,
        data_inicio=datetime.now(),
    )
)
```

---

## Comentarios

### Comentarios que Evitar

```python
# RUIM - Comentario obvio
# Incrementa contador
contador += 1

# RUIM - Comentario desatualizado
# Retorna lista de interrupcoes ativas
# TODO: adicionar filtro por data
def buscar_ativas() -> list[Interrupcao]:
    pass

# RUIM - Comentario ao inves de codigo claro
# Verifica se a interrupcao e programada checando
# se o PLAN_ID e diferente de null
if plan_id is not None:
    pass
```

### Comentarios Aceitaveis

```python
# BOM - Explica regra de negocio complexa
def from_plan_id(plan_id: int | None) -> TipoInterrupcao:
    """
    Determina tipo de interrupcao baseado na existencia de PLAN_ID.

    Uma interrupcao e classificada como PROGRAMADA quando existe
    um registro associado na tabela SWITCH_PLAN_TASKS.

    Fonte: Oficio Circular 14/2025-SFE/ANEEL
    """
    return (
        TipoInterrupcao.PROGRAMADA
        if plan_id is not None
        else TipoInterrupcao.NAO_PROGRAMADA
    )


# BOM - Documenta API publica
async def buscar_ativas(self) -> list[Interrupcao]:
    """
    Busca todas as interrupcoes ativas no momento.

    Returns:
        Lista de interrupcoes com is_open = 'T'
    """
    pass


# BOM - Aviso importante
# WARNING: DBLink pode ter latencia alta em horarios de pico
result = await self._session.execute(text(query))
```

---

## Formatacao

### Formatacao Vertical

```python
# BOM - Agrupamento logico com espacamento
class GetInterrupcoesAtivasUseCase:
    """Caso de uso para buscar interrupcoes ativas."""

    # Dependencias
    _repository: InterrupcaoRepository
    _cache: CacheService
    _aggregator: InterrupcaoAggregatorService

    # Configuracao
    _ttl_cache_segundos: int = 300
    _cache_key: str = "interrupcoes:ativas"

    def __init__(
        self,
        repository: InterrupcaoRepository,
        cache: CacheService,
        aggregator: InterrupcaoAggregatorService,
    ) -> None:
        self._repository = repository
        self._cache = cache
        self._aggregator = aggregator

    # Metodo principal
    async def execute(self) -> Result[list[InterrupcaoAgregada]]:
        cached = await self._cache.get(self._cache_key)
        if cached:
            return Result.ok(cached)

        interrupcoes = await self._repository.buscar_ativas()
        agregadas = self._aggregator.agregar(interrupcoes)

        await self._cache.set(self._cache_key, agregadas, self._ttl_cache_segundos)

        return Result.ok(agregadas)
```

### Formatacao Horizontal

```python
# BOM - Linhas nao muito longas (max ~100 caracteres)
interrupcao_agregada = InterrupcaoAgregada.create(
    id_conjunto=conjunto,
    municipio=CodigoIBGE.create(codigo_ibge).value,
    qtd_ucs_atendidas=total_ucs,
    qtd_programada=soma_programada,
    qtd_nao_programada=soma_nao_programada,
)

# BOM - Query SQL formatada
query = """
    SELECT
        ae.num_1 AS id,
        ae.NUM_CUST AS ucs_afetadas,
        spt.PLAN_ID AS plan_id,
        oc.conj AS conjunto,
        iu.CD_UNIVERSO AS codigo_ibge
    FROM INSERVICE.AGENCY_EVENT@DBLINK_INSERVICE ae
    LEFT JOIN INSERVICE.SWITCH_PLAN_TASKS@DBLINK_INSERVICE spt
        ON spt.OUTAGE_NUM = ae.num_1
    INNER JOIN INSERVICE.OMS_CONNECTIVITY@DBLINK_INSERVICE oc
        ON oc.mslink = ae.dev_id
    INNER JOIN INDICADORES.IND_UNIVERSOS@DBLINK_INDICADORES iu
        ON iu.ID_DISPOSITIVO = ae.dev_id
        AND iu.CD_TIPO_UNIVERSO = 2
    WHERE ae.is_open = 'T'
        AND ae.ag_id = 370
"""
```

---

## Tratamento de Erros

### Use Result Pattern, Nao Codigos de Retorno

```python
# RUIM - Dicionario com status
def buscar_ativas() -> dict:
    try:
        data = ...  # buscar
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


# BOM - Result Pattern
from shared.domain.result import Result


async def buscar_ativas(self) -> Result[list[Interrupcao]]:
    try:
        interrupcoes = await self._fetch_from_db()
        return Result.ok(interrupcoes)
    except DatabaseError as e:
        return Result.fail(f"Erro ao buscar interrupcoes: {e}")


# Uso
result = await repository.buscar_ativas()
if result.is_failure:
    logger.error("Falha ao buscar interrupcoes", error=result.error)
    return self._handle_error(result.error)

interrupcoes = result.value
```

### Exceptions com Contexto

```python
# shared/domain/errors.py
class DomainError(Exception):
    """Erro base do dominio."""

    def __init__(
        self,
        message: str,
        code: str,
        context: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.context = context or {}


class CodigoIbgeInvalidoError(DomainError):
    """Erro quando codigo IBGE e invalido."""

    def __init__(self, codigo: str) -> None:
        super().__init__(
            message=f"Codigo IBGE invalido: {codigo}",
            code="IBGE_INVALIDO",
            context={
                "codigo": codigo,
                "esperado": "Codigo de 7 digitos de Roraima (14xxxxx)",
            },
        )


class DatabaseConnectionError(DomainError):
    """Erro de conexao com banco de dados."""

    def __init__(self, original_error: Exception) -> None:
        super().__init__(
            message="Falha na conexao com banco de dados",
            code="DB_CONNECTION_ERROR",
            context={"original_message": str(original_error)},
        )
```

---

## Classes

### Principio da Responsabilidade Unica

```python
# Uma classe, uma responsabilidade
class InterrupcaoMapper:
    """Responsabilidade: Converter entre camadas."""

    def to_entity(self, row: tuple) -> Interrupcao:
        ...

    def to_dto(self, entity: Interrupcao) -> InterrupcaoDTO:
        ...

    def to_aneel_response(self, dto: InterrupcaoDTO) -> dict:
        ...


class InterrupcaoValidator:
    """Responsabilidade: Validar dados."""

    def validate_codigo_ibge(self, codigo: str) -> Result[None]:
        ...

    def validate_ucs_afetadas(self, ucs: int) -> Result[None]:
        ...


class InterrupcaoAggregatorService:
    """Responsabilidade: Agregar interrupcoes."""

    def agregar(self, interrupcoes: list[Interrupcao]) -> list[InterrupcaoAgregada]:
        ...
```

### Coesao Alta

```python
# BOM - Todos os metodos usam os mesmos dados
@dataclass(frozen=True)
class CodigoIBGE:
    """Value Object para codigo IBGE - alta coesao."""

    valor: str

    def __post_init__(self) -> None:
        # usa self.valor
        self._validate()

    def _validate(self) -> None:
        # usa self.valor
        if not self._is_valid():
            raise ValueError(f"Codigo IBGE invalido: {self.valor}")

    def _is_valid(self) -> bool:
        # usa self.valor
        return len(self.valor) == 7 and self.valor.isdigit()

    def is_roraima(self) -> bool:
        # usa self.valor
        return self.valor.startswith("14")

    def __eq__(self, other: object) -> bool:
        # usa self.valor
        if not isinstance(other, CodigoIBGE):
            return False
        return self.valor == other.valor

    def __str__(self) -> str:
        # usa self.valor
        return self.valor
```

---

## Checklist Clean Code

### Nomes
- [ ] Nomes revelam intencao
- [ ] Nomes sao pronunciaveis
- [ ] Nomes sao faceis de buscar
- [ ] Classes = substantivos
- [ ] Metodos = verbos

### Funcoes
- [ ] Funcoes sao pequenas (< 20 linhas)
- [ ] Fazem apenas uma coisa
- [ ] Um nivel de abstracao
- [ ] Poucos argumentos (< 3)
- [ ] Sem efeitos colaterais

### Comentarios
- [ ] Codigo se auto-documenta
- [ ] Comentarios explicam "por que", nao "o que"
- [ ] Sem comentarios desatualizados
- [ ] Docstrings apenas em APIs publicas

### Formatacao
- [ ] Agrupamento logico
- [ ] Linhas curtas (< 100 caracteres)
- [ ] Indentacao consistente
- [ ] Espacamento vertical apropriado

### Erros
- [ ] Usa Result Pattern
- [ ] Exceptions tem contexto
- [ ] Erros sao logados
- [ ] Recovery quando possivel

### Classes
- [ ] Pequenas e coesas
- [ ] Responsabilidade unica
- [ ] Dependencias injetadas
- [ ] Baixo acoplamento
