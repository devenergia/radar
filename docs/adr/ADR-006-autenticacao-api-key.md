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

```python
# app/infrastructure/http/middlewares/auth_middleware.py

from typing import List
from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from app.shared.errors import UnauthorizedError, ForbiddenError
from app.core.config import settings

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_keys: List[str], ip_whitelist: List[str],
                 ip_whitelist_enabled: bool):
        super().__init__(app)
        self.api_keys = api_keys
        self.ip_whitelist = ip_whitelist
        self.ip_whitelist_enabled = ip_whitelist_enabled

    async def dispatch(self, request: Request, call_next):
        # 1. Verificar IP (se habilitado)
        if self.ip_whitelist_enabled:
            client_ip = self._get_client_ip(request)
            if client_ip not in self.ip_whitelist:
                raise ForbiddenError(f"IP {client_ip} não autorizado")

        # 2. Validar API Key
        api_key = request.headers.get("x-api-key")

        if not api_key:
            raise UnauthorizedError("Header x-api-key é obrigatório")

        if api_key not in self.api_keys:
            raise UnauthorizedError("API Key inválida")

        # 3. Adicionar metadata ao request
        request.state.auth = {
            "api_key": self._mask_api_key(api_key),
            "client_ip": self._get_client_ip(request),
            "authenticated_at": datetime.now()
        }

        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extrai o IP real do cliente considerando proxies"""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _mask_api_key(self, api_key: str) -> str:
        """Mascara a API key para logs"""
        if len(api_key) <= 8:
            return "****"
        return f"{api_key[:4]}...{api_key[-4:]}"


# Dependency para uso em rotas específicas
async def verify_api_key(api_key: str = api_key_header) -> str:
    """Verifica API key em rotas específicas"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header x-api-key é obrigatório"
        )

    if api_key not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida"
        )

    return api_key
```

### Configuração de API Keys

```python
# app/core/config.py

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Keys
    API_KEY_ANEEL: str
    API_KEYS_INTERNAL: str = ""

    # IP Whitelist
    IP_WHITELIST_ANEEL: str = ""
    IP_WHITELIST_ENABLED: bool = True

    @property
    def API_KEYS(self) -> List[str]:
        """Lista de todas as API keys válidas"""
        keys = [self.API_KEY_ANEEL]
        if self.API_KEYS_INTERNAL:
            keys.extend(self.API_KEYS_INTERNAL.split(","))
        return keys

    @property
    def IP_WHITELIST(self) -> List[str]:
        """Lista de IPs autorizados"""
        if not self.IP_WHITELIST_ANEEL:
            return []
        return [ip.strip() for ip in self.IP_WHITELIST_ANEEL.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### Variáveis de Ambiente

```bash
# .env
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
- **Performance**: Validação rápida (lookup em lista)
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
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
