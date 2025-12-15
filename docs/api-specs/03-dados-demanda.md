# API 3 - Dados Detalhados de Demanda
## `/dadosdemanda`

**Base Legal:** Ofício Circular nº 14/2025-SFE/ANEEL - Seção 5
**Prazo:** Dezembro/2025

---

## 1. Descrição

Retorna os **dados detalhados** de uma demanda específica, identificada pelo número de protocolo. Este endpoint permite à ANEEL consultar informações completas sobre uma demanda individual registrada na distribuidora.

**Disponibilidade de Dados:**
- Todas as demandas **em tratamento** (independentemente da data de abertura)
- Demandas **encerradas** há pelo menos **6 meses**

---

## 2. Endpoint

```
GET /dadosdemanda?numProtocolo={numero}
```

| Propriedade | Valor |
|-------------|-------|
| **Método** | GET |
| **Rota** | `dadosdemanda` |
| **Case Sensitivity** | Tudo em minúsculo |
| **Frequência de Consulta** | Sob demanda |
| **Horário de Disponibilidade** | Segunda a sábado, 8h às 20h (horário CTA ANEEL) |
| **Retenção de Dados** | Demandas em andamento + encerradas há 6 meses |

---

## 3. Parâmetros

### 3.1 Query Parameters

| Parâmetro | Tipo | Obrigatório | Formato | Descrição |
|-----------|------|-------------|---------|-----------|
| `numProtocolo` | string | Sim | Alfanumérico (até 30 caracteres) | Número do protocolo da demanda |

### 3.2 Regras do Parâmetro

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `numProtocolo` |
| **Canal de passagem** | Query String |
| **Tipo** | Alfanumérico (até 30 caracteres) |
| **Obrigatório** | Sim |
| **Sensibilidade** | Camel Case |

### 3.3 Exemplos de Requisição

**Consulta de demanda específica:**
```http
GET /dadosdemanda?numProtocolo=02157896542021565898742569875 HTTP/1.1
Host: api.roraimaenergia.com.br
x-api-key: sua-api-key
```

**Exemplo em cURL:**
```bash
curl -X GET "https://api.roraimaenergia.com.br/radar/dadosdemanda?numProtocolo=02157896542021565898742569875" \
     -H "x-api-key: sua-api-key"
```

**Exemplo em Python:**
```python
import requests

url = "https://api.roraimaenergia.com.br/radar/dadosdemanda"
headers = {
    "x-api-key": "sua-api-key"
}
params = {
    "numProtocolo": "02157896542021565898742569875"
}

response = requests.get(url, headers=headers, params=params)
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
  "demanda": {
    "numProtocolo": "02157896542021565898742569875",
    "numUC": "025467891234567890223210987654",
    "numCPFCNPJ": "12345678000132",
    "nomeTitularUC": "João Matias",
    "idcCanalAtendimento": 1,
    "idcTipologia": "10105",
    "idcStatus": 0,
    "idcProcedencia": 2,
    "dthAbertura": "01/01/2024 18:32",
    "dthEncerramento": null,
    "ideMunicipio": 1400050,
    "idcNivelTratamento": 0
  }
}
```

### 5.2 Campos do Response Principal

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `idcStatusRequisicao` | int | Sim | 1 = Sucesso, 2 = Erro |
| `mensagem` | string | Sim/Não* | Mensagem de erro (vazio se sucesso) |
| `demanda` | object | Sim | Objeto contendo os detalhes da demanda |

*Obrigatório apenas quando `idcStatusRequisicao` = 2

### 5.3 Campos do Objeto `demanda`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `numProtocolo` | string (30) | Sim | Número do protocolo da demanda |
| `numUC` | string (15) | Sim | Número da Unidade Consumidora |
| `numCPFCNPJ` | string (14) | Sim | CPF/CNPJ do titular da UC (sem formatação) |
| `nomeTitularUC` | string (50) | Sim | Nome do titular da Unidade Consumidora |
| `idcCanalAtendimento` | int | Sim | Código do canal de atendimento (ver tabela) |
| `idcTipologia` | string (7) | Sim | Código da tipologia (RH 2.992/2021) |
| `idcStatus` | int | Sim | Status da demanda (ver tabela) |
| `idcProcedencia` | int | Sim | Procedência da demanda (ver tabela) |
| `dthAbertura` | string | Sim | Data/hora de abertura (dd/MM/aaaa hh:mm) |
| `dthEncerramento` | string | Não | Data/hora de encerramento (dd/MM/aaaa hh:mm) |
| `ideMunicipio` | int | Sim | Código IBGE do município (7 dígitos) |
| `idcNivelTratamento` | int | Sim | Nível de tratamento conforme Caminho do Entendimento |

---

## 6. Códigos de Referência

### 6.1 Canal de Atendimento (`idcCanalAtendimento`)

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

### 6.2 Status da Demanda (`idcStatus`)

| Código | Descrição |
|--------|-----------|
| 0 | Em andamento |
| 1 | Encerrada |
| 2 | Outros |

