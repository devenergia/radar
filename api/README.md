# API RADAR - Roraima Energia
## Rede de Acompanhamento e Diagnóstico da Distribuição

**Versão:** 1.0
**Base Legal:** Ofício Circular nº 14/2025-SFE/ANEEL (V4 - 23/10/2025)
**Data:** Dezembro/2025

---

## 1. Visão Geral

A API RADAR é um serviço REST desenvolvido pela Roraima Energia para atender às exigências da ANEEL, permitindo que a agência reguladora consulte dados sobre:

1. **Interrupções de fornecimento** - Quantitativo de UCs com interrupções ativas
2. **Demandas diversas** - Quantitativo acumulado de demandas por canal/tipologia
3. **Dados de demanda** - Detalhes de uma demanda específica por protocolo

---

## 2. Endpoints

| # | Endpoint | Método | Descrição | Frequência |
|---|----------|--------|-----------|------------|
| 1 | `/quantitativointerrupcoesativas` | GET | Interrupções ativas por município/conjunto | A cada 30 min |
| 2 | `/quantitativodemandasdiversas` | GET | Quantitativo de demandas do dia | A cada 30 min |
| 3 | `/dadosdemanda` | GET | Detalhes de uma demanda específica | Sob demanda |

---

## 3. URL Base

```
https://api.roraimaenergia.com.br/radar
```

**Exemplo completo:**
```
https://api.roraimaenergia.com.br/radar/quantitativointerrupcoesativas
```

---

## 4. Autenticação

Todas as requisições devem incluir a API Key no header:

```http
x-api-key: {sua-api-key}
```

**Exemplo em Python:**
```python
import requests

url = "https://api.roraimaenergia.com.br/radar/quantitativointerrupcoesativas"
headers = {
    "x-api-key": "sua-api-key-aqui"
}

response = requests.get(url, headers=headers)
```

**Exemplo em cURL:**
```bash
curl -X GET "https://api.roraimaenergia.com.br/radar/quantitativointerrupcoesativas" \
     -H "x-api-key: sua-api-key-aqui"
```

---

## 5. Segurança

| Requisito | Implementação |
|-----------|---------------|
| **Protocolo** | HTTPS obrigatório |
| **Autenticação** | API Key no header `x-api-key` |
| **Whitelist IP** | Restrito ao bloco ANEEL: `200.198.220.128/25` |
| **Padrões** | e-Ping (gov.br) + Guia de Requisitos Mínimos de APIs |

---

## 6. Respostas

### 6.1 Códigos HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 401 | Não autorizado (API Key inválida) |
| 403 | Proibido (IP não autorizado) |
| 500 | Erro interno do servidor |

### 6.2 Estrutura Padrão de Resposta

```json
{
  "idcStatusRequisicao": 1,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "",
  ...
}
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `idcStatusRequisicao` | int | 1 = Sucesso, 2 = Erro |
| `emailIndisponibilidade` | string | Email para contato em caso de indisponibilidade |
| `mensagem` | string | Vazio se sucesso, mensagem de erro se falha |

---

## 7. Estrutura da Documentação

```
api/
├── README.md                          # Este arquivo
├── docs/
│   ├── 01-interrupcoes.md            # Documentação Endpoint 1
│   ├── 02-demandas-diversas.md       # Documentação Endpoint 2
│   ├── 03-dados-demanda.md           # Documentação Endpoint 3
│   ├── 04-seguranca.md               # Documentação de Segurança
│   ├── 05-codigos-referencia.md      # Códigos IBGE, Tipologias, etc.
│   └── 06-integracao-sistemas.md     # Integração com sistemas internos
├── specs/
│   └── openapi.yaml                  # Especificação OpenAPI 3.0
└── examples/
    ├── requests.http                 # Exemplos de requisições
    ├── responses/                    # Exemplos de respostas JSON
    │   ├── interrupcoes-sucesso.json
    │   ├── interrupcoes-vazio.json
    │   ├── interrupcoes-erro.json
    │   ├── demandas-sucesso.json
    │   └── ...
    └── python/                       # Exemplos em Python
        └── client.py
```

---

## 8. Prazos ANEEL

| Endpoint | Prazo | Status |
|----------|-------|--------|
| `/quantitativointerrupcoesativas` | Dezembro/2025 | Em desenvolvimento |
| `/quantitativodemandasdiversas` | Dezembro/2025 | Em desenvolvimento |
| `/dadosdemanda` | Dezembro/2025 | Em desenvolvimento |
| Consulta retroativa (dthRecuperacao) | Abril/2026 | Planejado |

---

## 9. Contatos

| Função | Email |
|--------|-------|
| Indisponibilidade API | radar@roraimaenergia.com.br |
| Suporte Técnico | ti.radar@roraimaenergia.com.br |

---

## 10. Changelog

| Versão | Data | Alterações |
|--------|------|------------|
| 1.0 | Dez/2025 | Versão inicial conforme Ofício Circular 14/2025 V4 |

---

## 11. Referências

- [Ofício Circular nº 14/2025-SFE/ANEEL](./Oficio_Circular_14-2025_SMA-ANEEL_RADAR.pdf)
- [Resolução Homologatória nº 2.992/2021 - Tipologias](https://www2.aneel.gov.br/cedoc/reh20212992ti.pdf)
- [Códigos IBGE Municípios](https://www.ibge.gov.br/explica/codigos-dos-municipios.php)
- [e-Ping - Padrões de Interoperabilidade](https://governoeletronico.gov.br)
- [Guia de Requisitos Mínimos de APIs](https://www.gov.br/governodigital/pt-br/seguranca-e-protecao-de-dados/guias/guia_requisitos_minimos_apis.pdf)

---

*Documentação gerada em Dezembro/2025 - Projeto RADAR - Roraima Energia S/A*
