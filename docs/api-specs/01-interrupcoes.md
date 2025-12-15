# API 1 - Quantitativo de Interrupções Ativas
## `/quantitativointerrupcoesativas`

**Base Legal:** Ofício Circular nº 14/2025-SFE/ANEEL - Seção 3
**Prazo:** Dezembro/2025

---

## 1. Descrição

Retorna o quantitativo de unidades consumidoras com interrupção do fornecimento de energia elétrica **ativas no momento da consulta**. Interrupções já restabelecidas NÃO devem ser incluídas.

Os dados são agrupados por:
- **Município** (código IBGE)
- **Conjunto Elétrico** (código do conjunto)
- **Tipo de Interrupção** (programada / não programada)

---

## 2. Endpoint

```
GET /quantitativointerrupcoesativas
```

| Propriedade | Valor |
|-------------|-------|
| **Método** | GET |
| **Rota** | `quantitativointerrupcoesativas` |
| **Case Sensitivity** | Tudo em minúsculo |
| **Frequência de Consulta** | A cada 30 minutos |
| **Retenção ANEEL** | 36 meses |

---

## 3. Parâmetros

### 3.1 Query Parameters

| Parâmetro | Tipo | Obrigatório | Formato | Descrição |
|-----------|------|-------------|---------|-----------|
| `dthRecuperacao` | string | Não | `dd/mm/yyyy hh:mm` | Data/hora para recuperação de dados históricos |

### 3.2 Comportamento do Parâmetro

| Cenário | Comportamento |
|---------|---------------|
| **Sem parâmetro** | Retorna dados do momento exato da requisição |
| **Com parâmetro** | Retorna dados correspondentes à data/hora informada |

**Importante:**
- Formato do parâmetro: `dd/mm/yyyy hh:mm` (horário de Brasília)
- A distribuidora deve manter dados dos **últimos 7 dias** para recuperação
- A funcionalidade de consulta retroativa será utilizada pela ANEEL a partir de **01/04/2026**

### 3.3 Exemplos de Requisição

**Dados atuais (sem parâmetro):**
```http
GET /quantitativointerrupcoesativas HTTP/1.1
Host: api.roraimaenergia.com.br
x-api-key: sua-api-key
```

**Dados históricos (com parâmetro):**
```http
GET /quantitativointerrupcoesativas?dthRecuperacao=10/12/2025%2014:30 HTTP/1.1
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
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "",
  "interrupcaoFornecimento": [
    {
      "ideConjuntoUnidadeConsumidora": 1,
      "ideMunicipio": 1400050,
      "qtdUCsAtendidas": 150000,
      "qtdOcorrenciaProgramada": 500,
      "qtdOcorrenciaNaoProgramada": 1200
    }
  ]
}
```

### 5.2 Campos do Response Principal

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `idcStatusRequisicao` | int | Sim | 1 = Sucesso, 2 = Erro |
| `emailIndisponibilidade` | string (50) | Sim | Email para notificação de indisponibilidade |
| `mensagem` | string | Sim/Não* | Mensagem de erro (vazio se sucesso) |
| `interrupcaoFornecimento` | array | Sim | Lista de interrupções por conjunto/município |

*Obrigatório apenas quando `idcStatusRequisicao` = 2

### 5.3 Campos do Array `interrupcaoFornecimento`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `ideConjuntoUnidadeConsumidora` | int | Sim | Código do Conjunto Elétrico |
| `ideMunicipio` | int | Sim | Código IBGE do município (7 dígitos) |
| `qtdUCsAtendidas` | int | Sim | Total de UCs atendidas pelo conjunto no município |
| `qtdOcorrenciaProgramada` | int | Sim | Qtd. de UCs com interrupção **programada** ativa |
| `qtdOcorrenciaNaoProgramada` | int | Sim | Qtd. de UCs com interrupção **não programada** ativa |

**Importante sobre os campos de quantidade:**
- `qtdOcorrenciaProgramada` e `qtdOcorrenciaNaoProgramada` representam **quantidade de UCs**, não número de eventos
- Todos os campos numéricos: inteiro > 0, limite máximo: 2.147.483.647

