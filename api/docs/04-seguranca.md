# Segurança da API RADAR

**Base Legal:** Ofício Circular nº 14/2025-SFE/ANEEL - Seção 6
**Versão:** 1.0
**Data:** Dezembro/2025

---

## 1. Visão Geral

A API RADAR implementa múltiplas camadas de segurança para garantir que apenas a ANEEL tenha acesso às informações fornecidas. Este documento descreve os mecanismos de segurança implementados e as boas práticas a serem seguidas.

---

## 2. Requisitos de Segurança

### 2.1 Padrões Obrigatórios

A API deve seguir os seguintes padrões do governo federal:

| Padrão | Descrição | Link |
|--------|-----------|------|
| **e-Ping** | Padrões de Interoperabilidade de Governo Eletrônico | [governoeletronico.gov.br](https://governoeletronico.gov.br) |
| **Guia de APIs** | Guia de Requisitos Mínimos de Privacidade e Segurança para APIs | [gov.br](https://www.gov.br/governodigital/pt-br/seguranca-e-protecao-de-dados/guias/guia_requisitos_minimos_apis.pdf) |

### 2.2 Requisitos Implementados

| Requisito | Status | Descrição |
|-----------|--------|-----------|
| HTTPS Obrigatório | Implementado | Toda comunicação via protocolo seguro |
| API Key | Implementado | Autenticação via chave no header |
| Whitelist de IP | Implementado | Acesso restrito ao bloco ANEEL |
| Criptografia | Implementado | TLS 1.2+ para transporte |

---

## 3. Protocolo HTTPS

### 3.1 Configuração

A API está disponível **exclusivamente** via protocolo HTTPS:

```
https://api.roraimaenergia.com.br/radar
```

**Requisitos:**
- TLS 1.2 ou superior
- Certificado SSL válido emitido por CA confiável
- HTTP (porta 80) deve redirecionar para HTTPS ou estar desabilitado

### 3.2 Certificado SSL

| Propriedade | Valor |
|-------------|-------|
| **Domínio** | api.roraimaenergia.com.br |
| **Tipo** | Wildcard ou SAN |
| **Validade** | Renovação automática recomendada |
| **CA** | Autoridade Certificadora reconhecida |

---

## 4. Autenticação via API Key

### 4.1 Conceito

A API Key é uma **chave única** fornecida pela Roraima Energia que:
- Identifica a requisição como originária da ANEEL
- Autoriza o acesso aos endpoints da API
- Permite rastreamento e auditoria de acessos

### 4.2 Configuração do Header

A API Key deve ser enviada no **header** de todas as requisições:

```http
x-api-key: {valor-da-chave}
```

**Exemplo de requisição:**

```http
GET /radar/quantitativointerrupcoesativas HTTP/1.1
Host: api.roraimaenergia.com.br
x-api-key: abc123def456ghi789jkl012mno345pqr678
```

### 4.3 Exemplo em Código

**Python:**
```python
import requests

url = "https://api.roraimaenergia.com.br/radar/quantitativointerrupcoesativas"
headers = {
    "x-api-key": "sua-api-key-aqui"
}

response = requests.get(url, headers=headers)
```

**cURL:**
```bash
curl -X GET "https://api.roraimaenergia.com.br/radar/quantitativointerrupcoesativas" \
     -H "x-api-key: sua-api-key-aqui"
```

**JavaScript:**
```javascript
fetch('https://api.roraimaenergia.com.br/radar/quantitativointerrupcoesativas', {
    method: 'GET',
    headers: {
        'x-api-key': 'sua-api-key-aqui'
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

### 4.4 Gerenciamento da API Key

| Ação | Responsável | Procedimento |
|------|-------------|--------------|
| **Geração** | Roraima Energia (TI) | Gerar chave única para ANEEL |
| **Distribuição** | Roraima Energia | Enviar de forma segura para ANEEL |
| **Armazenamento** | Ambas as partes | Manter em sigilo absoluto |
| **Renovação** | Roraima Energia | Sob demanda ou periodicamente |
| **Revogação** | Roraima Energia | Em caso de comprometimento |

### 4.5 Boas Práticas para API Key

**Para a Distribuidora:**
- Armazenar a chave em cofre de senhas (ex: Azure Key Vault, AWS Secrets Manager)
- Não versionar a chave em repositórios de código
- Implementar rotação periódica da chave
- Manter log de todas as requisições autenticadas

**Para a ANEEL:**
- Não compartilhar a chave entre sistemas
- Armazenar de forma segura
- Notificar imediatamente em caso de comprometimento

---

## 5. Whitelist de IP

### 5.1 Bloco Autorizado

A API aceita requisições **apenas** do bloco de IPs da ANEEL:

```
200.198.220.128/25
```

**Range de IPs:** 200.198.220.128 a 200.198.220.255 (128 endereços)

### 5.2 Implementação

A validação de IP deve ocorrer **antes** da validação da API Key:

```
Requisição → Verificar IP → Verificar API Key → Processar
```

### 5.3 Configuração de Firewall

**Exemplo de regra (iptables):**
```bash
# Permitir apenas bloco ANEEL na porta 443
iptables -A INPUT -p tcp --dport 443 -s 200.198.220.128/25 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j DROP
```

**Exemplo de regra (nginx):**
```nginx
location /radar {
    allow 200.198.220.128/25;
    deny all;

    proxy_pass http://api-backend;
}
```

**Exemplo de regra (Apache):**
```apache
<Location "/radar">
    Require ip 200.198.220.128/25
</Location>
```

### 5.4 Resposta para IP Não Autorizado

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
    "error": "Access denied",
    "message": "IP not authorized"
}
```

---

## 6. Códigos de Resposta HTTP

### 6.1 Tabela de Códigos

| Código | Descrição | Causa | Ação |
|--------|-----------|-------|------|
| 200 | OK | Requisição bem-sucedida | - |
| 400 | Bad Request | Parâmetros inválidos | Verificar formato da requisição |
| 401 | Unauthorized | API Key inválida ou ausente | Verificar header x-api-key |
| 403 | Forbidden | IP não autorizado | Verificar origem da requisição |
| 404 | Not Found | Rota não encontrada | Verificar URL do endpoint |
| 429 | Too Many Requests | Rate limit excedido | Aguardar e tentar novamente |
| 500 | Internal Server Error | Erro interno da API | Verificar campo `mensagem` |
| 502 | Bad Gateway | Erro no servidor upstream | Tentar novamente |
| 503 | Service Unavailable | Serviço indisponível | Aguardar e tentar novamente |

### 6.2 Exemplos de Respostas de Erro

**401 Unauthorized:**
```json
{
    "idcStatusRequisicao": 2,
    "mensagem": "API Key inválida ou ausente"
}
```

**403 Forbidden:**
```json
{
    "idcStatusRequisicao": 2,
    "mensagem": "IP de origem não autorizado"
}
```

---

## 7. Logging e Auditoria

### 7.1 Informações a Registrar

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| **Timestamp** | Data/hora da requisição | 2025-12-10T14:30:00-03:00 |
| **IP Origem** | Endereço IP do cliente | 200.198.220.150 |
| **Método** | Método HTTP | GET |
| **Endpoint** | Rota acessada | /quantitativointerrupcoesativas |
| **Parâmetros** | Query string | numProtocolo=123456 |
| **Status** | Código de resposta | 200 |
| **Tempo** | Tempo de resposta | 150ms |
| **API Key** | Hash da chave (não a chave completa) | abc123*** |

### 7.2 Exemplo de Log

```json
{
    "timestamp": "2025-12-10T14:30:00-03:00",
    "ip": "200.198.220.150",
    "method": "GET",
    "endpoint": "/radar/dadosdemanda",
    "params": {"numProtocolo": "123456789"},
    "status": 200,
    "response_time_ms": 150,
    "api_key_hash": "abc123***"
}
```

### 7.3 Retenção de Logs

| Tipo de Log | Retenção | Justificativa |
|-------------|----------|---------------|
| Logs de acesso | 12 meses | Auditoria e compliance |
| Logs de erro | 6 meses | Troubleshooting |
| Logs de segurança | 24 meses | Investigação de incidentes |

---

## 8. Proteção contra Ataques

### 8.1 Rate Limiting

Embora a ANEEL faça consultas a cada 30 minutos, é recomendado implementar rate limiting:

| Endpoint | Limite Sugerido |
|----------|-----------------|
| `/quantitativointerrupcoesativas` | 10 req/min |
| `/quantitativodemandasdiversas` | 10 req/min |
| `/dadosdemanda` | 60 req/min |

### 8.2 Proteção contra Injeção

- Validar todos os parâmetros de entrada
- Usar prepared statements para queries SQL
- Sanitizar dados antes de processar

### 8.3 Headers de Segurança

Incluir headers de segurança nas respostas:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'none'
```

---

## 9. Procedimentos de Segurança

### 9.1 Em Caso de Comprometimento da API Key

1. **Notificar** a ANEEL imediatamente
2. **Revogar** a chave comprometida
3. **Gerar** nova chave
4. **Enviar** nova chave de forma segura
5. **Analisar** logs para identificar acessos indevidos
6. **Documentar** o incidente

### 9.2 Em Caso de Tentativa de Acesso Não Autorizado

1. **Bloquear** o IP de origem (se não for da ANEEL)
2. **Alertar** a equipe de segurança
3. **Registrar** o incidente
4. **Notificar** a ANEEL se apropriado

### 9.3 Manutenção Programada

1. **Notificar** a ANEEL com antecedência mínima de 48h
2. **Agendar** para horários de menor impacto
3. **Comunicar** previsão de retorno
4. **Confirmar** retorno à operação normal

---

## 10. Contatos

### 10.1 Roraima Energia

| Função | Email |
|--------|-------|
| **Indisponibilidade API** | radar@roraimaenergia.com.br |
| **Suporte Técnico** | ti.radar@roraimaenergia.com.br |
| **Segurança da Informação** | seguranca@roraimaenergia.com.br |

### 10.2 Notificação de Indisponibilidade

O campo `emailIndisponibilidade` nas respostas da API indica o email que receberá notificações automáticas da ANEEL em caso de indisponibilidade:

```json
{
    "emailIndisponibilidade": "radar@roraimaenergia.com.br"
}
```

---

## 11. Checklist de Segurança

### 11.1 Infraestrutura

- [ ] HTTPS habilitado com TLS 1.2+
- [ ] Certificado SSL válido e não expirado
- [ ] HTTP redirecionando para HTTPS ou desabilitado
- [ ] Firewall configurado com whitelist de IP

### 11.2 Autenticação

- [ ] API Key gerada e enviada para ANEEL
- [ ] Validação de API Key implementada em todos os endpoints
- [ ] API Key armazenada de forma segura
- [ ] Mecanismo de rotação de chave disponível

### 11.3 Controle de Acesso

- [ ] Whitelist de IP `200.198.220.128/25` configurada
- [ ] Bloqueio de IPs não autorizados retornando 403
- [ ] Rate limiting implementado

### 11.4 Logging e Monitoramento

- [ ] Logs de acesso habilitados
- [ ] Logs de erro habilitados
- [ ] Alertas de segurança configurados
- [ ] Retenção de logs conforme política

### 11.5 Proteção

- [ ] Headers de segurança configurados
- [ ] Proteção contra SQL injection
- [ ] Validação de parâmetros de entrada
- [ ] CORS configurado (se aplicável)

---

## 12. Referências

- [e-Ping - Padrões de Interoperabilidade](https://governoeletronico.gov.br)
- [Guia de Requisitos Mínimos de APIs](https://www.gov.br/governodigital/pt-br/seguranca-e-protecao-de-dados/guias/guia_requisitos_minimos_apis.pdf)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [RFC 6749 - OAuth 2.0](https://tools.ietf.org/html/rfc6749)

---

*Documentação baseada no Ofício Circular 14/2025-SFE/ANEEL V4 (23/10/2025)*
