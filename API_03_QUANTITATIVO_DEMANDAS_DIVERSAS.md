# API 3 - Quantitativo de Demandas Diversas
## Projeto RADAR - Roraima Energia

**Versão:** 1.0
**Data:** 10/12/2025
**Prazo ANEEL:** Maio/2026
**Base Legal:** Ofício Circular nº 14/2025-SFE/ANEEL

---

## 1. Resumo Executivo

| Item | Descrição |
|------|-----------|
| **Endpoint** | `GET /quantitativodemandasdiversas` |
| **Objetivo** | Fornecer à ANEEL quantitativo agregado de demandas por canal, tipologia, status e nível de atendimento |
| **Frequência de Consulta** | Periódica pela ANEEL |
| **Criticidade** | **ALTA** - Prazo Maio/2026 |
| **Autenticação** | Header `x-api-key` |

---

## 2. Especificação Técnica

### 2.1 Endpoint

```
GET https://{host}/quantitativodemandasdiversas
```

### 2.2 Query Parameters

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `dthRecuperacao` | string | Não | Data/hora para recuperação histórica (formato: `dd/mm/yyyy hh:mm`) |

**Comportamento:**
- Se `dthRecuperacao` não informado: retorna dados atuais (snapshot)
- Se `dthRecuperacao` informado: retorna dados até aquela data/hora

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
  "quantitativoDemandasDiversas": [
    {
      "idcNivelAtendimento": 0,
      "idcCanalAtendimento": 2,
      "idcTipologia": "0101001",
      "qtdAndamento": 15,
      "qtdRegistrada": 5,
      "qtdImprocedente": 3,
      "qtdProcedente": 120,
      "qtdSemProcedencia": 8
    }
  ]
}
```

### 2.5 Campos do Response

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `idcStatusRequisicao` | int | Sim | 1=Sucesso, 2=Erro |
| `emailIndisponibilidade` | string | Sim | Email para contato |
| `mensagem` | string | Sim | Mensagem de erro (vazio se sucesso) |
| `quantitativoDemandasDiversas` | array | Sim | Lista de agregações |
| `idcNivelAtendimento` | int | Sim | Nível de atendimento (ver tabela) |
| `idcCanalAtendimento` | int | Sim | Canal de atendimento (ver tabela) |
| `idcTipologia` | string | Sim | Código tipologia ANEEL (7 dígitos) |
| `qtdAndamento` | int | Sim | Quantidade em andamento |
| `qtdRegistrada` | int | Sim | Quantidade apenas registrada |
| `qtdImprocedente` | int | Sim | Quantidade encerrada improcedente |
| `qtdProcedente` | int | Sim | Quantidade encerrada procedente |
| `qtdSemProcedencia` | int | Sim | Quantidade sem procedência definida |

---

## 3. Códigos e Enumerações

### 3.1 Nível de Atendimento (`idcNivelAtendimento`)

| Código | Descrição | Setor Típico |
|--------|-----------|--------------|
| 0 | 1º Nível | Call Center, Atendimento inicial |
| 1 | 2º Nível | Retaguarda, Análise técnica |
| 2 | 3º Nível | Especializado, Ouvidoria |

### 3.2 Canal de Atendimento (`idcCanalAtendimento`)

| Código | Descrição | Sistema Origem |
|--------|-----------|----------------|
| 1 | Presencial | Agências de atendimento |
| 2 | Telefone | Call Center / 0800 |
| 3 | Internet | Site / Portal do Cliente |
| 4 | Aplicativo | App Mobile |

### 3.3 Tipologias ANEEL (Principais)

| Código | Descrição | Categoria |
|--------|-----------|-----------|
| **01xxxxx** | **Reclamações** | |
| 0101001 | Falta de energia | Qualidade técnica |
| 0101002 | Qualidade de energia | Qualidade técnica |
| 0101003 | Oscilação de tensão | Qualidade técnica |
| 0101004 | Interrupção frequente | Qualidade técnica |
| **02xxxxx** | **Solicitações** | |
| 0102001 | Ligação nova | Serviços |
| 0102002 | Religação | Serviços |
| 0102003 | Desligamento | Serviços |
| 0102004 | Alteração cadastral | Serviços |
| 0102005 | Segunda via fatura | Serviços |
| **03xxxxx** | **Informações** | |
| 0103001 | Informação sobre fatura | Informações |
| 0103002 | Informação sobre consumo | Informações |
| **04xxxxx** | **Cobrança** | |
| 0201001 | Cobrança indevida | Comercial |
| 0202001 | Contestação de débito | Comercial |

**Referência completa:** Tabela de tipologias ANEEL disponível no site regulador.

---

## 4. Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   FLUXO API 3 - QUANTITATIVO DEMANDAS DIVERSAS               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐         ┌──────────┐         ┌──────────┐
│  ANEEL   │         │  RADAR   │         │   CRM    │
│          │         │   API    │         │ (SGC/?)  │
└────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │
     │ GET /quantitativo  │                    │
     │ demandasdiversas   │                    │
     │───────────────────>│                    │
     │                    │                    │
     │                    │ SELECT agregado    │
     │                    │ FROM VW_DEMANDAS_  │
     │                    │ AGREGADAS_RADAR    │
     │                    │───────────────────>│
     │                    │                    │
     │                    │  Dados agregados   │
     │                    │<───────────────────│
     │                    │                    │
     │  JSON Response     │                    │
     │<───────────────────│                    │
     │                    │                    │
```

