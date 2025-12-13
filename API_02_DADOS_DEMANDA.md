# API 2 - Dados de Demanda
## Projeto RADAR - Roraima Energia

**Versão:** 1.0
**Data:** 10/12/2025
**Prazo ANEEL:** Abril/2026
**Base Legal:** Ofício Circular nº 14/2025-SFE/ANEEL

---

## 1. Resumo Executivo

| Item | Descrição |
|------|-----------|
| **Endpoint** | `GET /dadosdemanda` |
| **Objetivo** | Fornecer à ANEEL dados detalhados de uma demanda específica a partir do número do protocolo |
| **Frequência de Consulta** | Sob demanda (quando ANEEL consulta um protocolo específico) |
| **Criticidade** | **ALTA** - Prazo Abril/2026 |
| **Autenticação** | Header `x-api-key` |

---

## 2. Especificação Técnica

### 2.1 Endpoint

```
GET https://{host}/dadosdemanda?numProtocolo={numero}
```

### 2.2 Query Parameters

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `numProtocolo` | string | **Sim** | Número do protocolo da demanda |

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
  "numProtocolo": "2025123456789",
  "numUC": "1234567",
  "numCpfCnpj": "***.***.123-**",
  "nomTitular": "JOSE DA SILVA",
  "idcCanalAtendimento": 2,
  "idcTipologia": "0101001",
  "idcStatus": 0,
  "idcProcedencia": 2,
  "dthAbertura": "10/12/2025 08:30",
  "dthEncerramento": null,
  "ideMunicipio": 1400050,
  "idcNivelTratamento": 0
}
```

### 2.5 Campos do Response

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `idcStatusRequisicao` | int | Sim | 1=Sucesso, 2=Erro |
| `emailIndisponibilidade` | string | Sim | Email para contato |
| `mensagem` | string | Sim | Mensagem de erro (vazio se sucesso) |
| `numProtocolo` | string | Sim | Número do protocolo |
| `numUC` | string | Sim | Número da Unidade Consumidora |
| `numCpfCnpj` | string | Sim | CPF/CNPJ mascarado (LGPD) |
| `nomTitular` | string | Sim | Nome do titular |
| `idcCanalAtendimento` | int | Sim | Canal de atendimento (ver tabela) |
| `idcTipologia` | string | Sim | Código da tipologia (7 dígitos) |
| `idcStatus` | int | Sim | Status da demanda (ver tabela) |
| `idcProcedencia` | int | Sim | Procedência (ver tabela) |
| `dthAbertura` | string | Sim | Data/hora abertura (dd/mm/yyyy hh:mm) |
| `dthEncerramento` | string | Não | Data/hora encerramento |
| `ideMunicipio` | int | Sim | Código IBGE do município |
| `idcNivelTratamento` | int | Sim | Nível de tratamento (ver tabela) |

---

## 3. Códigos e Enumerações

### 3.1 Canal de Atendimento (`idcCanalAtendimento`)

| Código | Descrição | Sistema Origem |
|--------|-----------|----------------|
| 1 | Presencial | Agências de atendimento |
| 2 | Telefone | Call Center / 0800 |
| 3 | Internet | Site / Portal do Cliente |
| 4 | Aplicativo | App Mobile |

### 3.2 Status da Demanda (`idcStatus`)

| Código | Descrição | Significado |
|--------|-----------|-------------|
| 0 | Em Andamento | Demanda em tratamento |
| 1 | Registrada | Demanda apenas registrada, sem tratamento |
| 2 | Encerrada | Demanda finalizada |

### 3.3 Procedência (`idcProcedencia`)

| Código | Descrição | Quando Usar |
|--------|-----------|-------------|
| 0 | Improcedente | Solicitação indeferida |
| 1 | Procedente | Solicitação deferida |
| 2 | Sem Procedência | Ainda não avaliada ou não aplicável |

### 3.4 Nível de Tratamento (`idcNivelTratamento`)

| Código | Descrição | Típico |
|--------|-----------|--------|
| 0 | 1º Nível | Atendimento inicial / Call Center |
| 1 | 2º Nível | Retaguarda / Análise técnica |
| 2 | 3º Nível | Especializado / Ouvidoria |

### 3.5 Tipologias ANEEL

As tipologias seguem o padrão ANEEL de 7 dígitos. Exemplos comuns:

| Código | Descrição |
|--------|-----------|
| 0101001 | Reclamação - Falta de energia |
| 0101002 | Reclamação - Qualidade de energia |
| 0101003 | Reclamação - Oscilação de tensão |
| 0102001 | Solicitação - Ligação nova |
| 0102002 | Solicitação - Religação |
| 0102003 | Solicitação - Desligamento |
| 0103001 | Informação - Fatura |
| 0103002 | Informação - Consumo |
| 0201001 | Reclamação - Atendimento |
| 0202001 | Reclamação - Cobrança indevida |

**Referência:** Tabela completa de tipologias disponível no site da ANEEL.

---

## 4. Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FLUXO API 2 - DADOS DEMANDA                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│  ANEEL   │         │  RADAR   │         │   CRM    │         │  AJURI   │
│          │         │   API    │         │ (SGC/?)  │         │          │
└────┬─────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │                    │
     │ GET /dadosdemanda  │                    │                    │
     │ ?numProtocolo=X    │                    │                    │
     │───────────────────>│                    │                    │
     │                    │                    │                    │
     │                    │ SELECT * FROM      │                    │
     │                    │ VW_DEMANDAS_RADAR  │                    │
     │                    │ WHERE protocolo=X  │                    │
     │                    │───────────────────>│                    │
     │                    │                    │                    │
     │                    │   Dados demanda    │                    │
     │                    │<───────────────────│                    │
     │                    │                    │                    │
     │                    │ (Se necessário)    │                    │
     │                    │ Busca dados UC     │                    │
     │                    │────────────────────┼───────────────────>│
     │                    │                    │                    │
     │                    │                    │    Dados UC        │
     │                    │<───────────────────┼────────────────────│
     │                    │                    │                    │
     │  JSON Response     │                    │                    │
     │<───────────────────│                    │                    │
     │                    │                    │                    │
```

