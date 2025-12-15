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

```python
# app/domain/schemas/base.py

from pydantic import BaseModel, Field
from typing import Literal

class BaseResponse(BaseModel):
    """Estrutura base de resposta ANEEL"""
    idc_status_requisicao: Literal[1, 2] = Field(
        ...,
        alias="idcStatusRequisicao",
        description="1 = Sucesso, 2 = Erro"
    )
    email_indisponibilidade: str = Field(
        ...,
        alias="emailIndisponibilidade",
        max_length=50,
        description="Email para contato"
    )
    mensagem: str = Field(
        default="",
        description="Vazio se sucesso, mensagem de erro se falha"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "idcStatusRequisicao": 1,
                "emailIndisponibilidade": "radar@roraimaenergia.com.br",
                "mensagem": ""
            }
        }
```

### API 1 - Interrupções Ativas

```python
# app/domain/schemas/interrupcao.py

from typing import List
from pydantic import BaseModel, Field

class InterrupcaoFornecimentoItem(BaseModel):
    """Item de interrupção de fornecimento"""
    ide_conjunto_unidade_consumidora: int = Field(
        ...,
        alias="ideConjuntoUnidadeConsumidora",
        ge=1,
        description="Código do conjunto"
    )
    ide_municipio: int = Field(
        ...,
        alias="ideMunicipio",
        ge=1000000,
        le=9999999,
        description="Código IBGE 7 dígitos"
    )
    qtd_ucs_atendidas: int = Field(
        ...,
        alias="qtdUCsAtendidas",
        ge=0,
        description="Total de UCs no conjunto"
    )
    qtd_ocorrencia_programada: int = Field(
        ...,
        alias="qtdOcorrenciaProgramada",
        ge=0,
        description="UCs com interrupção programada"
    )
    qtd_ocorrencia_nao_programada: int = Field(
        ...,
        alias="qtdOcorrenciaNaoProgramada",
        ge=0,
        description="UCs com interrupção não programada"
    )

    class Config:
        populate_by_name = True


class InterrupcoesAtivasResponse(BaseResponse):
    """Resposta da API de interrupções ativas"""
    interrupcao_fornecimento: List[InterrupcaoFornecimentoItem] = Field(
        default_factory=list,
        alias="interrupcaoFornecimento"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "idcStatusRequisicao": 1,
                "emailIndisponibilidade": "radar@roraimaenergia.com.br",
                "mensagem": "",
                "interrupcaoFornecimento": [
                    {
                        "ideConjuntoUnidadeConsumidora": 1001,
                        "ideMunicipio": 1400100,
                        "qtdUCsAtendidas": 1500,
                        "qtdOcorrenciaProgramada": 100,
                        "qtdOcorrenciaNaoProgramada": 0
                    }
                ]
            }
        }
```

### API 2 - Dados da Demanda

```python
# app/domain/schemas/demanda.py

from typing import List
from pydantic import BaseModel, Field

class DadosDemandaItem(BaseModel):
    """Item de dados de demanda"""
    # Campos conforme especificação ANEEL
    ...

class DadosDemandaResponse(BaseResponse):
    """Resposta da API de dados de demanda"""
    dados_demanda: List[DadosDemandaItem] = Field(
        default_factory=list,
        alias="dadosDemanda"
    )

    class Config:
        populate_by_name = True
```

### Mapper de Resposta