---

## 5. Sistemas Fonte de Dados

### 5.1 SISTEMA DE CRM/ATENDIMENTO (Obrigatório)

**Este é o ÚNICO sistema fonte para esta API.**

| Dado | View/Tabela | Campos Necessários |
|------|-------------|-------------------|
| Demandas agregadas | VW_DEMANDAS_AGREGADAS_RADAR | Todos os campos da API |

**Equipes Responsáveis:**
- CRM / Gestão de Atendimento
- Call Center
- Ouvidoria
- Canais Digitais

---

## 6. Especificação das Views do CRM

### 6.1 VW_DEMANDAS_AGREGADAS_RADAR (CRÍTICA)

**Objetivo:** Fornecer quantitativo de demandas agregadas por nível, canal, tipologia e status.

**Opção A - View com agregação (recomendado):**

```sql
CREATE OR REPLACE VIEW CRM.VW_DEMANDAS_AGREGADAS_RADAR AS
SELECT
    -- ============================================
    -- DIMENSÕES DE AGREGAÇÃO
    -- ============================================
    nivel_tratamento AS nivel_atendimento,   -- NUMBER(1) NOT NULL - 0=1º, 1=2º, 2=3º
    canal_atendimento,                        -- NUMBER(1) NOT NULL - 1,2,3,4
    tipologia,                                -- VARCHAR2(7) NOT NULL - Código ANEEL

    -- ============================================
    -- MÉTRICAS AGREGADAS
    -- ============================================
    SUM(CASE WHEN status_demanda = 0 THEN 1 ELSE 0 END) AS qtd_andamento,
    SUM(CASE WHEN status_demanda = 1 THEN 1 ELSE 0 END) AS qtd_registrada,
    SUM(CASE WHEN status_demanda = 2 AND procedencia = 0 THEN 1 ELSE 0 END) AS qtd_improcedente,
    SUM(CASE WHEN status_demanda = 2 AND procedencia = 1 THEN 1 ELSE 0 END) AS qtd_procedente,
    SUM(CASE WHEN procedencia = 2 OR procedencia IS NULL THEN 1 ELSE 0 END) AS qtd_sem_procedencia

FROM ... -- tabelas de demandas do CRM
GROUP BY
    nivel_tratamento,
    canal_atendimento,
    tipologia;
```

**Opção B - View detalhada (RADAR faz agregação):**

```sql
CREATE OR REPLACE VIEW CRM.VW_DEMANDAS_DETALHE_RADAR AS
SELECT
    num_protocolo,
    nivel_tratamento,           -- NUMBER(1) - 0, 1, 2
    canal_atendimento,          -- NUMBER(1) - 1, 2, 3, 4
    tipologia,                  -- VARCHAR2(7)
    status_demanda,             -- NUMBER(1) - 0, 1, 2
    procedencia,                -- NUMBER(1) - 0, 1, 2
    data_hora_abertura,         -- TIMESTAMP
    data_hora_encerramento      -- TIMESTAMP
FROM ... -- tabelas de demandas do CRM;
```

### 6.2 VW_DEMANDAS_AGREGADAS_HISTORICO_RADAR (Para dthRecuperacao)

Para suportar o parâmetro `dthRecuperacao`, é necessário ter histórico:

```sql
CREATE OR REPLACE VIEW CRM.VW_DEMANDAS_AGREGADAS_HISTORICO_RADAR AS
SELECT
    nivel_tratamento AS nivel_atendimento,
    canal_atendimento,
    tipologia,
    data_hora_abertura,
    data_hora_encerramento,
    status_demanda,
    procedencia
FROM ... -- tabelas de demandas do CRM
WHERE data_hora_abertura >= ADD_MONTHS(SYSDATE, -60);  -- 5 anos de histórico
```

