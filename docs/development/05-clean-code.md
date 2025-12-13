# Clean Code - Projeto RADAR

## Visao Geral

Clean Code sao praticas que tornam o codigo legivel, mantenivel e expressivo. O codigo deve comunicar sua intencao claramente.

> "Qualquer tolo pode escrever codigo que um computador entenda. Bons programadores escrevem codigo que humanos entendem." - Martin Fowler

---

## Nomes Significativos

### Nomes Reveladores de Intencao

```typescript
// RUIM - O que significa 'd' e 't'?
const d = new Date();
const t = 5;

// BOM - Intencao clara
const dataInicioInterrupcao = new Date();
const ttlCacheEmMinutos = 5;
```

```typescript
// RUIM - Abreviacoes confusas
function getIntAgg(ibge: number): IntAgg[] { }

// BOM - Nome completo e descritivo
function getInterrupcoesAgregadasPorMunicipio(
  codigoIbge: CodigoIBGE
): InterrupcaoAgregada[] { }
```

### Nomes Pronunciaveis e Pesquisaveis

```typescript
// RUIM - Impronunciavel e dificil de buscar
const ymdhms = new Date();
const uc = 150;

// BOM - Pronunciavel e facil de encontrar
const dataHoraFormatoBrasilia = new Date();
const unidadesConsumidorasAfetadas = 150;
```

### Nomes de Classes e Metodos

```typescript
// Classes: Substantivos no singular
class Interrupcao { }
class CodigoIBGE { }
class InterrupcaoRepository { }

// Metodos: Verbos que descrevem acao
class InterrupcaoRepository {
  findAtivas(): Promise<Interrupcao[]> { }
  findByMunicipio(ibge: CodigoIBGE): Promise<Interrupcao[]> { }
}

// Use Cases: Verbo + Substantivo
class GetInterrupcoesAtivasUseCase { }
class ValidarCodigoIbgeUseCase { }
```

---

## Funcoes

### Funcoes Pequenas

```typescript
// RUIM - Funcao faz muitas coisas
async function processarRequisicao(request: Request): Promise<Response> {
  // Validar autenticacao
  const apiKey = request.headers['x-api-key'];
  if (!apiKey) throw new UnauthorizedError();
  if (apiKey !== process.env.API_KEY) throw new UnauthorizedError();

  // Buscar dados
  const connection = await oracledb.getConnection();
  const result = await connection.execute('SELECT ...');
  await connection.close();

  // Processar dados
  const interrupcoes = result.rows.map(row => ({
    id: row[0],
    tipo: row[1] ? 'PROGRAMADA' : 'NAO_PROGRAMADA',
    ucs: row[2]
  }));

  // Agregar
  const agregadas = new Map();
  for (const i of interrupcoes) {
    // logica de agregacao...
  }

  // Formatar resposta
  return {
    idcStatusRequisicao: 1,
    listaInterrupcoes: Array.from(agregadas.values())
  };
}

// BOM - Cada funcao faz uma coisa
async function processarRequisicao(request: Request): Promise<Response> {
  await this.authMiddleware.validar(request);
  const interrupcoes = await this.repository.findAtivas();
  const agregadas = this.aggregator.agregar(interrupcoes);
  return this.formatter.formatarResposta(agregadas);
}
```

### Um Nivel de Abstracao por Funcao

```typescript
// BOM - Mesmo nivel de abstracao
class GetInterrupcoesAtivasUseCase {
  async execute(): Promise<Result<InterrupcaoAgregada[]>> {
    const cacheado = await this.tentarBuscarDoCache();
    if (cacheado) return cacheado;

    const dados = await this.buscarDoBanco();
    const agregados = this.agregar(dados);
    await this.salvarNoCache(agregados);

    return Result.ok(agregados);
  }

  private async tentarBuscarDoCache(): Promise<InterrupcaoAgregada[] | null> {
    return this.cache.get('interrupcoes:ativas');
  }

  private async buscarDoBanco(): Promise<Interrupcao[]> {
    return this.repository.findAtivas();
  }

  private agregar(interrupcoes: Interrupcao[]): InterrupcaoAgregada[] {
    return this.aggregatorService.agregar(interrupcoes);
  }

  private async salvarNoCache(dados: InterrupcaoAgregada[]): Promise<void> {
    await this.cache.set('interrupcoes:ativas', dados, this.ttlEmSegundos);
  }
}
```