---

## 5. Sistemas Fonte de Dados

### 5.1 SISTEMA DE CRM/ATENDIMENTO (Obrigatório)

**Este é o sistema principal para esta API.**

| Dado | View/Tabela | Campos Necessários |
|------|-------------|-------------------|
| Dados da demanda | VW_DEMANDAS_RADAR | Todos os campos da API |

**Sistemas possíveis:**
- SGC (Sistema de Gestão Comercial)
- CRM próprio
- Sistema de Call Center
- Outro: _____________

**Equipe Responsável:** CRM / Atendimento ao Cliente / Call Center

### 5.2 SISTEMA COMERCIAL - AJURI (Complementar)

| Dado | View/Tabela | Campos Necessários |
|------|-------------|-------------------|
| Dados do titular | VW_UNIDADES_CONSUMIDORAS_RADAR | nome_titular, cpf_cnpj (mascarado) |
| Dados da UC | VW_UNIDADES_CONSUMIDORAS_RADAR | id_uc, municipio_ibge |

**Equipe Responsável:** Sistema Comercial / Ajuri

---

## 6. Especificação da View do CRM

### 6.1 VW_DEMANDAS_RADAR (CRÍTICA)

**Objetivo:** Fornecer dados das demandas (reclamações, solicitações, informações) registradas no CRM.

```sql
CREATE OR REPLACE VIEW CRM.VW_DEMANDAS_RADAR AS
SELECT
    -- ============================================
    -- IDENTIFICAÇÃO (Obrigatórios)
    -- ============================================
    num_protocolo,               -- VARCHAR2(20) NOT NULL - Número do protocolo (PK)
    num_uc,                      -- VARCHAR2(20) NOT NULL - Código da UC

    -- ============================================
    -- DADOS DO SOLICITANTE (Obrigatórios)
    -- ============================================
    cpf_cnpj_mascarado,          -- VARCHAR2(20) NOT NULL - CPF/CNPJ mascarado (***.***.XXX-**)
    nome_titular,                -- VARCHAR2(200) NOT NULL - Nome do titular

    -- ============================================
    -- CANAL DE ATENDIMENTO (Obrigatório)
    -- ============================================
    canal_atendimento,           -- NUMBER(1) NOT NULL
                                 -- 1=Presencial, 2=Telefone, 3=Internet, 4=App

    -- ============================================
    -- CLASSIFICAÇÃO (Obrigatórios)
    -- ============================================
    tipologia,                   -- VARCHAR2(7) NOT NULL - Código tipologia ANEEL (7 dígitos)
    descricao_tipologia,         -- VARCHAR2(200) - Descrição da tipologia

    -- ============================================
    -- STATUS (Obrigatórios)
    -- ============================================
    status_demanda,              -- NUMBER(1) NOT NULL
                                 -- 0=Em andamento, 1=Registrada, 2=Encerrada

    procedencia,                 -- NUMBER(1) NOT NULL
                                 -- 0=Improcedente, 1=Procedente, 2=Sem procedência

    nivel_tratamento,            -- NUMBER(1) NOT NULL
                                 -- 0=1º nível, 1=2º nível, 2=3º nível

    -- ============================================
    -- DATAS (Obrigatórios)
    -- ============================================
    data_hora_abertura,          -- TIMESTAMP NOT NULL - Data/hora de abertura
    data_hora_encerramento,      -- TIMESTAMP - NULL se ainda aberta

    -- ============================================
    -- LOCALIZAÇÃO (Obrigatório)
    -- ============================================
    municipio_ibge,              -- NUMBER(10) NOT NULL - Código IBGE do município

    -- ============================================
    -- AUDITORIA
    -- ============================================
    data_atualizacao             -- TIMESTAMP - Última atualização

FROM ... -- suas tabelas internas do CRM
WHERE 1=1;  -- Todas as demandas (sem filtro)
```