**Query do RADAR para dthRecuperacao:**

```sql
-- Se dthRecuperacao = '10/12/2025 14:30'
SELECT
    nivel_atendimento,
    canal_atendimento,
    tipologia,
    SUM(CASE WHEN status_demanda = 0 THEN 1 ELSE 0 END) AS qtd_andamento,
    SUM(CASE WHEN status_demanda = 1 THEN 1 ELSE 0 END) AS qtd_registrada,
    SUM(CASE WHEN status_demanda = 2 AND procedencia = 0 THEN 1 ELSE 0 END) AS qtd_improcedente,
    SUM(CASE WHEN status_demanda = 2 AND procedencia = 1 THEN 1 ELSE 0 END) AS qtd_procedente,
    SUM(CASE WHEN procedencia = 2 OR procedencia IS NULL THEN 1 ELSE 0 END) AS qtd_sem_procedencia
FROM VW_DEMANDAS_AGREGADAS_HISTORICO_RADAR@CRM_LINK
WHERE data_hora_abertura <= TO_TIMESTAMP('10/12/2025 14:30', 'DD/MM/YYYY HH24:MI')
GROUP BY nivel_atendimento, canal_atendimento, tipologia;
```

---

## 7. Requisitos por Equipe

### 7.1 EQUIPE CRM / GESTÃO DE ATENDIMENTO

**Prioridade: CRÍTICA**
**Prazo: Abril/2026**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - CRM/GESTÃO - API 3                                 │
└─────────────────────────────────────────────────────────────────────────────┘

1. SISTEMA DE CRM

   1.1. Qual sistema de CRM é utilizado?
        [ ] SGC (Sistema de Gestão Comercial)
        [ ] Sistema próprio (nome: _______________)
        [ ] Outro: _______________

   1.2. Todos os canais registram demandas no mesmo sistema?
        [ ] Sim - Todos no mesmo CRM
        [ ] Não - Quais sistemas separados?
            Call Center: _______________
            Agências: _______________
            Digital: _______________
            Ouvidoria: _______________

2. MAPEAMENTO DE DADOS

   2.1. Nível de atendimento - como é identificado?
        [ ] Campo específico (qual? _______________)
        [ ] Baseado no setor/fila
        [ ] Baseado na tipologia
        [ ] Outro: _______________

        Mapeamento atual:
        | Valor no Sistema | Nível ANEEL |
        |------------------|-------------|
        | | 0 (1º nível) |
        | | 1 (2º nível) |
        | | 2 (3º nível) |

   2.2. Canal de atendimento - como é identificado?
        Campo: _______________

        Mapeamento atual:
        | Valor no Sistema | Canal ANEEL |
        |------------------|-------------|
        | | 1 (Presencial) |
        | | 2 (Telefone) |
        | | 3 (Internet) |
        | | 4 (App) |

   2.3. Tipologia - usa padrão ANEEL (7 dígitos)?
        [ ] Sim - diretamente
        [ ] Não - precisa DE-PARA

        Se não, quantas tipologias existem? _______________
        Tabela DE-PARA pode ser criada? [ ] Sim [ ] Não

   2.4. Status da demanda:
        | Valor no Sistema | Status ANEEL |
        |------------------|--------------|
        | | 0 (Andamento) |
        | | 1 (Registrada) |
        | | 2 (Encerrada) |

   2.5. Procedência - existe esse campo?
        [ ] Sim - Campo: _______________
        [ ] Não - Como derivar?

        Mapeamento:
        | Valor no Sistema | Procedência ANEEL |
        |------------------|-------------------|
        | | 0 (Improcedente) |
        | | 1 (Procedente) |
        | | 2 (Sem procedência) |

3. HISTÓRICO

   3.1. Existe histórico de demandas para recuperação?
        [ ] Sim - Período: _______________
        [ ] Não

   3.2. É possível reconstruir o estado em uma data/hora específica?
        [ ] Sim
        [ ] Não - apenas dados atuais

4. VOLUME DE DADOS

   4.1. Quantidade média de demandas por mês: _______________
   4.2. Quantidade de tipologias distintas: _______________
   4.3. Distribuição aproximada por canal:
        - Presencial: _____%
        - Telefone: _____%
        - Internet: _____%
        - App: _____%

5. PERFORMANCE

   5.1. A consulta agregada pode ser executada em tempo real?
        [ ] Sim
        [ ] Não - precisa de tabela pré-agregada

   5.2. Existe índice nas colunas de agregação?
        [ ] Sim
        [ ] Não

6. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Gestor CRM | | | |
   | Analista de Dados | | | |
   | DBA | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 7.2 EQUIPE CALL CENTER