### Poucos Argumentos

```typescript
// RUIM - Muitos argumentos
function criarInterrupcao(
  id: number,
  tipo: string,
  municipio: number,
  conjunto: number,
  ucs: number,
  dataInicio: Date,
  dataFim: Date | null,
  ativa: boolean
): Interrupcao { }

// BOM - Objeto de parametros
interface CriarInterrupcaoParams {
  id: number;
  tipo: TipoInterrupcao;
  municipio: CodigoIBGE;
  conjunto: number;
  ucsAfetadas: number;
  dataInicio: Date;
  dataFim?: Date;
}

function criarInterrupcao(params: CriarInterrupcaoParams): Interrupcao { }

// Uso
const interrupcao = criarInterrupcao({
  id: 12345,
  tipo: TipoInterrupcao.PROGRAMADA,
  municipio: CodigoIBGE.create(1400100).getValue(),
  conjunto: 1,
  ucsAfetadas: 150,
  dataInicio: new Date()
});
```

---

## Comentarios

### Comentarios que Evitar

```typescript
// RUIM - Comentario obvio
// Incrementa contador
contador++;

// RUIM - Comentario desatualizado
// Retorna lista de interrupcoes ativas
// TODO: adicionar filtro por data
function findAtivas(): Interrupcao[] { }

// RUIM - Comentario ao inves de codigo claro
// Verifica se a interrupcao e programada checando
// se o PLAN_ID e diferente de null
if (planId !== null) { }
```

### Comentarios Aceitaveis

```typescript
// BOM - Explica regra de negocio complexa
/**
 * Uma interrupcao e classificada como PROGRAMADA quando existe
 * um registro associado na tabela SWITCH_PLAN_TASKS.
 * Fonte: Oficio Circular 14/2025-SFE/ANEEL
 */
static fromPlanId(planId: number | null): TipoInterrupcao {
  return planId !== null
    ? TipoInterrupcao.PROGRAMADA
    : TipoInterrupcao.NAO_PROGRAMADA;
}

// BOM - Documenta API publica
/**
 * Busca todas as interrupcoes ativas no momento.
 * @returns Lista de interrupcoes com is_open = 'T'
 */
async findAtivas(): Promise<Interrupcao[]> { }

// BOM - Aviso importante
// WARNING: DBLink pode ter latencia alta em horarios de pico
const result = await this.pool.execute(query);
```

---

## Formatacao

### Formatacao Vertical

```typescript
// BOM - Agrupamento logico com espacamento
export class GetInterrupcoesAtivasUseCase {
  // Dependencias
  private readonly repository: InterrupcaoRepository;
  private readonly cache: CacheRepository;
  private readonly aggregator: InterrupcaoAggregatorService;

  // Configuracao
  private readonly ttlCacheSegundos = 300;
  private readonly cacheKey = 'interrupcoes:ativas';

  constructor(
    repository: InterrupcaoRepository,
    cache: CacheRepository,
    aggregator: InterrupcaoAggregatorService
  ) {
    this.repository = repository;
    this.cache = cache;
    this.aggregator = aggregator;
  }

  // Metodo principal
  async execute(): Promise<Result<InterrupcaoAgregada[]>> {
    const cached = await this.cache.get<InterrupcaoAgregada[]>(this.cacheKey);
    if (cached) {
      return Result.ok(cached);
    }

    const interrupcoes = await this.repository.findAtivas();
    const agregadas = this.aggregator.agregar(interrupcoes);

    await this.cache.set(this.cacheKey, agregadas, this.ttlCacheSegundos);

    return Result.ok(agregadas);
  }
}
```

