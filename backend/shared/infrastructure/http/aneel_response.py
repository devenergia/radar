"""Builder para respostas no formato padrao ANEEL."""

from __future__ import annotations

from enum import IntEnum
from typing import Any

from pydantic import BaseModel


class AneelStatusRequisicao(IntEnum):
    """Status de requisicao padrao ANEEL."""

    SUCESSO = 1
    ERRO = 2


class AneelBaseResponse(BaseModel):
    """Resposta base padrao ANEEL."""

    idcStatusRequisicao: AneelStatusRequisicao
    desStatusRequisicao: str
    emailIndisponibilidade: str
    mensagem: str = ""


class AneelResponseBuilder:
    """
    Builder para criar respostas no formato padrao ANEEL.

    Garante consistencia em todas as respostas da API.
    """

    DEFAULT_EMAIL = "radar@roraimaenergia.com.br"

    @classmethod
    def success(
        cls,
        data: dict[str, Any],
        message: str = "",
        email: str | None = None,
    ) -> dict[str, Any]:
        """
        Cria resposta de sucesso.

        Args:
            data: Dados da resposta
            message: Mensagem opcional
            email: Email de contato (usa padrao se None)

        Returns:
            Dicionario com resposta ANEEL
        """
        return {
            "idcStatusRequisicao": AneelStatusRequisicao.SUCESSO,
            "desStatusRequisicao": "Sucesso",
            "emailIndisponibilidade": email or cls.DEFAULT_EMAIL,
            "mensagem": message,
            **data,
        }

    @classmethod
    def error(
        cls,
        message: str,
        additional_data: dict[str, Any] | None = None,
        email: str | None = None,
    ) -> dict[str, Any]:
        """
        Cria resposta de erro.

        Args:
            message: Mensagem de erro
            additional_data: Dados adicionais
            email: Email de contato

        Returns:
            Dicionario com resposta de erro ANEEL
        """
        response = {
            "idcStatusRequisicao": AneelStatusRequisicao.ERRO,
            "desStatusRequisicao": "Erro",
            "emailIndisponibilidade": email or cls.DEFAULT_EMAIL,
            "mensagem": message,
        }
        if additional_data:
            response.update(additional_data)
        return response

    @classmethod
    def validation_error(
        cls,
        field: str,
        message: str,
    ) -> dict[str, Any]:
        """Cria resposta de erro de validacao."""
        return cls.error(f"Erro de validacao no campo '{field}': {message}")

    @classmethod
    def unauthorized(cls, message: str | None = None) -> dict[str, Any]:
        """Cria resposta de erro de autenticacao."""
        return cls.error(message or "Header x-api-key e obrigatorio")

    @classmethod
    def internal_error(cls, message: str | None = None) -> dict[str, Any]:
        """Cria resposta de erro interno."""
        return cls.error(
            message or "Erro interno do servidor. Tente novamente mais tarde."
        )

    @classmethod
    def service_unavailable(cls, message: str | None = None) -> dict[str, Any]:
        """Cria resposta de servico indisponivel."""
        return cls.error(
            message or "Servico temporariamente indisponivel. Tente novamente mais tarde."
        )

    @classmethod
    def not_found(cls, resource: str) -> dict[str, Any]:
        """Cria resposta de recurso nao encontrado."""
        return cls.error(f"{resource} nao encontrado")

    @classmethod
    def timeout(cls) -> dict[str, Any]:
        """Cria resposta de timeout."""
        return cls.error("Tempo limite de processamento excedido. Tente novamente.")