### 6.2 Mascaramento de CPF/CNPJ (LGPD)

O CPF/CNPJ deve ser mascarado na própria view para conformidade com LGPD:

```sql
-- Exemplo de mascaramento na view
CASE
    WHEN LENGTH(cpf_cnpj) = 11 THEN  -- CPF
        '***.' || SUBSTR(cpf_cnpj, 4, 3) || '.' || SUBSTR(cpf_cnpj, 7, 3) || '-**'
    WHEN LENGTH(cpf_cnpj) = 14 THEN  -- CNPJ
        '**.' || SUBSTR(cpf_cnpj, 3, 3) || '.' || SUBSTR(cpf_cnpj, 6, 3) || '/****-**'
    ELSE
        '***'
END AS cpf_cnpj_mascarado
```

---

## 7. Requisitos por Equipe

### 7.1 EQUIPE CRM / ATENDIMENTO AO CLIENTE

**Prioridade: CRÍTICA**
**Prazo: Março/2026**

#### Questões a Responder:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - CRM/ATENDIMENTO - API 2                            │
└─────────────────────────────────────────────────────────────────────────────┘

1. SISTEMA DE CRM

   1.1. Qual sistema de CRM é utilizado?
        [ ] SGC (Sistema de Gestão Comercial)
        [ ] Sistema próprio (nome: _______________)
        [ ] Outro: _______________

   1.2. O sistema é Oracle?
        [ ] Sim - Versão: _______________
        [ ] Não - Qual banco? _______________

   1.3. Existe integração com outros sistemas?
        [ ] Ajuri (comercial)
        [ ] Sistema Técnico
        [ ] Call Center
        [ ] Outros: _______________

2. DADOS DAS DEMANDAS

   2.1. Formato do número do protocolo:
        Exemplo: _______________
        Máscara/Padrão: _______________

   2.2. Campos disponíveis (marque os existentes):
        [ ] Número do protocolo
        [ ] Número da UC
        [ ] CPF/CNPJ
        [ ] Nome do titular
        [ ] Canal de atendimento
        [ ] Tipologia
        [ ] Status
        [ ] Procedência
        [ ] Data/hora abertura
        [ ] Data/hora encerramento
        [ ] Município
        [ ] Nível de tratamento

   2.3. Canal de atendimento - como é registrado?
        Campo: _______________
        Valores possíveis: _______________

   2.4. Tipologia - usa padrão ANEEL (7 dígitos)?
        [ ] Sim
        [ ] Não - Precisa criar tabela DE-PARA

   2.5. Status da demanda - valores atuais:
        | Valor no Sistema | Significado |
        |------------------|-------------|
        | | |
        | | |
        | | |

   2.6. Procedência - como é registrada?
        [ ] Existe campo específico
        [ ] Deriva de outro campo
        [ ] Não existe (sempre retornará 2)

   2.7. Nível de tratamento - como identificar?
        [ ] Campo específico
        [ ] Baseado no setor/fila
        [ ] Não existe

3. VOLUME DE DADOS

   3.1. Quantidade média de demandas por mês: _______________
   3.2. Quantidade total de demandas no sistema: _______________
   3.3. Período de retenção dos dados: _______________

4. CONEXÃO

   4.1. Servidor (hostname/IP): _______________
   4.2. Porta: _______________
   4.3. Service Name/SID: _______________
   4.4. Schema das tabelas: _______________

5. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Gestor CRM | | | |
   | DBA | | | |
   | Desenvolvedor | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 7.2 EQUIPE CALL CENTER / TELEATENDIMENTO

**Prioridade: ALTA**
**Prazo: Março/2026**

Se o sistema de Call Center for separado do CRM:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - CALL CENTER - API 2                                │
└─────────────────────────────────────────────────────────────────────────────┘

