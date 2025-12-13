# ADR-007: Padrão de Resposta ANEEL

## Status

Aceito

## Data

2025-12-12

## Contexto

O Ofício Circular 14/2025-SFE/ANEEL define um formato específico de resposta JSON que todas as distribuidoras devem seguir. A conformidade com este padrão é obrigatória e será verificada pela ANEEL.

## Decisão

Implementaremos **exatamente** o padrão de resposta definido pela ANEEL, sem modificações ou extensões.

### Estrutura Base de Resposta

Todas as APIs seguem a mesma estrutura base:

```typescript
interface BaseResponse {
  idcStatusRequisicao: 1 | 2;           // 1 = Sucesso, 2 = Erro
  emailIndisponibilidade: string;        // Email para contato
  mensagem: string;                      // Vazio se sucesso, erro se falha
}
```

### API 1 - Interrupções Ativas

```typescript
interface InterrupcaoFornecimentoItem {
  ideConjuntoUnidadeConsumidora: number; // Código do conjunto
  ideMunicipio: number;                   // IBGE 7 dígitos
  qtdUCsAtendidas: number;                // Total UCs no conjunto
  qtdOcorrenciaProgramada: number;        // UCs com interrupção programada
  qtdOcorrenciaNaoProgramada: number;     // UCs com interrupção não programada
}

interface InterrupcoesAtivasResponse extends BaseResponse {
  interrupcaoFornecimento: InterrupcaoFornecimentoItem[];
}
```

### API 2 - Dados da Demanda

```typescript
interface DadosDemandaItem {
  // Campos conforme especificação
}

interface DadosDemandaResponse extends BaseResponse {
  dadosDemanda: DadosDemandaItem[];
}
```

### Mapper de Resposta

```typescript
// src/application/mappers/response.mapper.ts

import { InterrupcaoAgregada } from '@domain/entities';

export class ResponseMapper {
  static toInterrupcoesAtivasResponse(
    interrupcoes: InterrupcaoAgregada[],
    email: string
  ): InterrupcoesAtivasResponse {
    return {
      idcStatusRequisicao: 1,
      emailIndisponibilidade: email,
      mensagem: '',
      interrupcaoFornecimento: interrupcoes.map(i => ({
        ideConjuntoUnidadeConsumidora: i.idConjunto,
        ideMunicipio: i.municipioIbge,
        qtdUCsAtendidas: i.qtdUcsAtendidas,
        qtdOcorrenciaProgramada: i.qtdUcsProgramada,
        qtdOcorrenciaNaoProgramada: i.qtdUcsNaoProgramada,
      })),
    };
  }

  static toErrorResponse(
    error: Error,
    email: string
  ): BaseResponse {
    return {
      idcStatusRequisicao: 2,
      emailIndisponibilidade: email,
      mensagem: error.message,
    };
  }
}
```

### Validação de Schema

```typescript
// JSON Schema para validação de resposta
export const interrupcoesResponseSchema = {
  type: 'object',
  required: ['idcStatusRequisicao', 'emailIndisponibilidade', 'mensagem', 'interrupcaoFornecimento'],
  properties: {
    idcStatusRequisicao: {
      type: 'integer',
      enum: [1, 2],
    },
    emailIndisponibilidade: {
      type: 'string',
      maxLength: 50,
      format: 'email',
    },
    mensagem: {
      type: 'string',
    },
    interrupcaoFornecimento: {
      type: 'array',
      items: {
        type: 'object',
        required: [
          'ideConjuntoUnidadeConsumidora',
          'ideMunicipio',
          'qtdUCsAtendidas',
          'qtdOcorrenciaProgramada',
          'qtdOcorrenciaNaoProgramada',
        ],
        properties: {
          ideConjuntoUnidadeConsumidora: { type: 'integer', minimum: 1 },
          ideMunicipio: { type: 'integer', minimum: 1000000, maximum: 9999999 },
          qtdUCsAtendidas: { type: 'integer', minimum: 0 },
          qtdOcorrenciaProgramada: { type: 'integer', minimum: 0 },
          qtdOcorrenciaNaoProgramada: { type: 'integer', minimum: 0 },
        },
      },
    },
  },
};
```

### Convenções de Nomenclatura

| Convenção ANEEL | Implementação |
|-----------------|---------------|
| camelCase | Todos os campos em camelCase |
| Prefixo `ide` | Identificadores (ideConjunto, ideMunicipio) |
| Prefixo `idc` | Indicadores (idcStatusRequisicao) |
| Prefixo `qtd` | Quantidades (qtdUCsAtendidas) |
| Prefixo `dth` | Data/Hora (dthRecuperacao) |

## Consequências

### Positivas

- **Conformidade**: Atende exatamente à especificação da ANEEL
- **Interoperabilidade**: Todas as distribuidoras usam mesmo formato
- **Validação**: Schema permite validação automática
- **Consistência**: Mesma estrutura para sucesso e erro

### Negativas

- **Rigidez**: Não podemos adicionar campos extras úteis
- **Limitações**: Alguns campos têm tipos/tamanhos específicos (ex: email 50 chars)
- **Evolução**: Mudanças dependem de nova versão do ofício ANEEL

### Neutras

- Necessidade de mapear entidades de domínio para o formato ANEEL
- Testes devem validar conformidade com schema

## Regras Importantes

1. **NUNCA** adicionar campos além dos especificados
2. **SEMPRE** retornar `interrupcaoFornecimento: []` mesmo quando vazio
3. **SEMPRE** usar HTTP 200 OK, status de erro vai no `idcStatusRequisicao`
4. **NUNCA** incluir stack traces ou detalhes técnicos na `mensagem`

## Referências

- Ofício Circular 14/2025-SFE/ANEEL V4 (23/10/2025)
- Especificação JSON das APIs no ofício
