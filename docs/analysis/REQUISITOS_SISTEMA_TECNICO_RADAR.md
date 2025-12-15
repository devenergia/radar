# Requisitos de Integração - Sistema Técnico
## Projeto RADAR - Roraima Energia

**Versão:** 1.0
**Data:** 10/12/2025
**De:** Equipe TI - Projeto RADAR
**Para:** Equipe Sistema Técnico
**Assunto:** Requisitos de dados e views para integração com Sistema RADAR

---

## 1. Contexto

O **Sistema RADAR** está sendo desenvolvido para atender às exigências regulatórias da ANEEL, conforme:
- **Ofício Circular nº 14/2025-SFE/ANEEL** - APIs de interrupções e demandas
- **REN 1.137/2025** - Portal Público de Interrupções (Art. 106-107), Notificações SMS/WhatsApp (Art. 105), Indicador DISE (Art. 173/180-A)

O RADAR consumirá dados do **Sistema Técnico** via **Oracle Database Link** para:
- Fornecer dados de interrupções em tempo real para a ANEEL
- Alimentar o Portal Público de Interrupções
- Disparar notificações para consumidores afetados
- Monitorar o indicador DISE durante situações de emergência

---

## 2. Arquitetura de Integração

```
┌─────────────────────────────────┐
│      SISTEMA TÉCNICO            │
│         (Oracle)                │
│                                 │
│  ┌───────────────────────────┐  │
│  │  Views criadas pela       │  │
│  │  equipe Sistema Técnico   │  │
│  │  (VW_*_RADAR)             │  │
│  └─────────────┬─────────────┘  │
└────────────────┼────────────────┘
                 │
                 │ Database Link (somente leitura)
                 │
                 ▼
┌─────────────────────────────────┐
│        SISTEMA RADAR            │
│         (Oracle)                │
│                                 │
│  - APIs ANEEL                   │
│  - Portal Público               │
│  - Notificações                 │
│  - Dashboard                    │
└─────────────────────────────────┘
```

---

## 3. O Que Precisamos

### 3.1 Resumo das Views Necessárias

| View | Schema Sugerido | Prioridade | Prazo |
|------|-----------------|------------|-------|
| VW_INTERRUPCOES_ATIVAS_RADAR | OPERACAO | **CRÍTICA** | Dez/2025 |
| VW_CONJUNTOS_RADAR | CADASTRO | **CRÍTICA** | Dez/2025 |
| VW_ALIMENTADORES_RADAR | CADASTRO | ALTA | Dez/2025 |
| VW_EQUIPES_CAMPO_RADAR | OPERACAO | ALTA | Jan/2026 |
| VW_UCS_INTERRUPCAO_RADAR | OPERACAO | ALTA | Jan/2026 |
| VW_DISE_RADAR | INDICADORES | MÉDIA | Fev/2026 |
| VW_HISTORICO_INTERRUPCOES_RADAR | HISTORICO | MÉDIA | Mar/2026 |

---

## 4. Especificação Detalhada das Views

### 4.1 VW_INTERRUPCOES_ATIVAS_RADAR (CRÍTICA)

**Objetivo:** Fornecer todas as interrupções ativas em tempo real para API ANEEL e Portal Público.

**Frequência de consulta:** A cada 5 minutos

