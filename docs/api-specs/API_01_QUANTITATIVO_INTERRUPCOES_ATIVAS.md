# API 1 - Quantitativo de Interrupções Ativas
## Projeto RADAR - Roraima Energia

**Versão:** 1.0
**Data:** 10/12/2025
**Prazo ANEEL:** Dezembro/2025
**Base Legal:** Ofício Circular nº 14/2025-SFE/ANEEL

---

## 1. Resumo Executivo

| Item | Descrição |
|------|-----------|
| **Endpoint** | `GET /quantitativointerrupcoesativas` |
| **Objetivo** | Fornecer à ANEEL dados em tempo real das interrupções ativas no sistema elétrico |
| **Frequência de Consulta** | A cada 5 minutos pela ANEEL |
| **Criticidade** | **ALTA** - Prazo Dez/2025 |
| **Autenticação** | Header `x-api-key` |

---

## 2. Especificação Técnica

### 2.1 Endpoint

```
GET https://{host}/quantitativointerrupcoesativas
```

### 2.2 Query Parameters

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `dthRecuperacao` | string | Não | Data/hora para recuperação de dados históricos (formato: `dd/mm/yyyy hh:mm`) |

### 2.3 Headers Obrigatórios

| Header | Tipo | Descrição |
|--------|------|-----------|
| `x-api-key` | string | Chave de autenticação fornecida pela distribuidora |

### 2.4 Response Schema (JSON)

```json
{
  "idcStatusRequisicao": 1,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "",
  "quantitativoInterrupcoesAtivas": [
    {
      "ideMunicipio": 1400050,
      "idcTipoInterrupcao": 1,
      "qtdInterrupcoes": 3,
      "qtdUcsInterrompidas": 1500,
      "qtdEquipesDeslocamento": 2,
      "dthUltRecuperacao": "10/12/2025 14:30"
    }
  ]
}
```

### 2.5 Campos do Response

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `idcStatusRequisicao` | int | Sim | 1=Sucesso, 2=Erro |
| `emailIndisponibilidade` | string | Sim | Email para contato em caso de problemas |
| `mensagem` | string | Sim | Mensagem de erro (vazio se sucesso) |
| `quantitativoInterrupcoesAtivas` | array | Sim | Lista de interrupções agregadas |
| `ideMunicipio` | int | Sim | Código IBGE do município (7 dígitos) |
| `idcTipoInterrupcao` | int | Sim | 1=Programada, 2=Não Programada |
| `qtdInterrupcoes` | int | Sim | Quantidade de interrupções |
| `qtdUcsInterrompidas` | int | Sim | Quantidade de UCs afetadas |
| `qtdEquipesDeslocamento` | int | Sim | Equipes em deslocamento/campo |
| `dthUltRecuperacao` | string | Sim | Data/hora da última atualização |

---

## 3. Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FLUXO API 1 - INTERRUPÇÕES ATIVAS                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐         ┌──────────┐         ┌──────────────────────────────────┐
│  ANEEL   │         │  RADAR   │         │        SISTEMA TÉCNICO           │
│          │         │   API    │         │ (INSERVICE + INDICADORES)        │
└────┬─────┘         └────┬─────┘         └────────────────┬─────────────────┘
     │                    │                                │
     │ GET /quantitativo  │                                │
     │ interrupcoesativas │                                │
     │───────────────────>│                                │
     │                    │                                │
     │                    │  Consulta dados de eventos     │
     │                    │  (AGENCY_EVENT + JOINs)        │
     │                    │───────────────────────────────>│
     │                    │                                │
     │                    │  - Eventos abertos (is_open=T) │
     │                    │  - Código IBGE (ind_universos) │
     │                    │  - Tipo (SWITCH_PLAN_TASKS)    │
     │                    │  - Conjunto (OMS_CONNECTIVITY) │
     │                    │  - UCs (consumidores_atingidos)│
     │                    │<───────────────────────────────│
     │                    │                                │
     │                    │ Agrega por                     │
     │                    │ município + conjunto + tipo    │
     │                    │                                │
     │  JSON Response     │                                │
     │<───────────────────│                                │
     │                    │                                │