1. SISTEMA DE CALL CENTER

   1.1. Qual sistema é utilizado?
        Nome: _______________
        Fornecedor: _______________

   1.2. Registra demandas diretamente?
        [ ] Sim - Sincroniza com CRM?
        [ ] Não - Apenas transfere para CRM

   1.3. Dados de conexão (se aplicável):
        Servidor: _______________
        Banco: _______________

2. INTEGRAÇÃO

   2.1. Como as demandas do Call Center chegam ao CRM?
        [ ] Integração automática
        [ ] Registro manual
        [ ] Outro: _______________

   2.2. Tempo médio de sincronização: _______________

3. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Supervisor Call Center | | | |
   | TI Call Center | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 7.3 EQUIPE AGÊNCIAS / ATENDIMENTO PRESENCIAL

**Prioridade: MÉDIA**
**Prazo: Março/2026**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - ATENDIMENTO PRESENCIAL - API 2                     │
└─────────────────────────────────────────────────────────────────────────────┘

1. SISTEMA DE ATENDIMENTO PRESENCIAL

   1.1. Qual sistema é utilizado nas agências?
        [ ] Mesmo CRM do Call Center
        [ ] Sistema separado (nome: _______________)

   1.2. Registra demandas diretamente?
        [ ] Sim
        [ ] Não - Usa qual sistema? _______________

2. CANAL DE ATENDIMENTO

   2.1. Como identificar atendimento presencial?
        Campo: _______________
        Valor: _______________

3. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Coordenador Agências | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 7.4 EQUIPE PORTAL DO CLIENTE / APP

**Prioridade: MÉDIA**
**Prazo: Março/2026**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - CANAIS DIGITAIS - API 2                            │
└─────────────────────────────────────────────────────────────────────────────┘

1. CANAIS DIGITAIS

   1.1. Existe Portal do Cliente (site)?
        [ ] Sim - URL: _______________
        [ ] Não

   1.2. Existe App Mobile?
        [ ] Sim - Android / iOS
        [ ] Não

   1.3. Os canais digitais registram demandas?
        [ ] Sim - Integram com CRM
        [ ] Sim - Sistema próprio
        [ ] Não registram demandas

2. INTEGRAÇÃO

   2.1. Como as demandas digitais chegam ao CRM?
        [ ] API direta
        [ ] Fila de mensagens
        [ ] Outro: _______________

3. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Gestor Canais Digitais | | | |
   | Desenvolvedor | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 7.5 EQUIPE OUVIDORIA

**Prioridade: ALTA**
**Prazo: Março/2026**

As demandas de ouvidoria (3º nível) precisam estar contempladas:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - OUVIDORIA - API 2                                  │
└─────────────────────────────────────────────────────────────────────────────┘

1. SISTEMA DA OUVIDORIA

   1.1. A ouvidoria usa o mesmo CRM?
        [ ] Sim
        [ ] Não - Sistema separado: _______________

   1.2. Como identificar demandas de ouvidoria?
        [ ] Campo nível = 3º nível
        [ ] Setor/Fila específica
        [ ] Tipologia específica

2. NUMERAÇÃO

   2.1. Protocolo da ouvidoria é diferente?
        [ ] Sim - Formato: _______________
        [ ] Não - Mesmo protocolo do CRM

3. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Ouvidor | | | |
   | Analista Ouvidoria | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 7.6 EQUIPE SISTEMA COMERCIAL (AJURI)

**Prioridade: MÉDIA** (complementar)
**Prazo: Março/2026**

O Ajuri pode fornecer dados complementares (nome titular, município) caso o CRM não tenha:

- View necessária: VW_UNIDADES_CONSUMIDORAS_RADAR (já especificada no documento do Sistema Comercial)

---

## 8. Mapeamento de Dados Detalhado

### 8.1 Campos da API → Dados do CRM

| Campo API | Campo CRM | Transformação |
|-----------|-----------|---------------|
| `numProtocolo` | num_protocolo | Direto |
| `numUC` | num_uc | Direto |
| `numCpfCnpj` | cpf_cnpj_mascarado | Mascarado na view |
| `nomTitular` | nome_titular | Direto |
| `idcCanalAtendimento` | canal_atendimento | 1=Presencial, 2=Telefone, 3=Internet, 4=App |
| `idcTipologia` | tipologia | Código 7 dígitos ANEEL |
| `idcStatus` | status_demanda | 0=Andamento, 1=Registrada, 2=Encerrada |
| `idcProcedencia` | procedencia | 0=Improcedente, 1=Procedente, 2=Sem |
| `dthAbertura` | data_hora_abertura | Formato dd/mm/yyyy hh:mm |
| `dthEncerramento` | data_hora_encerramento | Formato dd/mm/yyyy hh:mm ou null |
| `ideMunicipio` | municipio_ibge | Código IBGE 7 dígitos |
| `idcNivelTratamento` | nivel_tratamento | 0=1º, 1=2º, 2=3º nível |