### Formatacao Horizontal

```typescript
// BOM - Linhas nao muito longas (max ~100 caracteres)
const interrupcaoAgregada = InterrupcaoAgregada.create({
  idConjunto: conjunto,
  municipio: CodigoIBGE.create(codigoIbge).getValue(),
  qtdUcsAtendidas: totalUcs,
  qtdProgramada: somaProgramada,
  qtdNaoProgramada: somaNaoProgramada
});

// BOM - Query SQL formatada
const query = `
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
`;
```

---

## Tratamento de Erros

### Use Exceptions, Nao Codigos de Retorno

```typescript
// RUIM - Codigo de retorno
function findAtivas(): { success: boolean; data?: Interrupcao[]; error?: string } {
  try {
    const data = // buscar...
    return { success: true, data };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// BOM - Result Pattern
function findAtivas(): Promise<Result<Interrupcao[]>> {
  // ...
}

// Uso
const result = await repository.findAtivas();
if (result.isFailure) {
  logger.error('Falha ao buscar interrupcoes', { error: result.getError() });
  return this.handleError(result.getError());
}
const interrupcoes = result.getValue();
```

### Exceptions com Contexto

```typescript
// domain/errors/domain.errors.ts
export class DomainError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly context?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'DomainError';
  }
}

export class CodigoIbgeInvalidoError extends DomainError {
  constructor(codigo: number) {
    super(
      `Codigo IBGE invalido: ${codigo}`,
      'IBGE_INVALIDO',
      { codigo, esperado: 'Codigo de 7 digitos de Roraima (14xxxxx)' }
    );
  }
}

export class DatabaseConnectionError extends DomainError {
  constructor(originalError: Error) {
    super(
      'Falha na conexao com banco de dados',
      'DB_CONNECTION_ERROR',
      { originalMessage: originalError.message }
    );
  }
}
```

---

## Classes

### Principio da Responsabilidade Unica

```typescript
// Uma classe, uma responsabilidade
class InterrupcaoMapper {
  // Responsabilidade: Converter entre camadas
  toEntity(row: OracleRow): Interrupcao { }
  toDTO(entity: Interrupcao): InterrupcaoDTO { }
  toAneelResponse(dto: InterrupcaoDTO): AneelInterrupcaoItem { }
}

class InterrupcaoValidator {
  // Responsabilidade: Validar dados
  validateCodigoIbge(codigo: number): Result<void> { }
  validateUcsAfetadas(ucs: number): Result<void> { }
}

class InterrupcaoAggregatorService {
  // Responsabilidade: Agregar interrupcoes
  agregar(interrupcoes: Interrupcao[]): InterrupcaoAgregada[] { }
}
```

### Coesao Alta

```typescript
// BOM - Todos os metodos usam os mesmos dados
class CodigoIBGE {
  private readonly _valor: number;

  static create(codigo: number): Result<CodigoIBGE> {
    // usa _valor implicitamente
  }

  get valor(): number {
    return this._valor;
  }

  isRoraima(): boolean {
    return this._valor >= 1400000 && this._valor <= 1499999;
  }

  equals(other: CodigoIBGE): boolean {
    return this._valor === other._valor;
  }

  toString(): string {
    return this._valor.toString();
  }
}
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
- [ ] JSDoc apenas em APIs publicas

### Formatacao
- [ ] Agrupamento logico
- [ ] Linhas curtas (< 100 caracteres)
- [ ] Indentacao consistente
- [ ] Espacamento vertical apropriado

### Erros
- [ ] Usa exceptions, nao codigos
- [ ] Exceptions tem contexto
- [ ] Erros sao logados
- [ ] Recovery quando possivel

### Classes
- [ ] Pequenas e coesas
- [ ] Responsabilidade unica
- [ ] Dependencias injetadas
- [ ] Baixo acoplamento