```

**Nota:** Todos os dados necessários para a API 1 são obtidos diretamente das tabelas do Sistema Técnico (INSERVICE) e da tabela INDICADORES.IND_UNIVERSOS. Não há dependência do Sistema Comercial (Ajuri) para esta API.

---

## 4. Sistemas Fonte de Dados

### 4.1 SISTEMA TÉCNICO - INSERVICE (Obrigatório)

| Dado | Tabela/View | Campos Necessários |
|------|-------------|-------------------|
| Eventos/Ocorrências | `INSERVICE.AGENCY_EVENT` | num_1, is_open, NUM_CUST, dev_id, ad_ts, xdts, hxgn_ds_municipio |
| Tipo Interrupção | `INSERVICE.SWITCH_PLAN_TASKS` | OUTAGE_NUM, PLAN_ID (se existe = PROGRAMADA) |
| Conjunto Elétrico | `INSERVICE.OMS_CONNECTIVITY` | mslink, conj, dist |
| UCs Atingidas | `INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW` | num_evento, num_instalacao |
| Coordenadas | `INSERVICE.HXGN_INT_AJURI` | num_1, latitude, longitude |

**Equipe Responsável:** Sistema Técnico / COD

### 4.2 INDICADORES (Obrigatório)

| Dado | Tabela | Campos Necessários |
|------|--------|-------------------|
| Código IBGE Município | `INDICADORES.IND_UNIVERSOS` | ID_DISPOSITIVO, CD_UNIVERSO (código IBGE 7 dígitos), CD_TIPO_UNIVERSO |

**Filtro:** `CD_TIPO_UNIVERSO = 2` (para obter município)

**Equipe Responsável:** Sistema Técnico / Indicadores

### 4.3 SISTEMA COMERCIAL - AJURI

**Status:** NÃO NECESSÁRIO para API 1

A integração com o Ajuri **não é mais necessária** para a API 1, pois:
- O código IBGE do município é obtido de `INDICADORES.IND_UNIVERSOS`
- As UCs atingidas são obtidas de `INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW`

---

## 5. Mapeamento de Dados Detalhado

### 5.1 Campos da API → Dados das Tabelas

| Campo API | Tabela Origem | Campo/Cálculo |
|-----------|---------------|---------------|
| `ideMunicipio` | `INDICADORES.IND_UNIVERSOS` | `CD_UNIVERSO` (código IBGE 7 dígitos) |
| `idcTipoInterrupcao` | `INSERVICE.SWITCH_PLAN_TASKS` | Se `PLAN_ID IS NOT NULL` → 1 (PROGRAMADA), senão → 2 (NAO_PROGRAMADA) |
| `qtdInterrupcoes` | `INSERVICE.AGENCY_EVENT` | `COUNT(DISTINCT num_1)` agregado por município + tipo |
| `qtdUcsInterrompidas` | `INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW` | `COUNT(DISTINCT num_instalacao)` por evento |
| `qtdEquipesDeslocamento` | `INSERVICE.UN_HI` | COUNT de equipes com status em deslocamento/campo |
| `dthUltRecuperacao` | Sistema | `SYSDATE` no formato dd/mm/yyyy hh:mm |

### 5.2 Relacionamentos (JOINs)

```
INSERVICE.AGENCY_EVENT (a)
    │
    ├── LEFT JOIN INSERVICE.SWITCH_PLAN_TASKS (sp)
    │       ON sp.OUTAGE_NUM = a.NUM_1
    │       → Identificar se é PROGRAMADA (PLAN_ID IS NOT NULL)
    │
    ├── LEFT JOIN INSERVICE.OMS_CONNECTIVITY (eq)
    │       ON eq.MSLINK = a.DEV_ID AND eq.DIST = 370
    │       → Obter conjunto elétrico (CONJ)
    │
    ├── JOIN INDICADORES.IND_UNIVERSOS (u)
    │       ON u.ID_DISPOSITIVO = a.DEV_ID AND u.CD_TIPO_UNIVERSO = 2
    │       → Obter código IBGE do município (CD_UNIVERSO)
    │
    └── LEFT JOIN INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW (ca)
            ON ca.NUM_EVENTO = a.NUM_1
            → Obter UCs atingidas por evento
```

### 5.3 Query Base para Eventos Ativos

```sql
-- Query para obter eventos abertos com tipo de interrupção
SELECT
    ae.num_1 AS id_evento,
    ae.is_open,
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

### 5.4 Query para UCs Atingidas por Evento

```sql
-- Query para obter UCs atingidas em um evento específico
SELECT
    num_evento,
    num_instalacao,
    data_interrupcao,
    previsao_restabelecimento,
    num_dispositivo
FROM INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW
WHERE num_evento = :id_evento;
```

### 5.5 Query de Agregação Final (Lógica no RADAR)