```sql
CREATE OR REPLACE VIEW OPERACAO.VW_INTERRUPCOES_ATIVAS_RADAR AS
SELECT
    -- ============================================
    -- IDENTIFICAÇÃO (Obrigatórios)
    -- ============================================
    id_interrupcao,              -- VARCHAR2(50) NOT NULL - ID único da interrupção

    -- ============================================
    -- CLASSIFICAÇÃO (Obrigatórios)
    -- ============================================
    tipo_interrupcao,            -- VARCHAR2(20) NOT NULL - Valores: 'PROGRAMADA' ou 'NAO_PROGRAMADA'
    origem,                      -- VARCHAR2(50) - Origem: 'INSERVICE', 'MANUAL', 'CRM', etc.

    -- ============================================
    -- LOCALIZAÇÃO (Obrigatórios)
    -- ============================================
    id_alimentador,              -- VARCHAR2(20) NOT NULL - Código do alimentador
    nome_alimentador,            -- VARCHAR2(100) - Nome do alimentador
    id_subestacao,               -- VARCHAR2(20) - Código da subestação
    nome_subestacao,             -- VARCHAR2(100) - Nome da subestação

    -- ============================================
    -- TEMPORALIDADE (Obrigatórios)
    -- ============================================
    data_hora_inicio,            -- TIMESTAMP NOT NULL - Data/hora início da interrupção
    data_hora_fim,               -- TIMESTAMP - NULL se ainda ativa
    previsao_restabelecimento,   -- TIMESTAMP - Previsão de normalização

    -- ============================================
    -- CAUSA
    -- ============================================
    id_causa,                    -- NUMBER(10) - Código interno da causa
    descricao_causa,             -- VARCHAR2(200) - Descrição da causa
    causa_conhecida,             -- NUMBER(1) - 1=conhecida, 0=em investigação

    -- ============================================
    -- STATUS DA OCORRÊNCIA (REN 1.137 Art. 107)
    -- ============================================
    status_ocorrencia,           -- VARCHAR2(30) NOT NULL
                                 -- Valores: 'EM_PREPARACAO', 'DESLOCAMENTO', 'EM_EXECUCAO', 'CONCLUIDA'

    -- ============================================
    -- QUANTITATIVOS (Obrigatórios)
    -- ============================================
    qtd_ucs_afetadas,            -- NUMBER(10) NOT NULL - Quantidade de UCs sem energia
    qtd_consumidores,            -- NUMBER(10) - Quantidade de consumidores (pode ser igual UCs)

    -- ============================================
    -- EQUIPES (REN 1.137 Art. 107)
    -- ============================================
    qtd_equipes_designadas,      -- NUMBER(10) DEFAULT 0 - Equipes alocadas

    -- ============================================
    -- GEOLOCALIZAÇÃO (Para mapa do Portal)
    -- ============================================
    latitude,                    -- NUMBER(10,7) - Latitude do ponto central
    longitude,                   -- NUMBER(10,7) - Longitude do ponto central

    -- ============================================
    -- ÁREA GEOGRÁFICA (Obrigatórios)
    -- ============================================
    municipio_ibge,              -- NUMBER(10) NOT NULL - Código IBGE do município (7 dígitos)
    bairro,                      -- VARCHAR2(100) - Bairro/Localidade principal
    tipo_area,                   -- VARCHAR2(10) - 'URBANO' ou 'RURAL'

    -- ============================================
    -- AUDITORIA
    -- ============================================
    data_atualizacao             -- TIMESTAMP NOT NULL - Última atualização do registro

FROM ... -- suas tabelas internas
WHERE data_hora_fim IS NULL;     -- Apenas interrupções ativas (não finalizadas)
```

**Códigos IBGE dos municípios de Roraima:**

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

### 4.2 VW_CONJUNTOS_RADAR (CRÍTICA)

**Objetivo:** Fornecer os conjuntos elétricos conforme cadastro ANEEL para agregação dos dados da API.

```sql
CREATE OR REPLACE VIEW CADASTRO.VW_CONJUNTOS_RADAR AS
SELECT
    id_conjunto,                 -- NUMBER(10) PRIMARY KEY - Código do conjunto
    nome_conjunto,               -- VARCHAR2(100) NOT NULL - Nome do conjunto
    codigo_aneel,                -- VARCHAR2(20) - Código oficial ANEEL
    qtd_ucs_total,               -- NUMBER(10) NOT NULL - Total de UCs no conjunto
    municipios_abrangidos,       -- VARCHAR2(500) - Códigos IBGE separados por vírgula
                                 -- Ex: '1400050,1400175,1400308'
    ativo,                       -- NUMBER(1) DEFAULT 1 - 1=ativo, 0=inativo
    data_atualizacao             -- TIMESTAMP

FROM ... -- suas tabelas internas
WHERE ativo = 1;
```

