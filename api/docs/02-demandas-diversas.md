# API 2 - Quantitativo de Demandas Diversas
## `/quantitativodemandasdiversas`

**Base Legal:** Ofício Circular nº 14/2025-SFE/ANEEL - Seção 4
**Prazo:** Dezembro/2025

---

## 1. Descrição

Retorna o quantitativo **acumulado** de demandas diversas (em tratamento, registradas e encerradas) do dia atual, agrupadas por:
- **Nível de Atendimento** (1º nível / 2º nível)
- **Canal de Atendimento** (presencial, telefone, internet, etc.)
- **Tipologia** (conforme RH 2.992/2021)

---

## 2. Endpoint

```
GET /quantitativodemandasdiversas
```

| Propriedade | Valor |
|-------------|-------|
| **Método** | GET |
| **Rota** | `quantitativodemandasdiversas` |
| **Case Sensitivity** | Tudo em minúsculo |
| **Frequência de Consulta** | A cada 30 minutos (6h às 24h, seg-sex) |
| **Retenção ANEEL** | 36 meses (última consulta do dia) |

---

## 3. Parâmetros

Este endpoint **não possui parâmetros**. Retorna sempre os dados acumulados do dia atual até o momento da consulta.

### 3.1 Exemplo de Requisição

```http
GET /quantitativodemandasdiversas HTTP/1.1
Host: api.roraimaenergia.com.br
x-api-key: sua-api-key
```

---

## 4. Headers

| Header | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `x-api-key` | string | Sim | Chave de autenticação fornecida pela distribuidora |

---

## 5. Resposta

### 5.1 Estrutura da Resposta

```json
{
  "idcStatusRequisicao": 1,
  "mensagem": "",
  "demandasDiversas": [
    {
      "idcNivelAtendimento": 1,
      "idcCanalAtendimento": 2,
      "idcTipologia": "10101",
      "qtdAndamentoNoMomento": 15,
      "qtdRegistradaNoDia": 50,
      "qtdImprocedenteNoDia": 5,
      "qtdProcedenteNoDia": 30,
      "qtdSemProcedenciaNoDia": 10
    }
  ]
}
```

### 5.2 Campos do Response Principal

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `idcStatusRequisicao` | int | Sim | 1 = Sucesso, 2 = Erro |
| `mensagem` | string | Sim/Não* | Mensagem de erro (vazio se sucesso) |
| `demandasDiversas` | array | Sim | Lista de demandas agrupadas |

*Obrigatório apenas quando `idcStatusRequisicao` = 2

### 5.3 Campos do Array `demandasDiversas`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `idcNivelAtendimento` | int | Sim | Nível de atendimento (ver tabela) |
| `idcCanalAtendimento` | int | Sim | Canal de atendimento (ver tabela) |
| `idcTipologia` | string (7) | Sim | Código da tipologia (RH 2.992/2021) |
| `qtdAndamentoNoMomento` | int | Sim | Demandas em tratamento no momento |
| `qtdRegistradaNoDia` | int | Sim | Novas demandas registradas no dia (acumulado) |
| `qtdImprocedenteNoDia` | int | Sim | Demandas encerradas como improcedentes no dia |
| `qtdProcedenteNoDia` | int | Sim | Demandas encerradas como procedentes no dia |
| `qtdSemProcedenciaNoDia` | int | Sim | Demandas encerradas sem procedência definida no dia |

---

## 6. Códigos de Referência

### 6.1 Nível de Atendimento (`idcNivelAtendimento`)

| Código | Descrição | Setor Típico |
|--------|-----------|--------------|
| 1 | 1º Nível (CTA) | Call Center, Agências, Digital |
| 2 | 2º Nível (Ouvidoria) | Ouvidoria da distribuidora |

### 6.2 Canal de Atendimento (`idcCanalAtendimento`)

| Código | Descrição |
|--------|-----------|
| 1 | Presencial |
| 2 | Telefônico |
| 3 | Agência Virtual |
| 4 | consumidor.gov |
| 5 | Aplicativo |
| 6 | E-mail |
| 7 | SMS |
| 8 | Redes Sociais |
| 9 | Outros |
| 10 | Chatbot |
| 11 | Chat Humano |
| 12 | WhatsApp |

### 6.3 Tipologias (`idcTipologia`)

As tipologias seguem a árvore apresentada no **Anexo I da Resolução Homologatória nº 2.992/2021**.

**Exemplos:**

| Código | Descrição |
|--------|-----------|
| 10101 | Reclamação - Falta de energia |
| 10102 | Reclamação - Qualidade de energia |
| 10103 | Reclamação - Oscilação de tensão |
| 10201 | Solicitação - Ligação nova |
| 10202 | Solicitação - Religação |
| 10301 | Informação - Fatura |
| 20101 | Reclamação - Cobrança indevida |