```sql
-- Query conceitual que o RADAR executará para a API
SELECT
    u.CD_UNIVERSO AS ideMunicipio,
    eq.CONJ AS ideConjuntoUnidadeConsumidora,
    CASE
        WHEN sp.PLAN_ID IS NOT NULL THEN 1  -- PROGRAMADA
        ELSE 2  -- NAO_PROGRAMADA
    END AS idcTipoInterrupcao,
    COUNT(DISTINCT ae.num_1) AS qtdInterrupcoes,
    SUM(NVL(ae.NUM_CUST, 0)) AS qtdUcsInterrompidas,
    TO_CHAR(SYSDATE, 'DD/MM/YYYY HH24:MI') AS dthUltRecuperacao
FROM INSERVICE.AGENCY_EVENT ae
LEFT JOIN INSERVICE.SWITCH_PLAN_TASKS sp
    ON sp.OUTAGE_NUM = ae.num_1
LEFT JOIN INSERVICE.OMS_CONNECTIVITY eq
    ON eq.mslink = ae.dev_id AND eq.dist = 370
JOIN INDICADORES.IND_UNIVERSOS u
    ON u.ID_DISPOSITIVO = ae.dev_id AND u.CD_TIPO_UNIVERSO = 2
WHERE ae.ag_id = '370'
  AND ae.is_open = 'T'
GROUP BY
    u.CD_UNIVERSO,
    eq.CONJ,
    CASE WHEN sp.PLAN_ID IS NOT NULL THEN 1 ELSE 2 END
ORDER BY
    u.CD_UNIVERSO,
    eq.CONJ;
```

---

## 6. Requisitos por Equipe

### 6.1 EQUIPE SISTEMA TÉCNICO

**Prioridade: CRÍTICA**
**Prazo: Dezembro/2025**

#### Tabelas/Views Utilizadas (já existentes):

| Tabela/View | Schema | Campos Utilizados |
|-------------|--------|-------------------|
| `AGENCY_EVENT` | INSERVICE | num_1, is_open, NUM_CUST, dev_id, ad_ts, xdts, ag_id |
| `SWITCH_PLAN_TASKS` | INSERVICE | OUTAGE_NUM, PLAN_ID |
| `OMS_CONNECTIVITY` | INSERVICE | mslink, conj, dist |
| `CONSUMIDORES_ATINGIDOS_VIEW` | INSERVICE | num_evento, num_instalacao |
| `HXGN_INT_AJURI` | INSERVICE | num_1, latitude, longitude |
| `UN_HI` | INSERVICE | num_1, unid, cpers, unit_status, cdts |
| `IND_UNIVERSOS` | INDICADORES | ID_DISPOSITIVO, CD_UNIVERSO, CD_TIPO_UNIVERSO |

#### Mapeamentos Confirmados:

| Dado | Como Obter |
|------|------------|
| **Tipo Interrupção** | JOIN com `SWITCH_PLAN_TASKS`: se `PLAN_ID IS NOT NULL` → PROGRAMADA |
| **Código IBGE** | JOIN com `IND_UNIVERSOS` onde `CD_TIPO_UNIVERSO = 2`: campo `CD_UNIVERSO` |
| **Conjunto Elétrico** | JOIN com `OMS_CONNECTIVITY`: campo `CONJ` |
| **UCs Atingidas** | View `CONSUMIDORES_ATINGIDOS_VIEW` ou campo `NUM_CUST` da `AGENCY_EVENT` |
| **Eventos Abertos** | Filtro `is_open = 'T'` e `ag_id = '370'` |

#### Permissões Necessárias:

```sql
-- Usuário da API RADAR precisa de SELECT nas tabelas
GRANT SELECT ON INSERVICE.AGENCY_EVENT TO RADAR_API;
GRANT SELECT ON INSERVICE.SWITCH_PLAN_TASKS TO RADAR_API;
GRANT SELECT ON INSERVICE.OMS_CONNECTIVITY TO RADAR_API;
GRANT SELECT ON INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW TO RADAR_API;
GRANT SELECT ON INSERVICE.UN_HI TO RADAR_API;
GRANT SELECT ON INDICADORES.IND_UNIVERSOS TO RADAR_API;
```

---

### 6.2 EQUIPE SISTEMA COMERCIAL (AJURI)

**Status: NÃO NECESSÁRIO para API 1**

A API 1 não depende mais do Sistema Comercial (Ajuri), pois:
- O código IBGE do município é obtido de `INDICADORES.IND_UNIVERSOS`
- As UCs atingidas são obtidas de `INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW`

