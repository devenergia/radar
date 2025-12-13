# ADR-006: Autenticação via API Key

## Status

Aceito

## Data

2025-12-12

## Contexto

A ANEEL especificou no Ofício Circular 14/2025 que a autenticação deve ser feita via **header `x-api-key`**. Além disso:

1. A API será consumida apenas pela ANEEL (sistema automatizado)
2. Não há necessidade de gerenciamento de usuários/sessões
3. Simplicidade é preferida sobre complexidade
4. Deve haver controle de acesso por IP (whitelist)

## Decisão

Implementaremos autenticação via **API Key** no header `x-api-key`, conforme especificado pela ANEEL.

### Fluxo de Autenticação

```
┌───────────────┐                              ┌─────────────────┐
│    ANEEL      │                              │   RADAR API     │
└───────┬───────┘                              └────────┬────────┘
        │                                               │
        │  GET /quantitativointerrupcoesativas          │
        │  Header: x-api-key: <chave>                   │
        │───────────────────────────────────────────────>
        │                                               │
        │                                    ┌──────────┴──────────┐
        │                                    │ 1. Verificar IP     │
        │                                    │ 2. Validar API Key  │
        │                                    │ 3. Processar        │
        │                                    └──────────┬──────────┘
        │                                               │
        │  200 OK / 401 Unauthorized                    │
        │<───────────────────────────────────────────────
        │                                               │
```

### Implementação do Middleware

```typescript
// src/interfaces/http/middlewares/auth.middleware.ts

import { FastifyRequest, FastifyReply } from 'fastify';
import { UnauthorizedError, ForbiddenError } from '@shared/errors';

export interface AuthMiddlewareConfig {
  apiKeys: string[];
  ipWhitelist: string[];
  ipWhitelistEnabled: boolean;
}

export function createAuthMiddleware(config: AuthMiddlewareConfig) {
  return async (request: FastifyRequest, reply: FastifyReply) => {
    // 1. Verificar IP (se habilitado)
    if (config.ipWhitelistEnabled) {
      const clientIp = getClientIp(request);
      if (!config.ipWhitelist.includes(clientIp)) {
        throw new ForbiddenError(`IP ${clientIp} não autorizado`);
      }
    }

    // 2. Validar API Key
    const apiKey = request.headers['x-api-key'];

    if (!apiKey) {
      throw new UnauthorizedError('Header x-api-key é obrigatório');
    }

    if (!config.apiKeys.includes(apiKey as string)) {
      throw new UnauthorizedError('API Key inválida');
    }

    // 3. Adicionar metadata ao request
    request.auth = {
      apiKey: maskApiKey(apiKey as string),
      clientIp: getClientIp(request),
      authenticatedAt: new Date(),
    };
  };
}

function getClientIp(request: FastifyRequest): string {
  return (
    (request.headers['x-forwarded-for'] as string)?.split(',')[0]?.trim() ||
    request.headers['x-real-ip'] as string ||
    request.ip
  );
}

function maskApiKey(apiKey: string): string {
  if (apiKey.length <= 8) return '****';
  return `${apiKey.slice(0, 4)}...${apiKey.slice(-4)}`;
}
```

### Configuração de API Keys

```typescript
// Variáveis de ambiente
API_KEY_ANEEL=chave-secreta-aneel-producao
API_KEYS_INTERNAL=chave-interna-1,chave-interna-2
IP_WHITELIST_ANEEL=200.193.x.x,200.193.y.y
IP_WHITELIST_ENABLED=true
```

### Respostas de Erro

```json
// 401 Unauthorized - API Key ausente
{
  "idcStatusRequisicao": 2,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "Header x-api-key é obrigatório",
  "interrupcaoFornecimento": []
}

// 401 Unauthorized - API Key inválida
{
  "idcStatusRequisicao": 2,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "API Key inválida",
  "interrupcaoFornecimento": []
}

// 403 Forbidden - IP não autorizado
{
  "idcStatusRequisicao": 2,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "IP não autorizado",
  "interrupcaoFornecimento": []
}
```

## Consequências

### Positivas

- **Conformidade ANEEL**: Segue exatamente a especificação do ofício
- **Simplicidade**: Fácil de implementar e manter
- **Stateless**: Não requer sessões ou tokens de refresh
- **Performance**: Validação rápida (lookup em array)
- **Auditoria**: Fácil de logar qual API Key foi usada

### Negativas

- **Segurança Limitada**: API Keys podem ser comprometidas se vazadas
- **Sem Expiração**: Chaves não expiram automaticamente
- **Sem Rotação Automática**: Rotação de chaves é manual
- **Granularidade**: Todas as requisições têm mesmo nível de acesso

### Mitigações

1. **HTTPS Obrigatório**: API Keys trafegam apenas em canal seguro
2. **IP Whitelist**: Limita de onde as chaves podem ser usadas
3. **Rate Limiting**: Limita abuso mesmo com chave válida
4. **Logging**: Registra todas as requisições para auditoria
5. **Rotação Periódica**: Processo manual de rotação trimestral

## Alternativas Consideradas

### Alternativa 1: OAuth 2.0 / JWT

Tokens de acesso com expiração e refresh tokens.

**Rejeitado porque**: ANEEL especificou x-api-key, complexidade desnecessária para um consumidor único.

### Alternativa 2: Certificado mTLS

Autenticação mútua via certificados SSL.

**Rejeitado porque**: Não especificado pela ANEEL, complexidade de gerenciamento de certificados.

### Alternativa 3: Basic Auth

Username/password codificados em Base64.

**Rejeitado porque**: ANEEL especificou x-api-key, Basic Auth é menos seguro.

## Referências

- Ofício Circular 14/2025-SFE/ANEEL - Seção de Autenticação
- OWASP API Security Top 10
