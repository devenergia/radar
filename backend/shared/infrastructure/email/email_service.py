"""
Email Service Module

Serviço de envio de emails via Mailgun API.
Suporta múltiplos ambientes e templates HTML.
"""

from __future__ import annotations

import asyncio
import os
import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Any, Optional

import requests

from backend.shared.infrastructure.logger import get_logger

logger = get_logger(__name__)

# Pool de threads para operações assíncronas
_executor = ThreadPoolExecutor(max_workers=5)


def get_environment() -> str:
    """Detecta o ambiente atual baseado em variáveis de ambiente."""
    env = os.getenv("ENVIRONMENT", "development").lower()

    env_map = {
        "development": "DEV",
        "dev": "DEV",
        "homologation": "HM",
        "hm": "HM",
        "staging": "HM",
        "production": "PRD",
        "prd": "PRD",
        "prod": "PRD",
    }

    return env_map.get(env, "DEV")


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Busca variável de ambiente com suporte a prefixo de ambiente.

    Ordem de prioridade:
    1. {ENV}_{NAME} (ex: PRD_MAILGUN_API_KEY)
    2. {NAME} (ex: MAILGUN_API_KEY)
    3. default
    """
    env_prefix = get_environment()

    prefixed_value = os.getenv(f"{env_prefix}_{name}")
    if prefixed_value:
        return prefixed_value

    return os.getenv(name, default)


class EmailService:
    """
    Serviço de envio de emails via Mailgun.

    Implementa padrão Singleton para garantir uma única instância.
    Suporta templates HTML e envio assíncrono.

    Uso:
        service = EmailService()
        service.send_email(
            to_email="destinatario@email.com",
            subject="Assunto",
            html_body="<p>Conteúdo HTML</p>"
        )
    """

    _instance: Optional[EmailService] = None
    _initialized: bool = False

    def __new__(cls) -> EmailService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self.api_key = get_env_var("MAILGUN_API_KEY")
        self.domain = get_env_var("MAILGUN_DOMAIN")
        self.sender_email = get_env_var("MAILGUN_SENDER")
        self.sender_name = get_env_var("MAILGUN_SENDER_NAME", "RADAR")

        if self.domain:
            self.api_url = f"https://api.mailgun.net/v3/{self.domain}/messages"
        else:
            self.api_url = None

        # Diretório de templates
        self.templates_dir = Path(__file__).parent / "templates"

        self._initialized = True

        if self._is_configured():
            logger.info(
                "email_service_initialized",
                domain=self.domain,
                sender=self.sender_email,
            )
        else:
            logger.warning("email_service_not_configured")

    def _is_configured(self) -> bool:
        """Verifica se o serviço está configurado corretamente."""
        return all([self.api_key, self.domain, self.sender_email])

    def _html_to_text(self, html: str) -> str:
        """
        Converte HTML para texto puro de forma básica.

        Args:
            html: Conteúdo HTML

        Returns:
            Texto sem tags HTML
        """
        # Remove tags HTML
        text = re.sub(r"<[^>]+>", "", html)
        # Remove múltiplas quebras de linha
        text = re.sub(r"\n\s*\n", "\n\n", text)
        # Remove espaços extras
        text = re.sub(r" +", " ", text)
        return text.strip()

    def _render_template(self, template_name: str, **kwargs: Any) -> str:
        """
        Renderiza template HTML com variáveis.

        Args:
            template_name: Nome do arquivo de template
            **kwargs: Variáveis para substituição

        Returns:
            HTML renderizado
        """
        template_path = self.templates_dir / template_name

        if not template_path.exists():
            logger.warning("template_not_found", template=template_name)
            return ""

        content = template_path.read_text(encoding="utf-8")

        # Substitui variáveis no formato {{VARIAVEL}}
        for key, value in kwargs.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))

        return content

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """
        Envia email via Mailgun API.

        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_body: Corpo do email em HTML
            text_body: Corpo alternativo em texto puro (opcional)

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self._is_configured():
            logger.error(
                "email_not_configured",
                message="Serviço de email não configurado",
            )
            return False

        if not to_email or not subject or not html_body:
            logger.error(
                "email_invalid_params",
                to=to_email,
                has_subject=bool(subject),
                has_body=bool(html_body),
            )
            return False

        try:
            data: dict[str, str] = {
                "from": f"{self.sender_name} <{self.sender_email}>",
                "to": to_email,
                "subject": subject,
                "html": html_body,
            }

            # Adiciona versão texto se fornecida ou gera automaticamente
            if text_body:
                data["text"] = text_body
            else:
                data["text"] = self._html_to_text(html_body)

            response = requests.post(
                self.api_url,  # type: ignore
                auth=("api", self.api_key),  # type: ignore
                data=data,
                timeout=10,
            )

            if response.status_code == 200:
                logger.info(
                    "email_sent",
                    to=to_email,
                    subject=subject,
                )
                return True
            else:
                logger.error(
                    "email_failed",
                    to=to_email,
                    status=response.status_code,
                    response=response.text[:200],
                )
                return False

        except requests.Timeout:
            logger.error("email_timeout", to=to_email)
            return False

        except requests.RequestException as e:
            logger.error("email_request_error", to=to_email, error=str(e))
            return False

        except Exception as e:
            logger.error("email_error", to=to_email, error=str(e))
            return False

    async def send_email_async(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """
        Envia email de forma assíncrona.

        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_body: Corpo do email em HTML
            text_body: Corpo alternativo em texto puro

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _executor,
            partial(self.send_email, to_email, subject, html_body, text_body),
        )

    def send_indisponibilidade(
        self,
        to_email: str,
        sistema: str,
        data_inicio: str,
        previsao_retorno: str,
        motivo: str,
    ) -> bool:
        """
        Envia notificação de indisponibilidade do sistema.

        Args:
            to_email: Email do destinatário
            sistema: Nome do sistema indisponível
            data_inicio: Data/hora de início da indisponibilidade
            previsao_retorno: Previsão de retorno
            motivo: Motivo da indisponibilidade

        Returns:
            True se enviado com sucesso
        """
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #1a5f2a; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">RADAR - Roraima Energia</h1>
            </div>
            <div style="padding: 20px;">
                <h2 style="color: #c00;">Aviso de Indisponibilidade</h2>

                <p>Prezado(a),</p>

                <p>Informamos que o sistema <strong>{sistema}</strong> está
                temporariamente indisponível.</p>

                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9;">
                            <strong>Início:</strong>
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            {data_inicio}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9;">
                            <strong>Previsão de retorno:</strong>
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            {previsao_retorno}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background: #f9f9f9;">
                            <strong>Motivo:</strong>
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            {motivo}
                        </td>
                    </tr>
                </table>

                <p>Em caso de dúvidas, entre em contato conosco.</p>

                <p>Atenciosamente,<br>
                <strong>Equipe RADAR</strong></p>
            </div>
            <div style="background: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666;">
                <p style="margin: 0;">Este é um email automático do sistema RADAR.</p>
                <p style="margin: 5px 0 0;">Roraima Energia - Boa Vista, RR</p>
            </div>
        </div>
        """

        text = f"""
Aviso de Indisponibilidade

Prezado(a),

Informamos que o sistema {sistema} está temporariamente indisponível.

Início: {data_inicio}
Previsão de retorno: {previsao_retorno}
Motivo: {motivo}

Em caso de dúvidas, entre em contato conosco.

Atenciosamente,
Equipe RADAR

---
Este é um email automático do sistema RADAR.
Roraima Energia - Boa Vista, RR
        """

        return self.send_email(
            to_email=to_email,
            subject=f"[RADAR] Indisponibilidade - {sistema}",
            html_body=html,
            text_body=text.strip(),
        )

    def send_alerta_erro(
        self,
        to_email: str,
        endpoint: str,
        erro: str,
        traceback_info: str,
    ) -> bool:
        """
        Envia alerta de erro crítico.

        Args:
            to_email: Email do destinatário
            endpoint: Endpoint onde ocorreu o erro
            erro: Mensagem de erro
            traceback_info: Traceback completo

        Returns:
            True se enviado com sucesso
        """
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #c00; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">RADAR - Alerta de Erro</h1>
            </div>
            <div style="padding: 20px;">
                <h2 style="color: #c00;">Erro Crítico Detectado</h2>

                <p><strong>Endpoint:</strong> <code>{endpoint}</code></p>
                <p><strong>Erro:</strong> {erro}</p>

                <h3>Traceback:</h3>
                <pre style="background: #f5f5f5; padding: 15px; overflow-x: auto; font-size: 12px; border-radius: 4px;">{traceback_info}</pre>

                <p style="color: #666; font-size: 12px;">
                    Este alerta foi gerado automaticamente pelo sistema RADAR.
                </p>
            </div>
            <div style="background: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666;">
                <p style="margin: 0;">Roraima Energia - Boa Vista, RR</p>
            </div>
        </div>
        """

        return self.send_email(
            to_email=to_email,
            subject=f"[RADAR] Erro Crítico - {endpoint}",
            html_body=html,
        )


# Instância global
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Retorna instância singleton do serviço de email.

    Returns:
        EmailService instance
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