---

## 6. Regras de Negócio

### 6.1 Agrupamento dos Dados

Os dados devem ser agrupados por:
1. Município (código IBGE)
2. Conjunto Elétrico
3. Tipo de interrupção (programada/não programada)

### 6.2 UCs a Considerar

- **Incluir:** Todas as UCs com interrupção ativa (não restabelecida) no momento
- **Incluir:** UCs atendidas em caráter excepcional (Art. 117 da REN 1000/2021)
- **Excluir:** UCs com interrupção já restabelecida

### 6.3 Interrupções Programadas vs Não Programadas

| Tipo | Descrição | Exemplos |
|------|-----------|----------|
| **Programada** | Realizadas intencionalmente pela concessionária | Manutenção preventiva, obras, expansão |
| **Não Programada** | Não previstas | Falhas, acidentes, eventos climáticos |

---

## 7. Exemplos de Resposta

### 7.1 Sucesso com Dados

```json
{
  "idcStatusRequisicao": 1,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "",
  "interrupcaoFornecimento": [
    {
      "ideConjuntoUnidadeConsumidora": 1,
      "ideMunicipio": 1400050,
      "qtdUCsAtendidas": 150000,
      "qtdOcorrenciaProgramada": 500,
      "qtdOcorrenciaNaoProgramada": 1200
    },
    {
      "ideConjuntoUnidadeConsumidora": 1,
      "ideMunicipio": 1400175,
      "qtdUCsAtendidas": 12000,
      "qtdOcorrenciaProgramada": 0,
      "qtdOcorrenciaNaoProgramada": 350
    },
    {
      "ideConjuntoUnidadeConsumidora": 2,
      "ideMunicipio": 1400209,
      "qtdUCsAtendidas": 8500,
      "qtdOcorrenciaProgramada": 200,
      "qtdOcorrenciaNaoProgramada": 0
    }
  ]
}
```

### 7.2 Sucesso sem Dados (Sem Interrupções Ativas)

```json
{
  "idcStatusRequisicao": 1,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "",
  "interrupcaoFornecimento": []
}
```

### 7.3 Erro

```json
{
  "idcStatusRequisicao": 2,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "Erro ao calcular quantitativos - Unable to connect to database instance!",
  "interrupcaoFornecimento": []
}
```

---

## 8. Códigos IBGE - Municípios de Roraima

| Código IBGE | Município |
|-------------|-----------|
| 1400050 | Boa Vista |
| 1400100 | Alto Alegre |
| 1400027 | Amajari |
| 1400159 | Bonfim |
| 1400175 | Cantá |
| 1400209 | Caracaraí |
| 1400233 | Caroebe |
| 1400282 | Iracema |
| 1400308 | Mucajaí |
| 1400407 | Normandia |
| 1400456 | Pacaraima |
| 1400472 | Rorainópolis |
| 1400506 | São João da Baliza |
| 1400605 | São Luiz |
| 1400704 | Uiramutã |

---

## 9. Integração com Sistemas Internos

### 9.1 Sistema Técnico (INSERVICE + INDICADORES)

| Dado | Tabela/View | Campos |
|------|-------------|--------|
| Eventos/Ocorrências | `INSERVICE.AGENCY_EVENT` | num_1, is_open, NUM_CUST, dev_id, ad_ts, ag_id |
| Tipo Interrupção | `INSERVICE.SWITCH_PLAN_TASKS` | OUTAGE_NUM, PLAN_ID |
| Conjunto Elétrico | `INSERVICE.OMS_CONNECTIVITY` | mslink, conj, dist |
| UCs Atingidas | `INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW` | num_evento, num_instalacao |
| Código IBGE | `INDICADORES.IND_UNIVERSOS` | ID_DISPOSITIVO, CD_UNIVERSO, CD_TIPO_UNIVERSO |

### 9.2 Sistema Comercial (Ajuri)

**NÃO NECESSÁRIO para esta API**

Os dados necessários são obtidos diretamente do Sistema Técnico e da tabela INDICADORES.

### 9.3 Query Base

