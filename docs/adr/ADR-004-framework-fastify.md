# ADR-004: Fastify como Framework HTTP

## Status

Aceito

## Data

2025-12-12

## Contexto

Precisamos de um framework HTTP para expor a API REST do RADAR. Requisitos:

1. Alta performance (tempo de resposta < 5 segundos exigido pela ANEEL)
2. Suporte nativo a TypeScript
3. Validação de schemas integrada
4. Plugin para OpenAPI/Swagger
5. Middlewares para autenticação, logging, rate limiting
6. Comunidade ativa e manutenção contínua

## Decisão

Utilizaremos **Fastify** como framework HTTP principal.

### Versão

- Fastify: ^4.x

### Plugins Principais

```typescript
// Plugins que serão utilizados
import fastify from 'fastify';
import fastifySwagger from '@fastify/swagger';
import fastifySwaggerUi from '@fastify/swagger-ui';
import fastifyRateLimit from '@fastify/rate-limit';
import fastifyHelmet from '@fastify/helmet';
import fastifyCors from '@fastify/cors';
import fastifyAuth from '@fastify/auth';

const app = fastify({
  logger: true,
  requestIdHeader: 'x-request-id',
  requestIdLogLabel: 'requestId',
});
```

### Estrutura de Plugins

```typescript
// Organização dos plugins
src/
├── interfaces/
│   └── http/
│       ├── plugins/
│       │   ├── swagger.plugin.ts
│       │   ├── auth.plugin.ts
│       │   ├── error-handler.plugin.ts
│       │   └── rate-limit.plugin.ts
│       ├── routes/
│       │   ├── interrupcoes.routes.ts
│       │   ├── demandas.routes.ts
│       │   └── health.routes.ts
│       └── server.ts
```

### Validação com JSON Schema

```typescript
// Exemplo de schema de validação
const queryInterrupcoesSchema = {
  querystring: {
    type: 'object',
    properties: {
      dthRecuperacao: {
        type: 'string',
        pattern: '^\\d{2}/\\d{2}/\\d{4} \\d{2}:\\d{2}$'
      }
    }
  },
  response: {
    200: {
      type: 'object',
      properties: {
        idcStatusRequisicao: { type: 'integer', enum: [1, 2] },
        emailIndisponibilidade: { type: 'string' },
        mensagem: { type: 'string' },
        interrupcaoFornecimento: {
          type: 'array',
          items: { /* ... */ }
        }
      }
    }
  }
};
```

## Consequências

### Positivas

- **Performance**: Um dos frameworks Node.js mais rápidos (benchmark superior ao Express)
- **JSON Schema**: Validação e serialização otimizadas
- **TypeScript**: Suporte nativo excelente com tipos bem definidos
- **Plugins**: Ecossistema rico de plugins oficiais
- **Logging**: Logger Pino integrado (alta performance)
- **OpenAPI**: Geração automática de documentação Swagger

### Negativas

- **Menor Adoção**: Menos popular que Express (menos exemplos online)
- **API Diferente**: Desenvolvedores acostumados com Express precisam se adaptar
- **Plugins Específicos**: Alguns plugins comuns do Express não têm equivalente direto

### Neutras

- Padrão de hooks diferente de middlewares tradicionais
- Serialização customizada requer entendimento do ciclo de vida

## Alternativas Consideradas

### Alternativa 1: Express.js

Framework mais popular do ecossistema Node.js.

**Rejeitado porque**: Performance inferior, tipagem TypeScript não é nativa, middleware-based pode ficar complexo.

### Alternativa 2: NestJS

Framework opinado com arquitetura Angular-like.

**Rejeitado porque**: Muito opinado, adiciona abstrações desnecessárias sobre o HTTP, overhead de decorators.

### Alternativa 3: Hono

Framework moderno e ultra-leve.

**Rejeitado porque**: Ecossistema ainda jovem, menos plugins maduros, menor comunidade.

### Alternativa 4: Koa

Sucessor espiritual do Express pelos mesmos autores.

**Rejeitado porque**: Performance inferior ao Fastify, menos plugins oficiais, desenvolvimento menos ativo.

## Referências

- [Fastify Documentation](https://fastify.dev/)
- [Fastify Benchmarks](https://fastify.dev/benchmarks/)
- [Fastify TypeScript](https://fastify.dev/docs/latest/Reference/TypeScript/)