---

### 4.3 VW_ALIMENTADORES_RADAR

**Objetivo:** Cadastro de alimentadores para referência e relatórios.

```sql
CREATE OR REPLACE VIEW CADASTRO.VW_ALIMENTADORES_RADAR AS
SELECT
    id_alimentador,              -- VARCHAR2(20) PRIMARY KEY
    nome_alimentador,            -- VARCHAR2(100) NOT NULL
    id_subestacao,               -- VARCHAR2(20)
    nome_subestacao,             -- VARCHAR2(100)
    tensao_kv,                   -- NUMBER(10,2) - Tensão em kV
    extensao_km,                 -- NUMBER(10,2) - Extensão em km
    qtd_ucs_total,               -- NUMBER(10) NOT NULL - Total de UCs
    municipio_principal,         -- NUMBER(10) - Código IBGE
    ativo,                       -- NUMBER(1) DEFAULT 1
    data_atualizacao             -- TIMESTAMP

FROM ... -- suas tabelas internas
WHERE ativo = 1;
```

---

### 4.4 VW_EQUIPES_CAMPO_RADAR

**Objetivo:** Status das equipes em campo para exibição no Portal Público (Art. 107 REN 1.137).

```sql
CREATE OR REPLACE VIEW OPERACAO.VW_EQUIPES_CAMPO_RADAR AS
SELECT
    id_equipe,                   -- VARCHAR2(20) PRIMARY KEY
    nome_equipe,                 -- VARCHAR2(100)
    tipo_equipe,                 -- VARCHAR2(50) - 'LINHA_VIVA', 'EMERGENCIA', 'PROGRAMADA'
    status,                      -- VARCHAR2(30) NOT NULL
                                 -- Valores: 'DISPONIVEL', 'EM_DESLOCAMENTO', 'EM_CAMPO'
    id_interrupcao_atual,        -- VARCHAR2(50) - FK para interrupção sendo atendida
    latitude_atual,              -- NUMBER(10,7) - Posição atual
    longitude_atual,             -- NUMBER(10,7) - Posição atual
    hora_ultima_posicao,         -- TIMESTAMP - Última atualização GPS
    data_atualizacao             -- TIMESTAMP

FROM ... -- suas tabelas internas;
```

---

### 4.5 VW_UCS_INTERRUPCAO_RADAR

**Objetivo:** Relação de UCs afetadas por cada interrupção (necessário para notificações SMS/WhatsApp).

```sql
CREATE OR REPLACE VIEW OPERACAO.VW_UCS_INTERRUPCAO_RADAR AS
SELECT
    id_interrupcao,              -- VARCHAR2(50) NOT NULL - FK para interrupção
    id_uc,                       -- VARCHAR2(20) NOT NULL - Código da UC
    data_hora_inicio,            -- TIMESTAMP NOT NULL - Início da interrupção para esta UC
    data_hora_fim,               -- TIMESTAMP - NULL se ainda interrompida
    municipio_ibge,              -- NUMBER(10) - Código IBGE
    tipo_area                    -- VARCHAR2(10) - 'URBANO' ou 'RURAL'

FROM ... -- suas tabelas internas
WHERE data_hora_fim IS NULL;     -- Apenas UCs ainda sem energia
```

---

### 4.6 VW_DISE_RADAR

**Objetivo:** Indicador DISE calculado durante situações de emergência (Art. 173/180-A REN 1.137).

**IMPORTANTE:** O cálculo do DISE deve ser feito pelo Sistema Técnico. O RADAR apenas consome o valor calculado.

