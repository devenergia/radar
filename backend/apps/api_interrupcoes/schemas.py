"""Schemas Pydantic para a API 1 - Interrupcoes Ativas."""

from typing import Any

from pydantic import BaseModel, Field


class InterrupcaoAgregadaItem(BaseModel):
    """Item de interrupcao agregada no formato ANEEL."""

    ideConjuntoUnidadeConsumidora: int = Field(
        ..., description="Identificador do conjunto eletrico"
    )
    ideMunicipio: int = Field(
        ..., description="Codigo IBGE do municipio (7 digitos)"
    )
    qtdUCsAtendidas: int = Field(
        ..., description="Quantidade de UCs atendidas no conjunto"
    )
    qtdOcorrenciaProgramada: int = Field(
        ..., description="Quantidade de UCs afetadas por interrupcoes programadas"
    )
    qtdOcorrenciaNaoProgramada: int = Field(
        ..., description="Quantidade de UCs afetadas por interrupcoes nao programadas"
    )


class InterrupcoesAtivasResponse(BaseModel):
    """Resposta do endpoint de interrupcoes ativas - Formato ANEEL V4."""

    idcStatusRequisicao: int = Field(
        ..., description="1 = Sucesso, 2 = Erro"
    )
    emailIndisponibilidade: str = Field(
        ..., description="Email para contato em caso de indisponibilidade"
    )
    mensagem: str = Field(
        default="", description="Mensagem de erro (vazio se sucesso)"
    )
    interrupcaoFornecimento: list[InterrupcaoAgregadaItem] = Field(
        default_factory=list,
        description="Lista de interrupcoes agregadas por municipio/conjunto",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "idcStatusRequisicao": 1,
                "emailIndisponibilidade": "radar@roraimaenergia.com.br",
                "mensagem": "",
                "interrupcaoFornecimento": [
                    {
                        "ideConjuntoUnidadeConsumidora": 1,
                        "ideMunicipio": 1400100,
                        "qtdUCsAtendidas": 125000,
                        "qtdOcorrenciaProgramada": 150,
                        "qtdOcorrenciaNaoProgramada": 45,
                    }
                ],
            }
        }
    }


class HealthResponse(BaseModel):
    """Resposta do endpoint de health check."""

    status: str = Field(..., description="Status geral: healthy, unhealthy, degraded")
    version: str = Field(..., description="Versao da API")
    checks: dict[str, Any] = Field(..., description="Detalhes dos checks")


class ErrorResponse(BaseModel):
    """Resposta de erro padrao ANEEL V4."""

    idcStatusRequisicao: int = Field(default=2, description="2 = Erro")
    emailIndisponibilidade: str = Field(
        ..., description="Email para contato em caso de indisponibilidade"
    )
    mensagem: str = Field(..., description="Mensagem de erro")
    interrupcaoFornecimento: list[InterrupcaoAgregadaItem] = Field(
        default_factory=list,
        description="Lista vazia em caso de erro",
    )
