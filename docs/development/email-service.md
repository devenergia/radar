# Email Service - Guia de Implementação

Este documento descreve a implementação do serviço de envio de emails no projeto RADAR.

## Visão Geral

O serviço de email é utilizado para:
- Notificações de indisponibilidade do sistema
- Alertas de erros críticos
- Comunicações com stakeholders (ANEEL)
- Relatórios automatizados

## Provedor: Mailgun

O RADAR utiliza **Mailgun** como provedor de email transacional devido a:
- Alta deliverability
- API REST simples
- Suporte a templates
- Logs e métricas detalhados
- Custo-benefício

## Configuração

### Variáveis de Ambiente

```env
# Configuração Multi-Ambiente
# O sistema detecta automaticamente o ambiente e usa o prefixo correto

# Desenvolvimento
DEV_MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEV_MAILGUN_DOMAIN=sandbox.mailgun.org
DEV_MAILGUN_SENDER=noreply@sandbox.mailgun.org

# Homologação
HM_MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HM_MAILGUN_DOMAIN=hm.roraimaenergia.com.br
HM_MAILGUN_SENDER=radar-hm@roraimaenergia.com.br

# Produção
PRD_MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PRD_MAILGUN_DOMAIN=roraimaenergia.com.br
PRD_MAILGUN_SENDER=radar@roraimaenergia.com.br

# Fallback
MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_DOMAIN=roraimaenergia.com.br
MAILGUN_SENDER=radar@roraimaenergia.com.br
```

### Estrutura de Configuração

| Variável | Descrição |
|----------|-----------|
| `MAILGUN_API_KEY` | Chave de API do Mailgun |
| `MAILGUN_DOMAIN` | Domínio configurado no Mailgun |
| `MAILGUN_SENDER` | Email do remetente |

## Implementação

### Classe EmailService

```python
from typing import Optional
import requests

class EmailService:
    """Serviço de envio de emails via Mailgun."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self.api_key = get_env_var('MAILGUN_API_KEY')
        self.domain = get_env_var('MAILGUN_DOMAIN')
        self.sender_email = get_env_var('MAILGUN_SENDER')
        self.api_url = f"https://api.mailgun.net/v3/{self.domain}/messages"

        self._initialized = True

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Envia email via Mailgun API.

        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_body: Corpo do email em HTML
            text_body: Corpo alternativo em texto puro

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not all([self.api_key, self.domain, self.sender_email]):
            logger.error("email_config_incomplete")
            return False

        try:
            data = {
                "from": f"RADAR <{self.sender_email}>",
                "to": to_email,
                "subject": subject,
                "html": html_body,
            }

            if text_body:
                data["text"] = text_body

            response = requests.post(
                self.api_url,
                auth=("api", self.api_key),
                data=data,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("email_sent", to=to_email, subject=subject)
                return True
            else:
                logger.error(
                    "email_failed",
                    status=response.status_code,
                    response=response.text
                )
                return False

        except Exception as e:
            logger.error("email_error", error=str(e))
            return False
```

## Templates de Email

### Estrutura Recomendada

```
backend/
└── shared/
    └── infrastructure/
        └── email/
            ├── email_service.py
            └── templates/
                ├── base.html
                ├── indisponibilidade.html
                ├── alerta_erro.html
                └── relatorio.html
```