```sql
CREATE OR REPLACE VIEW INDICADORES.VW_DISE_RADAR AS
SELECT
    -- ============================================
    -- IDENTIFICAÇÃO DA EMERGÊNCIA
    -- ============================================
    id_emergencia,               -- VARCHAR2(50) NOT NULL - ID da situação de emergência
    descricao_emergencia,        -- VARCHAR2(200) - Descrição do evento
    tipo_evento,                 -- VARCHAR2(50) - 'TEMPESTADE', 'ENCHENTE', 'INCENDIO', etc.

    -- ============================================
    -- PERÍODO DA EMERGÊNCIA
    -- ============================================
    data_inicio_emergencia,      -- TIMESTAMP NOT NULL - Início da emergência declarada
    data_fim_emergencia,         -- TIMESTAMP - NULL se ainda ativa
    emergencia_ativa,            -- NUMBER(1) - 1=ativa, 0=encerrada

    -- ============================================
    -- UNIDADE CONSUMIDORA
    -- ============================================
    id_uc,                       -- VARCHAR2(20) NOT NULL - Código da UC
    municipio_ibge,              -- NUMBER(10) NOT NULL - Código IBGE
    tipo_area,                   -- VARCHAR2(10) NOT NULL - 'URBANO' ou 'RURAL'

    -- ============================================
    -- INTERRUPÇÃO
    -- ============================================
    id_interrupcao,              -- VARCHAR2(50) NOT NULL - ID da interrupção
    data_inicio_interrupcao,     -- TIMESTAMP NOT NULL
    data_fim_interrupcao,        -- TIMESTAMP - NULL se ainda interrompida

    -- ============================================
    -- DISE CALCULADO (pelo Sistema Técnico)
    -- ============================================
    dise_minutos,                -- NUMBER(10) NOT NULL - Duração em minutos
    dise_horas,                  -- NUMBER(10,2) NOT NULL - Duração em horas
    limite_horas,                -- NUMBER(10) NOT NULL - 24 (urbano) ou 48 (rural)
    em_violacao,                 -- NUMBER(1) - 1 se dise_horas > limite_horas
    percentual_limite,           -- NUMBER(5,2) - (dise_horas / limite_horas) * 100

    -- ============================================
    -- DECRETO (se aplicável)
    -- ============================================
    decreto_estadual,            -- VARCHAR2(50) - Número do decreto estadual
    decreto_municipal,           -- VARCHAR2(50) - Número do decreto municipal

    -- ============================================
    -- AUDITORIA
    -- ============================================
    data_calculo,                -- TIMESTAMP NOT NULL - Data/hora do cálculo
    data_atualizacao             -- TIMESTAMP

FROM ... -- suas tabelas internas;
```

**Regras de Cálculo do DISE:**
- **Limite Urbano:** 24 horas
- **Limite Rural:** 48 horas
- **em_violacao:** 1 quando dise_horas > limite_horas
- Considerar apenas o período dentro da emergência declarada

---

### 4.7 VW_HISTORICO_INTERRUPCOES_RADAR

**Objetivo:** Histórico de interrupções para recuperação de dados (parâmetro dthRecuperacao da API ANEEL).

**Retenção mínima:** 36 meses

```sql
CREATE OR REPLACE VIEW HISTORICO.VW_HISTORICO_INTERRUPCOES_RADAR AS
SELECT
    id_interrupcao,              -- VARCHAR2(50) NOT NULL
    tipo_interrupcao,            -- VARCHAR2(20) NOT NULL
    id_alimentador,              -- VARCHAR2(20)
    municipio_ibge,              -- NUMBER(10)
    data_hora_inicio,            -- TIMESTAMP NOT NULL
    data_hora_fim,               -- TIMESTAMP NOT NULL
    duracao_minutos,             -- NUMBER(10) - Duração total
    qtd_ucs_afetadas,            -- NUMBER(10)
    id_causa,                    -- NUMBER(10)
    descricao_causa,             -- VARCHAR2(200)
    chi,                         -- NUMBER(15,2) - Consumidor Hora Interrompido
    tipo_area,                   -- VARCHAR2(10)
    data_registro                -- TIMESTAMP

FROM ... -- suas tabelas internas
WHERE data_hora_fim IS NOT NULL  -- Apenas interrupções finalizadas
  AND data_hora_inicio >= ADD_MONTHS(SYSDATE, -36);  -- Últimos 36 meses
```

---

## 5. Usuário para Integração

Solicitamos a criação de um usuário **SOMENTE LEITURA** para o Database Link:

```sql
-- Criar usuário (executar como DBA)
CREATE USER RADAR_READONLY IDENTIFIED BY "[SENHA_A_DEFINIR]"
    DEFAULT TABLESPACE USERS;

-- Permissões mínimas
GRANT CREATE SESSION TO RADAR_READONLY;

-- Permissões de SELECT nas views
GRANT SELECT ON OPERACAO.VW_INTERRUPCOES_ATIVAS_RADAR TO RADAR_READONLY;
GRANT SELECT ON OPERACAO.VW_EQUIPES_CAMPO_RADAR TO RADAR_READONLY;
GRANT SELECT ON OPERACAO.VW_UCS_INTERRUPCAO_RADAR TO RADAR_READONLY;
GRANT SELECT ON CADASTRO.VW_ALIMENTADORES_RADAR TO RADAR_READONLY;
GRANT SELECT ON CADASTRO.VW_CONJUNTOS_RADAR TO RADAR_READONLY;
GRANT SELECT ON INDICADORES.VW_DISE_RADAR TO RADAR_READONLY;
GRANT SELECT ON HISTORICO.VW_HISTORICO_INTERRUPCOES_RADAR TO RADAR_READONLY;
```

---

## 6. Informações Necessárias da Equipe Sistema Técnico

Por favor, preencha e retorne:

### 6.1 Dados de Conexão

| Item | Valor |
|------|-------|
| **Servidor (hostname/IP)** | |
| **Porta** | 1521 |
| **Service Name** | |
| **Usuário criado** | RADAR_READONLY |
| **Senha** | (enviar por canal seguro) |

### 6.2 Mapeamento de Campos

Para cada view, informar o mapeamento com suas tabelas internas:

**VW_INTERRUPCOES_ATIVAS_RADAR:**

| Campo RADAR | Tabela/Campo Sistema Técnico | Observações |
|-------------|------------------------------|-------------|
| id_interrupcao | | |
| tipo_interrupcao | | Como mapear para 'PROGRAMADA'/'NAO_PROGRAMADA'? |
| id_alimentador | | |
| data_hora_inicio | | |
| municipio_ibge | | Já usa código IBGE ou precisa DE-PARA? |
| status_ocorrencia | | Como mapear para os status esperados? |
| qtd_ucs_afetadas | | |

### 6.3 Cronograma

| View | Previsão de Entrega | Responsável |
|------|---------------------|-------------|
| VW_INTERRUPCOES_ATIVAS_RADAR | | |
| VW_CONJUNTOS_RADAR | | |
| VW_ALIMENTADORES_RADAR | | |
| VW_EQUIPES_CAMPO_RADAR | | |
| VW_UCS_INTERRUPCAO_RADAR | | |
| VW_DISE_RADAR | | |
| VW_HISTORICO_INTERRUPCOES_RADAR | | |

### 6.4 Dúvidas e Pendências

Liste aqui quaisquer dúvidas ou impedimentos:

1.
2.
3.

---

## 7. Requisitos de Performance

| Requisito | Valor |
|-----------|-------|
| Tempo de resposta das views | < 5 segundos |
| Disponibilidade | 24x7 |
| Atualização dos dados | Tempo real (sem delay) |

---

## 8. Contatos

| Função | Nome | Email | Telefone |
|--------|------|-------|----------|
| Coordenador RADAR | | | |
| DBA RADAR | | | |
| Desenvolvedor RADAR | | | |

---

## 9. Próximos Passos

1. [ ] Equipe Sistema Técnico analisa requisitos
2. [ ] Reunião de alinhamento (se necessário)
3. [ ] Criação das views no ambiente de desenvolvimento
4. [ ] Criação do usuário RADAR_READONLY
5. [ ] Envio dos dados de conexão
6. [ ] Testes de integração
7. [ ] Homologação
8. [ ] Produção

---

**Prazo para retorno:** ___/___/______

**Dúvidas?** Entrar em contato com a equipe TI do Projeto RADAR.

---

*Documento gerado em 10/12/2025 - Projeto RADAR - Roraima Energia S/A*