**Referência completa:** [RH 2.992/2021 - Anexo I](https://www2.aneel.gov.br/cedoc/reh20212992ti.pdf)

---

## 7. Regras de Negócio

### 7.1 Agrupamento dos Dados

Os dados são agrupados pelos campos **chave**:
1. `idcNivelAtendimento`
2. `idcCanalAtendimento`
3. `idcTipologia`

### 7.2 Campos de Quantidade

| Campo | Período de Contagem |
|-------|---------------------|
| `qtdAndamentoNoMomento` | Momento exato da consulta (snapshot) |
| `qtdRegistradaNoDia` | 00:00 até momento da consulta (acumulado) |
| `qtdImprocedenteNoDia` | 00:00 até momento da consulta (acumulado) |
| `qtdProcedenteNoDia` | 00:00 até momento da consulta (acumulado) |
| `qtdSemProcedenciaNoDia` | 00:00 até momento da consulta (acumulado) |

### 7.3 Volume Máximo de Registros

| Níveis | Canais | Tipologias | Total Máximo |
|--------|--------|------------|--------------|
| 2 | 12 | 117 | **2.808 registros** |

---

## 8. Exemplos de Resposta

### 8.1 Sucesso com Dados

```json
{
  "idcStatusRequisicao": 1,
  "mensagem": "",
  "demandasDiversas": [
    {
      "idcNivelAtendimento": 1,
      "idcCanalAtendimento": 1,
      "idcTipologia": "10101",
      "qtdAndamentoNoMomento": 6,
      "qtdRegistradaNoDia": 12,
      "qtdImprocedenteNoDia": 1,
      "qtdProcedenteNoDia": 2,
      "qtdSemProcedenciaNoDia": 9
    },
    {
      "idcNivelAtendimento": 1,
      "idcCanalAtendimento": 2,
      "idcTipologia": "10101",
      "qtdAndamentoNoMomento": 15,
      "qtdRegistradaNoDia": 45,
      "qtdImprocedenteNoDia": 3,
      "qtdProcedenteNoDia": 20,
      "qtdSemProcedenciaNoDia": 12
    },
    {
      "idcNivelAtendimento": 2,
      "idcCanalAtendimento": 1,
      "idcTipologia": "10102",
      "qtdAndamentoNoMomento": 7,
      "qtdRegistradaNoDia": 15,
      "qtdImprocedenteNoDia": 3,
      "qtdProcedenteNoDia": 0,
      "qtdSemProcedenciaNoDia": 12
    }
  ]
}
```

### 8.2 Sucesso sem Dados

```json
{
  "idcStatusRequisicao": 1,
  "mensagem": "",
  "demandasDiversas": []
}
```

### 8.3 Erro

```json
{
  "idcStatusRequisicao": 2,
  "mensagem": "Erro ao calcular quantitativos - Unable to connect to database instance!",
  "demandasDiversas": []
}
```

---

## 9. Integração com Sistemas Internos

### 9.1 Sistema CRM

| Dado | Origem |
|------|--------|
| Demandas do dia | VW_DEMANDAS_RADAR |
| Demandas agregadas | VW_DEMANDAS_AGREGADAS_RADAR |

### 9.2 Mapeamento de Canais

| Sistema Interno | Código ANEEL |
|-----------------|--------------|
| Agência | 1 (Presencial) |
| Call Center 0800 | 2 (Telefônico) |
| Portal Web | 3 (Agência Virtual) |
| consumidor.gov | 4 (consumidor.gov) |
| App Mobile | 5 (Aplicativo) |
| E-mail | 6 (E-mail) |
| WhatsApp | 12 (WhatsApp) |

### 9.3 Mapeamento de Níveis

| Sistema Interno | Código ANEEL |
|-----------------|--------------|
| CTA / Call Center | 1 (1º Nível) |
| Retaguarda | 1 (1º Nível) |
| Ouvidoria | 2 (2º Nível) |

### 9.4 Query Conceitual

```sql
SELECT
    CASE setor WHEN 'OUVIDORIA' THEN 2 ELSE 1 END AS idcNivelAtendimento,
    canal_atendimento AS idcCanalAtendimento,
    tipologia AS idcTipologia,
    SUM(CASE WHEN status = 'EM_ANDAMENTO' THEN 1 ELSE 0 END) AS qtdAndamentoNoMomento,
    SUM(CASE WHEN TRUNC(data_abertura) = TRUNC(SYSDATE) THEN 1 ELSE 0 END) AS qtdRegistradaNoDia,
    SUM(CASE WHEN status = 'ENCERRADA' AND procedencia = 'IMPROCEDENTE'
             AND TRUNC(data_encerramento) = TRUNC(SYSDATE) THEN 1 ELSE 0 END) AS qtdImprocedenteNoDia,
    SUM(CASE WHEN status = 'ENCERRADA' AND procedencia = 'PROCEDENTE'
             AND TRUNC(data_encerramento) = TRUNC(SYSDATE) THEN 1 ELSE 0 END) AS qtdProcedenteNoDia,
    SUM(CASE WHEN status = 'ENCERRADA' AND procedencia = 'SEM_PROCEDENCIA'
             AND TRUNC(data_encerramento) = TRUNC(SYSDATE) THEN 1 ELSE 0 END) AS qtdSemProcedenciaNoDia
FROM VW_DEMANDAS_RADAR
GROUP BY
    CASE setor WHEN 'OUVIDORIA' THEN 2 ELSE 1 END,
    canal_atendimento,
    tipologia;
```

---

## 10. Códigos de Erro HTTP

| Código | Descrição | Causa |
|--------|-----------|-------|
| 200 | OK | Requisição bem-sucedida |
| 401 | Unauthorized | API Key inválida ou ausente |
| 403 | Forbidden | IP não autorizado |
| 500 | Internal Server Error | Erro interno (verificar `mensagem` no JSON) |

---

## 11. Checklist de Implementação

- [ ] Endpoint `/quantitativodemandasdiversas` respondendo em minúsculo
- [ ] Autenticação via `x-api-key` no header
- [ ] Whitelist de IP da ANEEL configurado
- [ ] Resposta em JSON com camelCase
- [ ] Integração com sistema CRM implementada
- [ ] Mapeamento de canais de atendimento configurado
- [ ] Mapeamento de níveis de atendimento configurado
- [ ] Mapeamento de tipologias (RH 2.992) configurado
- [ ] Cálculo de acumulados do dia implementado
- [ ] Testes de carga realizados
- [ ] Swagger/OpenAPI documentado

---

*Documentação baseada no Ofício Circular 14/2025-SFE/ANEEL V4 (23/10/2025)*