### Template Base

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
        }
        .header {
            background: #1a5f2a;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .content {
            padding: 20px;
        }
        .footer {
            background: #f5f5f5;
            padding: 10px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>RADAR - Roraima Energia</h1>
    </div>
    <div class="content">
        {{CONTENT}}
    </div>
    <div class="footer">
        <p>Este é um email automático do sistema RADAR.</p>
        <p>Roraima Energia - Boa Vista, RR</p>
    </div>
</body>
</html>
```

### Template de Indisponibilidade

```html
<h2>Aviso de Indisponibilidade</h2>

<p>Prezado(a),</p>

<p>Informamos que o sistema <strong>{{SISTEMA}}</strong> está
temporariamente indisponível.</p>

<table style="width: 100%; border-collapse: collapse;">
    <tr>
        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Início:</strong></td>
        <td style="padding: 8px; border: 1px solid #ddd;">{{DATA_INICIO}}</td>
    </tr>
    <tr>
        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Previsão de retorno:</strong></td>
        <td style="padding: 8px; border: 1px solid #ddd;">{{PREVISAO_RETORNO}}</td>
    </tr>
    <tr>
        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Motivo:</strong></td>
        <td style="padding: 8px; border: 1px solid #ddd;">{{MOTIVO}}</td>
    </tr>
</table>

<p>Em caso de dúvidas, entre em contato conosco.</p>

<p>Atenciosamente,<br>
Equipe RADAR</p>
```

## Métodos de Envio Específicos

### Notificação de Indisponibilidade

```python
def send_indisponibilidade(
    self,
    to_email: str,
    sistema: str,
    data_inicio: str,
    previsao_retorno: str,
    motivo: str
) -> bool:
    """Envia notificação de indisponibilidade do sistema."""

    html = self._render_template(
        'indisponibilidade.html',
        SISTEMA=sistema,
        DATA_INICIO=data_inicio,
        PREVISAO_RETORNO=previsao_retorno,
        MOTIVO=motivo
    )

    text = f"""
    Aviso de Indisponibilidade

    O sistema {sistema} está temporariamente indisponível.

    Início: {data_inicio}
    Previsão de retorno: {previsao_retorno}
    Motivo: {motivo}

    Atenciosamente,
    Equipe RADAR
    """

    return self.send_email(
        to_email=to_email,
        subject=f"[RADAR] Indisponibilidade - {sistema}",
        html_body=html,
        text_body=text
    )
```

### Alerta de Erro

```python
def send_alerta_erro(
    self,
    to_email: str,
    endpoint: str,
    erro: str,
    traceback: str
) -> bool:
    """Envia alerta de erro crítico."""

    html = f"""
    <h2>Alerta de Erro Crítico</h2>

    <p><strong>Endpoint:</strong> {endpoint}</p>
    <p><strong>Erro:</strong> {erro}</p>

    <h3>Traceback:</h3>
    <pre style="background: #f5f5f5; padding: 10px; overflow-x: auto;">
{traceback}
    </pre>
    """

    return self.send_email(
        to_email=to_email,
        subject=f"[RADAR] Erro Crítico - {endpoint}",
        html_body=html
    )
```

## Boas Práticas

### 1. Sempre Forneça Versão Texto

```python
# Alguns clientes de email não renderizam HTML
def send_email(self, to, subject, html_body, text_body=None):
    if text_body is None:
        # Gera versão texto automaticamente
        text_body = self._html_to_text(html_body)
```

### 2. Use Timeout

```python
response = requests.post(
    self.api_url,
    auth=("api", self.api_key),
    data=data,
    timeout=10  # 10 segundos
)
```

### 3. Trate Erros Graciosamente

```python
try:
    return self._send_email(...)
except requests.Timeout:
    logger.error("email_timeout", to=to_email)
    return False
except requests.RequestException as e:
    logger.error("email_request_error", error=str(e))
    return False
```

### 4. Singleton Pattern

```python
# Garante uma única instância do serviço
email_service = EmailService()  # Sempre retorna mesma instância
```

### 5. Logging Adequado

```python
# Log sucesso
logger.info("email_sent", to=to_email, subject=subject)

# Log falha (sem dados sensíveis)
logger.error("email_failed", status=response.status_code)
```

## Envio Assíncrono

Para não bloquear a API durante o envio:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def send_email_async(
    self,
    to_email: str,
    subject: str,
    html_body: str
) -> bool:
    """Envia email de forma assíncrona."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: self.send_email(to_email, subject, html_body)
    )
```

## Fila de Emails (Opcional)

Para alto volume, considere usar uma fila:

```python
from queue import Queue
from threading import Thread

class EmailQueue:
    def __init__(self):
        self.queue = Queue()
        self.worker = Thread(target=self._process_queue, daemon=True)
        self.worker.start()

    def enqueue(self, to_email, subject, html_body):
        self.queue.put((to_email, subject, html_body))

    def _process_queue(self):
        email_service = EmailService()
        while True:
            to_email, subject, html_body = self.queue.get()
            email_service.send_email(to_email, subject, html_body)
            self.queue.task_done()
```

## Testes

### Mock para Testes

```python
from unittest.mock import patch, MagicMock

def test_send_email():
    with patch('requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200)

        service = EmailService()
        result = service.send_email(
            to_email="test@example.com",
            subject="Test",
            html_body="<p>Test</p>"
        )

        assert result is True
        mock_post.assert_called_once()
```

## Segurança

1. **Nunca** logue a API key
2. Valide emails antes de enviar
3. Limite taxa de envio para evitar bloqueio
4. Use TLS (HTTPS) para todas as chamadas
5. Armazene API key em variável de ambiente

## Referências

- [Mailgun API Documentation](https://documentation.mailgun.com/)
- [Email Best Practices](https://documentation.mailgun.com/en/latest/best_practices.html)