---

## 9. Exemplo de Response

### 9.1 Cenário: Demanda encontrada - Em andamento

```json
{
  "idcStatusRequisicao": 1,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "",
  "numProtocolo": "2025123456789",
  "numUC": "1234567",
  "numCpfCnpj": "***.456.789-**",
  "nomTitular": "MARIA JOSE DA SILVA",
  "idcCanalAtendimento": 2,
  "idcTipologia": "0101001",
  "idcStatus": 0,
  "idcProcedencia": 2,
  "dthAbertura": "10/12/2025 08:30",
  "dthEncerramento": null,
  "ideMunicipio": 1400050,
  "idcNivelTratamento": 0
}
```

### 9.2 Cenário: Demanda encontrada - Encerrada procedente

```json
{
  "idcStatusRequisicao": 1,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "",
  "numProtocolo": "2025987654321",
  "numUC": "7654321",
  "numCpfCnpj": "**.123.456/****-**",
  "nomTitular": "EMPRESA XYZ LTDA",
  "idcCanalAtendimento": 3,
  "idcTipologia": "0102001",
  "idcStatus": 2,
  "idcProcedencia": 1,
  "dthAbertura": "01/12/2025 10:00",
  "dthEncerramento": "05/12/2025 16:45",
  "ideMunicipio": 1400175,
  "idcNivelTratamento": 1
}
```

### 9.3 Cenário: Protocolo não encontrado

```json
{
  "idcStatusRequisicao": 1,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "Protocolo não encontrado",
  "numProtocolo": null,
  "numUC": null,
  "numCpfCnpj": null,
  "nomTitular": null,
  "idcCanalAtendimento": null,
  "idcTipologia": null,
  "idcStatus": null,
  "idcProcedencia": null,
  "dthAbertura": null,
  "dthEncerramento": null,
  "ideMunicipio": null,
  "idcNivelTratamento": null
}
```

### 9.4 Cenário: Erro no sistema

```json
{
  "idcStatusRequisicao": 2,
  "emailIndisponibilidade": "radar@roraimaenergia.com.br",
  "mensagem": "Erro de conexão com sistema CRM",
  "numProtocolo": null,
  "numUC": null,
  "numCpfCnpj": null,
  "nomTitular": null,
  "idcCanalAtendimento": null,
  "idcTipologia": null,
  "idcStatus": null,
  "idcProcedencia": null,
  "dthAbertura": null,
  "dthEncerramento": null,
  "ideMunicipio": null,
  "idcNivelTratamento": null
}
```

---

## 10. Requisitos Não-Funcionais

| Requisito | Valor | Justificativa |
|-----------|-------|---------------|
| Tempo de resposta | < 3 segundos | Consulta por chave primária |
| Disponibilidade | 99,5% | 24x7 |
| Retenção histórico | 60 meses | Demandas podem ser consultadas anos depois |

---

## 11. Usuário para Integração - CRM

```sql
-- Criar usuário (executar como DBA no banco do CRM)
CREATE USER RADAR_READONLY IDENTIFIED BY "[SENHA_A_DEFINIR]"
    DEFAULT TABLESPACE USERS;

-- Permissões mínimas
GRANT CREATE SESSION TO RADAR_READONLY;

-- Permissões de SELECT na view
GRANT SELECT ON CRM.VW_DEMANDAS_RADAR TO RADAR_READONLY;
```

---

## 12. Checklist de Implementação

### 12.1 CRM / Atendimento

- [ ] Identificar sistema CRM utilizado
- [ ] Mapear campos disponíveis
- [ ] Criar tabela DE-PARA de tipologias (se necessário)
- [ ] View VW_DEMANDAS_RADAR criada
- [ ] Usuário RADAR_READONLY criado
- [ ] Permissões concedidas
- [ ] Dados de conexão enviados
- [ ] Teste de conectividade realizado

### 12.2 RADAR

- [ ] Database Link configurado (CRM)
- [ ] Synonyms criados
- [ ] Endpoint implementado
- [ ] Mascaramento LGPD validado
- [ ] Testes unitários
- [ ] Testes de integração

### 12.3 Homologação

- [ ] Testes com protocolos reais
- [ ] Validação com equipe de atendimento
- [ ] Teste de protocolos de todos os canais
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