---

### 6.3 EQUIPE CRM/ATENDIMENTO

**Prioridade: BAIXA para API 1**

Para esta API específica, não há dependência direta do CRM.

---

## 7. Códigos de Referência

### 7.1 Códigos IBGE - Municípios de Roraima

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

### 7.2 Tipos de Interrupção

| Código | Descrição | Origem Típica |
|--------|-----------|---------------|
| 1 | Programada | Manutenção preventiva, obras, expansão |
| 2 | Não Programada | Falhas, acidentes, eventos climáticos |

---

## 8. Exemplo de Response

### 8.1 Cenário: 3 interrupções ativas em Boa Vista

```json
{
  "idcStatusRequisicao": 1,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "",
  "quantitativoInterrupcoesAtivas": [
    {
      "ideMunicipio": 1400050,
      "idcTipoInterrupcao": 2,
      "qtdInterrupcoes": 2,
      "qtdUcsInterrompidas": 3500,
      "qtdEquipesDeslocamento": 4,
      "dthUltRecuperacao": "10/12/2025 14:35"
    },
    {
      "ideMunicipio": 1400050,
      "idcTipoInterrupcao": 1,
      "qtdInterrupcoes": 1,
      "qtdUcsInterrompidas": 200,
      "qtdEquipesDeslocamento": 1,
      "dthUltRecuperacao": "10/12/2025 14:30"
    },
    {
      "ideMunicipio": 1400175,
      "idcTipoInterrupcao": 2,
      "qtdInterrupcoes": 1,
      "qtdUcsInterrompidas": 450,
      "qtdEquipesDeslocamento": 1,
      "dthUltRecuperacao": "10/12/2025 14:32"
    }
  ]
}
```

### 8.2 Cenário: Sem interrupções ativas

```json
{
  "idcStatusRequisicao": 1,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "",
  "quantitativoInterrupcoesAtivas": []
}
```

### 8.3 Cenário: Erro no sistema

```json
{
  "idcStatusRequisicao": 2,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "Erro de conexão com banco de dados do Sistema Técnico",
  "quantitativoInterrupcoesAtivas": []
}
```

---

## 9. Requisitos Não-Funcionais

| Requisito | Valor | Justificativa |
|-----------|-------|---------------|
| Tempo de resposta | < 5 segundos | Exigência ANEEL |
| Disponibilidade | 99,5% | 24x7 |
| Taxa de atualização | 5 minutos | Tempo real para ANEEL |
| Retenção histórico | 36 meses | Para parâmetro dthRecuperacao |

---

## 10. Checklist de Implementação

### 10.1 Sistema Técnico (Pré-requisitos)

- [x] Tabela `AGENCY_EVENT` disponível para consulta
- [x] Tabela `SWITCH_PLAN_TASKS` disponível (classificação PROGRAMADA/NAO_PROGRAMADA)
- [x] Tabela `OMS_CONNECTIVITY` disponível (conjunto elétrico)
- [x] View `CONSUMIDORES_ATINGIDOS_VIEW` disponível (UCs atingidas)
- [x] Tabela `IND_UNIVERSOS` disponível (código IBGE)
- [ ] Usuário RADAR_API criado
- [ ] Permissões SELECT concedidas ao RADAR_API
- [ ] Teste de conectividade realizado

### 10.2 RADAR (Desenvolvimento)

- [ ] Conexão com banco INSERVICE configurada
- [ ] Conexão com banco INDICADORES configurada
- [ ] Query de agregação implementada
- [ ] Endpoint `/quantitativointerrupcoesativas` implementado
- [ ] Autenticação via `x-api-key` implementada
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Documentação OpenAPI/Swagger

### 10.3 Homologação

- [ ] Testes com dados reais de eventos abertos
- [ ] Validação dos códigos IBGE com equipe técnica
- [ ] Validação da classificação PROGRAMADA/NAO_PROGRAMADA
- [ ] Teste de carga (tempo de resposta < 5 segundos)
- [ ] API Key gerada para ANEEL
- [ ] Whitelist de IP da ANEEL configurado
- [ ] Endpoint publicado em produção

---

## 11. Contatos do Projeto RADAR

| Função | Nome | Email | Telefone |
|--------|------|-------|----------|
| Coordenador | | | |
| Desenvolvedor | | | |
| DBA | | | |

---

**Dúvidas?** Entrar em contato com a equipe TI do Projeto RADAR.

---

*Documento gerado em 10/12/2025 - Projeto RADAR - Roraima Energia S/A*