**Prioridade: ALTA**
**Prazo: Abril/2026**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - CALL CENTER - API 3                                │
└─────────────────────────────────────────────────────────────────────────────┘

1. SISTEMA DO CALL CENTER

   1.1. As demandas do Call Center estão no CRM central?
        [ ] Sim
        [ ] Não - sistema separado: _______________

   1.2. Se separado, como integrar os dados?
        [ ] Database Link
        [ ] API
        [ ] Arquivo/ETL
        [ ] Outro: _______________

2. CLASSIFICAÇÃO

   2.1. O Call Center registra em qual nível?
        [ ] Sempre 1º nível
        [ ] Depende do caso - como identificar? _______________

   2.2. Canal é sempre "Telefone" (código 2)?
        [ ] Sim
        [ ] Não - existe outro canal? _______________

3. TIPOLOGIAS

   3.1. Usa as mesmas tipologias do CRM central?
        [ ] Sim
        [ ] Não - precisa mapeamento

4. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Supervisor | | | |
   | TI Call Center | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 7.3 EQUIPE OUVIDORIA

**Prioridade: ALTA**
**Prazo: Abril/2026**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - OUVIDORIA - API 3                                  │
└─────────────────────────────────────────────────────────────────────────────┘

1. SISTEMA DA OUVIDORIA

   1.1. A ouvidoria usa o mesmo CRM?
        [ ] Sim
        [ ] Não - sistema: _______________

   1.2. As demandas de ouvidoria são 3º nível?
        [ ] Sim - sempre
        [ ] Não - depende: _______________

2. TIPOLOGIAS DA OUVIDORIA

   2.1. Usa tipologias específicas?
        [ ] Sim - quais? _______________
        [ ] Não - mesmas do CRM

3. VOLUME

   3.1. Quantidade média de demandas/mês na ouvidoria: _______________

4. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Ouvidor | | | |
   | Analista | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 7.4 EQUIPE CANAIS DIGITAIS (Portal/App)

**Prioridade: MÉDIA**
**Prazo: Abril/2026**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - CANAIS DIGITAIS - API 3                            │
└─────────────────────────────────────────────────────────────────────────────┘

1. CANAIS DISPONÍVEIS

   1.1. Marque os canais digitais existentes:
        [ ] Portal do Cliente (Internet)
        [ ] App Mobile
        [ ] WhatsApp Bot
        [ ] Chatbot site
        [ ] Outro: _______________

   1.2. Todos registram demandas no CRM central?
        [ ] Sim
        [ ] Não - quais não? _______________

2. CLASSIFICAÇÃO

   2.1. Como diferenciar Internet (3) de App (4)?
        Campo: _______________
        Valores: _______________

   2.2. Nível de atendimento:
        [ ] Sempre 1º nível
        [ ] Depende: _______________

3. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Gestor Digital | | | |
   | Desenvolvedor | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 7.5 EQUIPE AGÊNCIAS (Atendimento Presencial)

**Prioridade: MÉDIA**
**Prazo: Abril/2026**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - AGÊNCIAS - API 3                                   │
└─────────────────────────────────────────────────────────────────────────────┘

1. SISTEMA DAS AGÊNCIAS

   1.1. Usam o mesmo CRM do Call Center?
        [ ] Sim
        [ ] Não - sistema: _______________

2. CLASSIFICAÇÃO

   2.1. Canal é sempre "Presencial" (código 1)?
        [ ] Sim
        [ ] Não - existem exceções? _______________

   2.2. Nível de atendimento:
        [ ] Sempre 1º nível
        [ ] Pode ser 2º nível
        [ ] Outro: _______________

3. VOLUME

   3.1. Quantidade média de atendimentos presenciais/mês: _______________
   3.2. % que gera demanda registrada: _____%

4. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Coordenador Agências | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Mapeamento de Dados Consolidado

### 8.1 Tabela DE-PARA - Nível de Atendimento

| Sistema Origem | Setor/Fila | Nível ANEEL |
|----------------|------------|-------------|
| Call Center | Atendimento inicial | 0 |
| Agências | Atendimento balcão | 0 |
| Portal/App | Auto-atendimento | 0 |
| CRM | Retaguarda | 1 |
| CRM | Análise técnica | 1 |
| Ouvidoria | Ouvidoria | 2 |
| CRM | Especializado | 2 |

### 8.2 Tabela DE-PARA - Canal de Atendimento

| Sistema Origem | Identificação | Canal ANEEL |
|----------------|---------------|-------------|
| Agências | ORIGEM='AGENCIA' | 1 |
| Call Center | ORIGEM='CALLCENTER' | 2 |
| Portal | ORIGEM='WEB' | 3 |
| App | ORIGEM='APP' | 4 |