### 6.3 Procedência da Demanda (`idcProcedencia`)

| Código | Descrição |
|--------|-----------|
| 0 | Improcedente |
| 1 | Procedente |
| 2 | Em tratamento |
| 3 | Outros |

### 6.4 Nível de Tratamento (`idcNivelTratamento`)

| Código | Descrição |
|--------|-----------|
| 0 | Primeiro nível (CTA) |
| 1 | Ouvidoria da distribuidora (segundo nível) |
| 2 | Outros |

### 6.5 Tipologias (`idcTipologia`)

As tipologias seguem a árvore apresentada no **Anexo I da Resolução Homologatória nº 2.992/2021**.

**Exemplos:**

| Código | Descrição |
|--------|-----------|
| 10101 | Reclamação - Falta de energia |
| 10102 | Reclamação - Qualidade de energia |
| 10103 | Reclamação - Oscilação de tensão |
| 10105 | Reclamação - Demora no atendimento |
| 10201 | Solicitação - Ligação nova |
| 10202 | Solicitação - Religação |
| 10301 | Informação - Fatura |
| 20101 | Reclamação - Cobrança indevida |

**Referência completa:** [RH 2.992/2021 - Anexo I](https://www2.aneel.gov.br/cedoc/reh20212992ti.pdf)

---

## 7. Regras de Negócio

### 7.1 Disponibilidade de Dados

| Tipo de Demanda | Disponibilidade |
|-----------------|-----------------|
| Em andamento | Sempre disponível (independente da data de abertura) |
| Encerrada | Disponível se encerrada há pelo menos 6 meses |

### 7.2 Horário de Funcionamento

| Dia | Horário |
|-----|---------|
| Segunda a Sábado | 8h às 20h (horário de Brasília) |
| Domingo | Indisponível |

**Nota:** O horário segue o funcionamento da CTA (Central de Teleatendimento) da ANEEL.

### 7.3 Formato de Datas

| Campo | Formato | Exemplo |
|-------|---------|---------|
| `dthAbertura` | dd/MM/aaaa hh:mm | 01/01/2024 18:32 |
| `dthEncerramento` | dd/MM/aaaa hh:mm | 15/01/2024 10:45 |

### 7.4 Formato de CPF/CNPJ

O campo `numCPFCNPJ` deve ser enviado **sem formatação** (sem pontos, traços ou barras):
- CPF: 11 dígitos (ex: `12345678901`)
- CNPJ: 14 dígitos (ex: `12345678000132`)

---

## 8. Exemplos de Resposta

### 8.1 Sucesso - Demanda em Andamento

```json
{
  "idcStatusRequisicao": 1,
  "mensagem": "",
  "demanda": {
    "numProtocolo": "02157896542021565898742569875",
    "numUC": "123456789012345",
    "numCPFCNPJ": "12345678901",
    "nomeTitularUC": "Maria Silva Santos",
    "idcCanalAtendimento": 2,
    "idcTipologia": "10101",
    "idcStatus": 0,
    "idcProcedencia": 2,
    "dthAbertura": "10/12/2025 14:30",
    "dthEncerramento": null,
    "ideMunicipio": 1400050,
    "idcNivelTratamento": 0
  }
}
```

### 8.2 Sucesso - Demanda Encerrada

```json
{
  "idcStatusRequisicao": 1,
  "mensagem": "",
  "demanda": {
    "numProtocolo": "98765432102025123456789012345",
    "numUC": "987654321098765",
    "numCPFCNPJ": "98765432000198",
    "nomeTitularUC": "Empresa ABC Ltda",
    "idcCanalAtendimento": 1,
    "idcTipologia": "10201",
    "idcStatus": 1,
    "idcProcedencia": 1,
    "dthAbertura": "01/06/2025 09:15",
    "dthEncerramento": "05/06/2025 16:42",
    "ideMunicipio": 1400175,
    "idcNivelTratamento": 0
  }
}
```

### 8.3 Sucesso - Demanda na Ouvidoria

```json
{
  "idcStatusRequisicao": 1,
  "mensagem": "",
  "demanda": {
    "numProtocolo": "55544433302025111222333444555",
    "numUC": "555444333222111",
    "numCPFCNPJ": "55544433321",
    "nomeTitularUC": "José Carlos Oliveira",
    "idcCanalAtendimento": 4,
    "idcTipologia": "20101",
    "idcStatus": 0,
    "idcProcedencia": 2,
    "dthAbertura": "15/11/2025 11:20",
    "dthEncerramento": null,
    "ideMunicipio": 1400209,
    "idcNivelTratamento": 1
  }
}
```

### 8.4 Sucesso - Protocolo Não Encontrado

```json
{
  "idcStatusRequisicao": 1,
  "mensagem": "",
  "demanda": {}
}
```

### 8.5 Erro

```json
{
  "idcStatusRequisicao": 2,
  "mensagem": "Erro ao obter dados demanda - NullReference!",
  "demanda": {}
}
```

---

## 9. Integração com Sistemas Internos

### 9.1 Sistema CRM

| Dado | Origem |
|------|--------|
| Dados da demanda | VW_DEMANDAS_RADAR |
| Dados da UC | VW_UNIDADES_CONSUMIDORAS_RADAR |
| Dados do consumidor | VW_CONSUMIDORES_RADAR |

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

### 9.3 Mapeamento de Status

| Sistema Interno | Código ANEEL |
|-----------------|--------------|
| ABERTA / EM_ANDAMENTO | 0 (Em andamento) |
| ENCERRADA / FINALIZADA | 1 (Encerrada) |
| CANCELADA / OUTROS | 2 (Outros) |

### 9.4 Mapeamento de Procedência

| Sistema Interno | Código ANEEL |
|-----------------|--------------|
| IMPROCEDENTE | 0 (Improcedente) |
| PROCEDENTE | 1 (Procedente) |
| EM_ANALISE / PENDENTE | 2 (Em tratamento) |
| NAO_SE_APLICA / OUTROS | 3 (Outros) |

### 9.5 Query Conceitual

```sql
SELECT
    d.protocolo AS numProtocolo,
    d.numero_uc AS numUC,
    c.cpf_cnpj AS numCPFCNPJ,
    c.nome AS nomeTitularUC,
    d.canal_atendimento AS idcCanalAtendimento,
    d.tipologia AS idcTipologia,
    CASE d.status
        WHEN 'EM_ANDAMENTO' THEN 0
        WHEN 'ENCERRADA' THEN 1
        ELSE 2
    END AS idcStatus,
    CASE d.procedencia
        WHEN 'IMPROCEDENTE' THEN 0
        WHEN 'PROCEDENTE' THEN 1
        WHEN 'EM_TRATAMENTO' THEN 2
        ELSE 3
    END AS idcProcedencia,
    TO_CHAR(d.data_abertura, 'DD/MM/YYYY HH24:MI') AS dthAbertura,
    TO_CHAR(d.data_encerramento, 'DD/MM/YYYY HH24:MI') AS dthEncerramento,
    u.municipio_ibge AS ideMunicipio,
    CASE d.setor
        WHEN 'CTA' THEN 0
        WHEN 'OUVIDORIA' THEN 1
        ELSE 2
    END AS idcNivelTratamento
FROM VW_DEMANDAS_RADAR d
JOIN VW_CONSUMIDORES_RADAR c ON d.id_consumidor = c.id_consumidor
JOIN VW_UNIDADES_CONSUMIDORAS_RADAR u ON d.numero_uc = u.numero_uc
WHERE d.protocolo = :numProtocolo
  AND (d.status = 'EM_ANDAMENTO'
       OR (d.status = 'ENCERRADA' AND d.data_encerramento >= ADD_MONTHS(SYSDATE, -6)));
```

---

## 10. Códigos de Erro HTTP

| Código | Descrição | Causa |
|--------|-----------|-------|
| 200 | OK | Requisição bem-sucedida (mesmo se protocolo não encontrado) |
| 400 | Bad Request | Parâmetro `numProtocolo` ausente ou inválido |
| 401 | Unauthorized | API Key inválida ou ausente |
| 403 | Forbidden | IP não autorizado |
| 500 | Internal Server Error | Erro interno (verificar `mensagem` no JSON) |

---

## 11. Considerações de Segurança

### 11.1 Dados Sensíveis

Este endpoint retorna dados pessoais sensíveis (CPF/CNPJ, nome do titular). Por isso:

- O acesso na ANEEL é restrito a público específico com login e senha
- Todos os acessos são registrados em log pela ANEEL
- A API Key deve ser mantida em sigilo pela distribuidora e pela ANEEL

### 11.2 LGPD

Os dados retornados estão sujeitos à Lei Geral de Proteção de Dados (LGPD). A distribuidora deve garantir que:

- Apenas dados necessários são expostos
- O acesso é devidamente logado internamente
- Os dados são transmitidos de forma segura (HTTPS)

---

## 12. Checklist de Implementação

- [ ] Endpoint `/dadosdemanda` respondendo em minúsculo
- [ ] Parâmetro `numProtocolo` via query string funcionando
- [ ] Autenticação via `x-api-key` no header
- [ ] Whitelist de IP da ANEEL configurado
- [ ] Resposta em JSON com camelCase
- [ ] Integração com sistema CRM implementada
- [ ] Mapeamento de canais de atendimento configurado
- [ ] Mapeamento de status configurado
- [ ] Mapeamento de procedência configurado
- [ ] Mapeamento de níveis de tratamento configurado
- [ ] Filtro de demandas (em andamento + encerradas há 6 meses) implementado
- [ ] Formato de datas correto (dd/MM/aaaa hh:mm)
- [ ] CPF/CNPJ sem formatação
- [ ] Retorno de objeto vazio quando protocolo não encontrado
- [ ] Log de acessos implementado
- [ ] Testes de segurança realizados
- [ ] Swagger/OpenAPI documentado

---

*Documentação baseada no Ofício Circular 14/2025-SFE/ANEEL V4 (23/10/2025)*