```sql
-- Query para obter eventos abertos com classificação e município
SELECT
    ae.num_1 AS id_evento,
    u.CD_UNIVERSO AS municipio_ibge,
    eq.CONJ AS conjunto,
    CASE
        WHEN sp.PLAN_ID IS NOT NULL THEN 'PROGRAMADA'
        ELSE 'NAO_PROGRAMADA'
    END AS tipo_interrupcao,
    ae.NUM_CUST AS clientes_afetados
FROM INSERVICE.AGENCY_EVENT ae
LEFT JOIN INSERVICE.SWITCH_PLAN_TASKS sp
    ON sp.OUTAGE_NUM = ae.num_1
LEFT JOIN INSERVICE.OMS_CONNECTIVITY eq
    ON eq.mslink = ae.dev_id AND eq.dist = 370
JOIN INDICADORES.IND_UNIVERSOS u
    ON u.ID_DISPOSITIVO = ae.dev_id AND u.CD_TIPO_UNIVERSO = 2
WHERE ae.ag_id = '370'
  AND ae.is_open = 'T';
```

### 9.4 Query de Agregação para API

```sql
SELECT
    eq.CONJ AS ideConjuntoUnidadeConsumidora,
    u.CD_UNIVERSO AS ideMunicipio,
    -- qtdUCsAtendidas virá de outra fonte (total de UCs no conjunto/município)
    SUM(CASE WHEN sp.PLAN_ID IS NOT NULL THEN NVL(ae.NUM_CUST, 0) ELSE 0 END) AS qtdOcorrenciaProgramada,
    SUM(CASE WHEN sp.PLAN_ID IS NULL THEN NVL(ae.NUM_CUST, 0) ELSE 0 END) AS qtdOcorrenciaNaoProgramada
FROM INSERVICE.AGENCY_EVENT ae
LEFT JOIN INSERVICE.SWITCH_PLAN_TASKS sp
    ON sp.OUTAGE_NUM = ae.num_1
LEFT JOIN INSERVICE.OMS_CONNECTIVITY eq
    ON eq.mslink = ae.dev_id AND eq.dist = 370
JOIN INDICADORES.IND_UNIVERSOS u
    ON u.ID_DISPOSITIVO = ae.dev_id AND u.CD_TIPO_UNIVERSO = 2
WHERE ae.ag_id = '370'
  AND ae.is_open = 'T'
GROUP BY eq.CONJ, u.CD_UNIVERSO;
```

### 9.5 Query para UCs Atingidas por Evento

```sql
-- Para obter detalhes das UCs atingidas em um evento específico
SELECT
    num_evento,
    num_instalacao,
    data_interrupcao,
    previsao_restabelecimento,
    num_dispositivo
FROM INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW
WHERE num_evento = :id_evento;
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

### 11.1 Fontes de Dados (Sistema Técnico)

- [x] Acesso à tabela `INSERVICE.AGENCY_EVENT`
- [x] Acesso à tabela `INSERVICE.SWITCH_PLAN_TASKS`
- [x] Acesso à tabela `INSERVICE.OMS_CONNECTIVITY`
- [x] Acesso à view `INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW`
- [x] Acesso à tabela `INDICADORES.IND_UNIVERSOS`
- [ ] Permissões SELECT concedidas ao usuário RADAR_API

### 11.2 Desenvolvimento API

- [ ] Endpoint `/quantitativointerrupcoesativas` respondendo em minúsculo
- [ ] Autenticação via `x-api-key` no header
- [ ] Whitelist de IP da ANEEL configurado
- [ ] Resposta em JSON com camelCase
- [ ] Campo `emailIndisponibilidade` configurado
- [ ] Agrupamento por conjunto + município implementado
- [ ] Query de agregação implementada (JOINs com tabelas do INSERVICE)
- [ ] Histórico de 7 dias para recuperação (dthRecuperacao) - até Abril/2026
- [ ] Testes de carga realizados (tempo resposta < 5 segundos)
- [ ] Swagger/OpenAPI documentado

---

*Documentação baseada no Ofício Circular 14/2025-SFE/ANEEL V4 (23/10/2025)*