---

## 9. Exemplo de Response

### 9.1 Cenário: Dados agregados normais

```json
{
  "idcStatusRequisicao": 1,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "",
  "quantitativoDemandasDiversas": [
    {
      "idcNivelAtendimento": 0,
      "idcCanalAtendimento": 2,
      "idcTipologia": "0101001",
      "qtdAndamento": 15,
      "qtdRegistrada": 5,
      "qtdImprocedente": 3,
      "qtdProcedente": 120,
      "qtdSemProcedencia": 8
    },
    {
      "idcNivelAtendimento": 0,
      "idcCanalAtendimento": 3,
      "idcTipologia": "0101001",
      "qtdAndamento": 8,
      "qtdRegistrada": 2,
      "qtdImprocedente": 1,
      "qtdProcedente": 45,
      "qtdSemProcedencia": 3
    },
    {
      "idcNivelAtendimento": 1,
      "idcCanalAtendimento": 2,
      "idcTipologia": "0102001",
      "qtdAndamento": 25,
      "qtdRegistrada": 10,
      "qtdImprocedente": 5,
      "qtdProcedente": 200,
      "qtdSemProcedencia": 15
    },
    {
      "idcNivelAtendimento": 2,
      "idcCanalAtendimento": 1,
      "idcTipologia": "0201001",
      "qtdAndamento": 3,
      "qtdRegistrada": 0,
      "qtdImprocedente": 2,
      "qtdProcedente": 18,
      "qtdSemProcedencia": 1
    }
  ]
}
```

### 9.2 Cenário: Sem demandas

```json
{
  "idcStatusRequisicao": 1,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "",
  "quantitativoDemandasDiversas": []
}
```

### 9.3 Cenário: Erro no sistema

```json
{
  "idcStatusRequisicao": 2,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "Erro ao agregar dados do CRM",
  "quantitativoDemandasDiversas": []
}
```

---

## 10. Requisitos Não-Funcionais

| Requisito | Valor | Justificativa |
|-----------|-------|---------------|
| Tempo de resposta | < 10 segundos | Agregação pode ser pesada |
| Disponibilidade | 99,5% | 24x7 |
| Retenção histórico | 60 meses | Para parâmetro dthRecuperacao |

---

## 11. Usuário para Integração - CRM

```sql
-- Criar usuário (executar como DBA no banco do CRM)
CREATE USER RADAR_READONLY IDENTIFIED BY "[SENHA_A_DEFINIR]"
    DEFAULT TABLESPACE USERS;

-- Permissões mínimas
GRANT CREATE SESSION TO RADAR_READONLY;

-- Permissões de SELECT nas views
GRANT SELECT ON CRM.VW_DEMANDAS_AGREGADAS_RADAR TO RADAR_READONLY;
GRANT SELECT ON CRM.VW_DEMANDAS_AGREGADAS_HISTORICO_RADAR TO RADAR_READONLY;
```

---

## 12. Checklist de Implementação

### 12.1 CRM / Atendimento

- [ ] Identificar todas as fontes de demandas
- [ ] Mapear níveis de atendimento
- [ ] Mapear canais de atendimento
- [ ] Mapear/criar tabela DE-PARA tipologias
- [ ] Mapear status e procedência
- [ ] View VW_DEMANDAS_AGREGADAS_RADAR criada
- [ ] View VW_DEMANDAS_AGREGADAS_HISTORICO_RADAR criada
- [ ] Usuário RADAR_READONLY criado
- [ ] Índices para performance criados
- [ ] Dados de conexão enviados

### 12.2 RADAR

- [ ] Database Link configurado (CRM)
- [ ] Synonyms criados
- [ ] Materialized View para cache (opcional)
- [ ] Endpoint implementado
- [ ] Suporte a dthRecuperacao implementado
- [ ] Testes unitários
- [ ] Testes de integração

### 12.3 Homologação

- [ ] Validação dos totais com equipe CRM
- [ ] Teste com diferentes combinações nível/canal/tipologia
- [ ] Teste de dthRecuperacao
- [ ] Teste de performance
- [ ] API Key gerada para ANEEL

---

## 13. Contatos do Projeto RADAR

| Função | Nome | Email | Telefone |
|--------|------|-------|----------|
| Coordenador | | | |
| Desenvolvedor | | | |
| DBA | | | |

---

**Dúvidas?** Entrar em contato com a equipe TI do Projeto RADAR.

---

*Documento gerado em 10/12/2025 - Projeto RADAR - Roraima Energia S/A*