```python
# app/application/mappers/response_mapper.py

from typing import List
from app.domain.entities import InterrupcaoAgregada
from app.domain.schemas.interrupcao import (
    InterrupcoesAtivasResponse,
    InterrupcaoFornecimentoItem
)
from app.domain.schemas.base import BaseResponse

class ResponseMapper:
    """Mapper de entidades de domínio para respostas ANEEL"""

    @staticmethod
    def to_interrupcoes_ativas_response(
        interrupcoes: List[InterrupcaoAgregada],
        email: str
    ) -> InterrupcoesAtivasResponse:
        """Mapeia lista de interrupções para resposta ANEEL"""
        return InterrupcoesAtivasResponse(
            idc_status_requisicao=1,
            email_indisponibilidade=email,
            mensagem="",
            interrupcao_fornecimento=[
                InterrupcaoFornecimentoItem(
                    ide_conjunto_unidade_consumidora=i.id_conjunto,
                    ide_municipio=i.municipio_ibge,
                    qtd_ucs_atendidas=i.qtd_ucs_atendidas,
                    qtd_ocorrencia_programada=i.qtd_ucs_programada,
                    qtd_ocorrencia_nao_programada=i.qtd_ucs_nao_programada
                )
                for i in interrupcoes
            ]
        )

    @staticmethod
    def to_error_response(error: Exception, email: str) -> BaseResponse:
        """Mapeia erro para resposta ANEEL"""
        return BaseResponse(
            idc_status_requisicao=2,
            email_indisponibilidade=email,
            mensagem=str(error)
        )
```

### Validação de Schema com Pydantic

Pydantic já fornece validação automática através dos modelos:

```python
# Exemplo de uso em rota
from fastapi import APIRouter
from app.domain.schemas.interrupcao import InterrupcoesAtivasResponse

router = APIRouter()

@router.get(
    "/quantitativointerrupcoesativas",
    response_model=InterrupcoesAtivasResponse,
    response_model_by_alias=True  # Usa os alias (camelCase) na resposta
)
async def get_interrupcoes_ativas():
    """
    Endpoint que retorna interrupções ativas.
    Pydantic garante que a resposta está conforme o schema.
    """
    # Lógica de negócio
    ...
```

### Convenções de Nomenclatura

| Convenção ANEEL | Implementação Python | Alias Pydantic |
|-----------------|---------------------|----------------|
| camelCase | snake_case | camelCase |
| Prefixo `ide` | Identificadores (ide_conjunto, ide_municipio) | ideConjunto, ideMunicipio |
| Prefixo `idc` | Indicadores (idc_status_requisicao) | idcStatusRequisicao |
| Prefixo `qtd` | Quantidades (qtd_ucs_atendidas) | qtdUCsAtendidas |
| Prefixo `dth` | Data/Hora (dth_recuperacao) | dthRecuperacao |

## Consequências

### Positivas

- **Conformidade**: Atende exatamente à especificação da ANEEL
- **Interoperabilidade**: Todas as distribuidoras usam mesmo formato
- **Validação**: Pydantic valida automaticamente tipos e constraints
- **Consistência**: Mesma estrutura para sucesso e erro
- **Type Safety**: Tipos Python validados em tempo de execução
- **Documentação Automática**: OpenAPI/Swagger gerado automaticamente

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
5. **SEMPRE** usar `response_model_by_alias=True` para retornar camelCase

## Exemplo de Teste

```python
# tests/unit/test_response_mapper.py

import pytest
from app.application.mappers.response_mapper import ResponseMapper
from app.domain.entities import InterrupcaoAgregada

def test_to_interrupcoes_ativas_response():
    # Arrange
    interrupcoes = [
        InterrupcaoAgregada(
            id_conjunto=1001,
            municipio_ibge=1400100,
            qtd_ucs_atendidas=1500,
            qtd_ucs_programada=100,
            qtd_ucs_nao_programada=0
        )
    ]

    # Act
    response = ResponseMapper.to_interrupcoes_ativas_response(
        interrupcoes,
        "radar@roraimaenergia.com.br"
    )

    # Assert
    assert response.idc_status_requisicao == 1
    assert response.mensagem == ""
    assert len(response.interrupcao_fornecimento) == 1

    # Validar que o JSON está em camelCase
    json_data = response.model_dump(by_alias=True)
    assert "idcStatusRequisicao" in json_data
    assert "interrupcaoFornecimento" in json_data
```

## Referências

- Ofício Circular 14/2025-SFE/ANEEL V4 (23/10/2025)
- Especificação JSON das APIs no ofício
- [Pydantic Documentation](https://docs.pydantic.dev/)
