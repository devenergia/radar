# ADR-010: Tratamento de Erros

## Status

Aceito

## Data

2025-12-12

## Contexto

A API RADAR precisa de uma estratégia consistente de tratamento de erros que:

1. Retorne o formato de erro especificado pela ANEEL
2. Não exponha detalhes técnicos sensíveis
3. Facilite debugging e logging
4. Seja consistente em toda a aplicação

## Decisão

### Hierarquia de Erros de Domínio

```typescript
// src/shared/errors/domain.errors.ts

export abstract class DomainError extends Error {
  abstract readonly code: string;
  abstract readonly statusCode: number;
  abstract readonly isOperational: boolean;

  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

// Erros de Negócio (esperados, operacionais)
export class ValidationError extends DomainError {
  readonly code = 'VALIDATION_ERROR';
  readonly statusCode = 400;
  readonly isOperational = true;
}

export class NotFoundError extends DomainError {
  readonly code = 'NOT_FOUND';
  readonly statusCode = 404;
  readonly isOperational = true;
}

export class UnauthorizedError extends DomainError {
  readonly code = 'UNAUTHORIZED';
  readonly statusCode = 401;
  readonly isOperational = true;
}

export class ForbiddenError extends DomainError {
  readonly code = 'FORBIDDEN';
  readonly statusCode = 403;
  readonly isOperational = true;
}

// Erros de Infraestrutura
export class DatabaseError extends DomainError {
  readonly code = 'DATABASE_ERROR';
  readonly statusCode = 500;
  readonly isOperational = true;

  constructor(message: string, public readonly originalError?: Error) {
    super(message);
  }
}

export class ExternalServiceError extends DomainError {
  readonly code = 'EXTERNAL_SERVICE_ERROR';
  readonly statusCode = 502;
  readonly isOperational = true;
}
```

### Error Handler Global

```typescript
// src/interfaces/http/middlewares/error-handler.middleware.ts

import { FastifyError, FastifyReply, FastifyRequest } from 'fastify';
import { DomainError } from '@shared/errors';

export function errorHandler(
  error: FastifyError | DomainError | Error,
  request: FastifyRequest,
  reply: FastifyReply,
) {
  const requestId = request.id;
  const email = process.env.EMAIL_INDISPONIBILIDADE || 'radar@roraimaenergia.com.br';

  // Log do erro (com stack trace para debugging)
  request.log.error({
    err: error,
    requestId,
    url: request.url,
    method: request.method,
  });

  // Determinar resposta baseada no tipo de erro
  if (error instanceof DomainError) {
    return reply.status(200).send({
      idcStatusRequisicao: 2,
      emailIndisponibilidade: email,
      mensagem: error.message,
      interrupcaoFornecimento: [],
    });
  }

  // Erro de validação do Fastify
  if (error.validation) {
    return reply.status(200).send({
      idcStatusRequisicao: 2,
      emailIndisponibilidade: email,
      mensagem: `Erro de validação: ${error.message}`,
      interrupcaoFornecimento: [],
    });
  }

  // Erro não esperado (não expor detalhes)
  return reply.status(200).send({
    idcStatusRequisicao: 2,
    emailIndisponibilidade: email,
    mensagem: 'Erro interno do servidor. Tente novamente mais tarde.',
    interrupcaoFornecimento: [],
  });
}
```

### Padrão de Resposta de Erro (ANEEL)

**Importante**: A ANEEL espera HTTP 200 OK mesmo em erros, com o status no campo `idcStatusRequisicao`.

```json
{
  "idcStatusRequisicao": 2,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "Erro de conexão com banco de dados",
  "interrupcaoFornecimento": []
}
```

### Exceções ao Padrão (HTTP Status Codes)

Apenas para erros de autenticação/autorização usamos HTTP status diferente de 200:

| Cenário | HTTP Status | idcStatusRequisicao |
|---------|-------------|---------------------|
| Sucesso | 200 | 1 |
| Erro de negócio | 200 | 2 |
| Erro de banco | 200 | 2 |
| API Key ausente | 401 | 2 |
| API Key inválida | 401 | 2 |
| IP não autorizado | 403 | 2 |

### Tratamento em Use Cases

```typescript
// src/application/use-cases/get-interrupcoes-ativas.use-case.ts

import { Result } from '@shared/utils/result';
import { DatabaseError } from '@shared/errors';

export class GetInterrupcoesAtivasUseCase {
  constructor(
    private readonly repository: InterrupcaoRepository,
  ) {}

  async execute(params: GetInterrupcoesParams): Promise<Result<InterrupcaoAgregada[]>> {
    try {
      const interrupcoes = await this.repository.findAtivas(params);
      return Result.ok(interrupcoes);
    } catch (error) {
      // Transformar erros de infra em erros de domínio
      if (error instanceof OracleError) {
        return Result.fail(new DatabaseError(
          'Erro ao consultar interrupções ativas',
          error
        ));
      }
      throw error; // Re-throw erros inesperados
    }
  }
}
```

### Result Pattern (Opcional)

```typescript
// src/shared/utils/result.ts

export class Result<T> {
  private constructor(
    public readonly isSuccess: boolean,
    public readonly value?: T,
    public readonly error?: DomainError,
  ) {}

  static ok<U>(value: U): Result<U> {
    return new Result(true, value);
  }

  static fail<U>(error: DomainError): Result<U> {
    return new Result(false, undefined, error);
  }

  getOrThrow(): T {
    if (!this.isSuccess) {
      throw this.error;
    }
    return this.value!;
  }
}
```

## Consequências

### Positivas

- **Consistência**: Todos os erros seguem mesmo formato
- **Segurança**: Detalhes técnicos não vazam para clientes
- **Debugging**: Stack traces completos nos logs
- **Conformidade ANEEL**: Formato de erro esperado

### Negativas

- **Verbosidade**: Mais código para tratar erros
- **Confusão HTTP**: 200 OK mesmo em erros pode confundir

### Neutras

- Necessidade de mapear erros de bibliotecas externas
- Testes devem cobrir cenários de erro

## Referências

- ANEEL Ofício Circular 14/2025 - Seção de Erros
- [Error Handling in Node.js](https://www.joyent.com/node-js/production/design/errors)
