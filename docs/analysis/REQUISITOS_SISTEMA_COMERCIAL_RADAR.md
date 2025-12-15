# Requisitos de Integração - Sistema Comercial (Ajuri)
## Projeto RADAR - Roraima Energia

**Versão:** 1.0
**Data:** 10/12/2025
**De:** Equipe TI - Projeto RADAR
**Para:** Equipe Sistema Comercial (Ajuri)
**Assunto:** Requisitos de dados e views para integração com Sistema RADAR

---

## 1. Contexto

O **Sistema RADAR** está sendo desenvolvido para atender às exigências regulatórias da ANEEL, conforme:
- **Ofício Circular nº 14/2025-SFE/ANEEL** - APIs de interrupções e demandas
- **REN 1.137/2025** - Portal Público de Interrupções (Art. 106-107), Notificações SMS/WhatsApp (Art. 105)

O RADAR consumirá dados do **Sistema Comercial (Ajuri)** via **Oracle Database Link** para:
- Obter dados de contato dos consumidores (telefone/WhatsApp) para notificações
- Vincular unidades consumidoras às interrupções
- Personalizar comunicações com dados cadastrais

### 1.1 Fluxo de Notificações (REN 1.137 Art. 105)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                      FLUXO DE NOTIFICAÇÃO SMS/WHATSAPP                     │
└───────────────────────────────────────────────────────────────────────────┘

  SISTEMA TÉCNICO                    RADAR                      AJURI
 ┌─────────────────┐           ┌─────────────────┐        ┌─────────────────┐
 │                 │           │                 │        │                 │
 │  Nova           │           │  Identifica     │        │  Fornece        │
 │  Interrupção    │──────────▶│  UCs afetadas   │───────▶│  Contatos       │
 │  Detectada      │    1      │                 │    2   │  (tel/WhatsApp) │
 │                 │           │                 │        │                 │
 └─────────────────┘           └────────┬────────┘        └─────────────────┘
                                        │
                                        │ 3
                                        ▼
                               ┌─────────────────┐
                               │                 │
                               │  Envia SMS/     │
                               │  WhatsApp para  │
                               │  Consumidores   │
                               │                 │
                               └─────────────────┘
```

**Notificações obrigatórias:**
- **Início da interrupção** - Informar que UC está sem energia
- **Atualização de previsão** - Quando previsão de retorno muda
- **Restabelecimento** - Confirmar que energia foi restaurada

---

## 2. Arquitetura de Integração

```
┌─────────────────────────────────────┐
│    SISTEMA COMERCIAL (AJURI)        │
│            (Oracle)                 │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  Views criadas pela           │  │
│  │  equipe Sistema Comercial     │  │
│  │  (VW_*_RADAR)                 │  │
│  └─────────────┬─────────────────┘  │
└────────────────┼────────────────────┘
                 │
                 │ Database Link (somente leitura)
                 │
                 ▼
┌─────────────────────────────────────┐
│          SISTEMA RADAR              │
│            (Oracle)                 │
│                                     │
│  - Notificações SMS/WhatsApp        │
│  - Portal Público                   │
│  - APIs ANEEL                       │
└─────────────────────────────────────┘
```

---

## 3. O Que Precisamos

### 3.1 Resumo das Views Necessárias

| View | Schema Sugerido | Prioridade | Prazo | Objetivo |
|------|-----------------|------------|-------|----------|
| VW_CONTATOS_RADAR | CLIENTE | **CRÍTICA** | Dez/2025 | Dados de contato para SMS/WhatsApp |
| VW_UNIDADES_CONSUMIDORAS_RADAR | CLIENTE | ALTA | Dez/2025 | Dados cadastrais das UCs |

---

## 4. Especificação Detalhada das Views

### 4.1 VW_CONTATOS_RADAR (CRÍTICA)

**Objetivo:** Fornecer dados de contato dos consumidores para envio de notificações SMS/WhatsApp sobre interrupções.

**Frequência de consulta:** Sob demanda (quando há interrupção afetando a UC)

**IMPORTANTE sobre LGPD:**
- O RADAR utilizará os contatos EXCLUSIVAMENTE para notificações sobre interrupções
- Não haverá armazenamento permanente dos dados de contato no RADAR
- Os dados são consultados em tempo real apenas quando necessário

```sql
CREATE OR REPLACE VIEW CLIENTE.VW_CONTATOS_RADAR AS
SELECT
    -- ============================================
    -- IDENTIFICAÇÃO DA UC (Obrigatórios)
    -- ============================================
    id_uc,                       -- VARCHAR2(20) NOT NULL - Código da UC (chave de busca)

    -- ============================================
    -- DADOS DO TITULAR
    -- ============================================
    nome_titular,                -- VARCHAR2(200) NOT NULL - Nome do titular da UC
    tipo_pessoa,                 -- VARCHAR2(2) - 'PF' ou 'PJ'

    -- ============================================
    -- CONTATOS PARA NOTIFICAÇÃO (Pelo menos 1 obrigatório)
    -- ============================================
    telefone_celular_1,          -- VARCHAR2(20) - Telefone principal (formato: 5595999999999)
    telefone_celular_2,          -- VARCHAR2(20) - Telefone secundário
    telefone_fixo,               -- VARCHAR2(20) - Telefone fixo (não recebe SMS/WhatsApp)
    email,                       -- VARCHAR2(200) - Email para futuras notificações

    -- ============================================
    -- PREFERÊNCIAS DE CONTATO
    -- ============================================
    aceita_sms,                  -- NUMBER(1) DEFAULT 1 - 1=aceita, 0=não aceita
    aceita_whatsapp,             -- NUMBER(1) DEFAULT 1 - 1=aceita, 0=não aceita
    aceita_email,                -- NUMBER(1) DEFAULT 0 - 1=aceita, 0=não aceita

    -- ============================================
    -- LOCALIZAÇÃO (para contexto na mensagem)
    -- ============================================
    endereco_instalacao,         -- VARCHAR2(300) - Endereço completo da UC
    bairro,                      -- VARCHAR2(100) - Bairro
    municipio,                   -- VARCHAR2(100) - Nome do município
    municipio_ibge,              -- NUMBER(10) - Código IBGE do município

    -- ============================================
    -- CLASSIFICAÇÃO
    -- ============================================
    classe_consumo,              -- VARCHAR2(50) - 'RESIDENCIAL', 'COMERCIAL', 'INDUSTRIAL', etc.
    subclasse_consumo,           -- VARCHAR2(50) - Subclasse (se houver)

    -- ============================================
    -- STATUS
    -- ============================================
    uc_ativa,                    -- NUMBER(1) DEFAULT 1 - 1=ativa, 0=inativa

    -- ============================================
    -- AUDITORIA
    -- ============================================
    data_atualizacao             -- TIMESTAMP - Última atualização do cadastro

FROM ... -- suas tabelas internas
WHERE uc_ativa = 1               -- Apenas UCs ativas
  AND (telefone_celular_1 IS NOT NULL OR telefone_celular_2 IS NOT NULL);
```

**Formato dos Telefones:**
- Formato esperado: `5595999999999` (código país + DDD + número)
- DDD de Roraima: `95`
- Se armazenado em outro formato, favor fazer a conversão na view
- Exemplos de conversão:
  - `(95) 99999-9999` → `5595999999999`
  - `95999999999` → `5595999999999`
  - `999999999` → `5595999999999` (assumir DDD 95)

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

### 4.2 VW_UNIDADES_CONSUMIDORAS_RADAR

**Objetivo:** Fornecer dados cadastrais completos das unidades consumidoras para enriquecimento de dados e relatórios.

```sql
CREATE OR REPLACE VIEW CLIENTE.VW_UNIDADES_CONSUMIDORAS_RADAR AS
SELECT
    -- ============================================
    -- IDENTIFICAÇÃO (Obrigatórios)
    -- ============================================
    id_uc,                       -- VARCHAR2(20) NOT NULL PRIMARY KEY - Código da UC
    id_cliente,                  -- VARCHAR2(20) - Código do cliente (titular)

    -- ============================================
    -- DADOS DO TITULAR
    -- ============================================
    nome_titular,                -- VARCHAR2(200) NOT NULL
    cpf_cnpj,                    -- VARCHAR2(20) - Mascarado para LGPD: ***.***.XXX-**
    tipo_pessoa,                 -- VARCHAR2(2) - 'PF' ou 'PJ'

    -- ============================================
    -- ENDEREÇO DE INSTALAÇÃO (Obrigatórios)
    -- ============================================
    logradouro,                  -- VARCHAR2(200) NOT NULL
    numero,                      -- VARCHAR2(20)
    complemento,                 -- VARCHAR2(100)
    bairro,                      -- VARCHAR2(100) NOT NULL
    cep,                         -- VARCHAR2(10)
    municipio,                   -- VARCHAR2(100) NOT NULL
    municipio_ibge,              -- NUMBER(10) NOT NULL - Código IBGE
    uf,                          -- VARCHAR2(2) DEFAULT 'RR'

    -- ============================================
    -- GEOLOCALIZAÇÃO (se disponível)
    -- ============================================
    latitude,                    -- NUMBER(10,7)
    longitude,                   -- NUMBER(10,7)

    -- ============================================
    -- CLASSIFICAÇÃO (Obrigatórios)
    -- ============================================
    classe_consumo,              -- VARCHAR2(50) NOT NULL
                                 -- Valores: 'RESIDENCIAL', 'COMERCIAL', 'INDUSTRIAL',
                                 --          'RURAL', 'PODER_PUBLICO', 'ILUMINACAO_PUBLICA',
                                 --          'SERVICO_PUBLICO', 'CONSUMO_PROPRIO'
    subclasse_consumo,           -- VARCHAR2(50)

    -- ============================================
    -- DADOS TÉCNICOS
    -- ============================================
    tipo_fornecimento,           -- VARCHAR2(20) - 'MONOFASICO', 'BIFASICO', 'TRIFASICO'
    tensao_fornecimento,         -- VARCHAR2(20) - Ex: '127/220V', '220/380V'
    carga_instalada_kw,          -- NUMBER(10,2) - Carga instalada em kW
    demanda_contratada_kw,       -- NUMBER(10,2) - Demanda contratada em kW (se aplicável)

    -- ============================================
    -- DADOS DE FATURAMENTO (para contexto)
    -- ============================================
    grupo_tarifario,             -- VARCHAR2(10) - 'A' ou 'B'
    subgrupo_tarifario,          -- VARCHAR2(10) - 'A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3'
    modalidade_tarifaria,        -- VARCHAR2(50) - 'CONVENCIONAL', 'BRANCA', 'AZUL', 'VERDE'

    -- ============================================
    -- VINCULAÇÃO ELÉTRICA (para cruzamento com Sistema Técnico)
    -- ============================================
    id_alimentador,              -- VARCHAR2(20) - Código do alimentador (se disponível)
    id_transformador,            -- VARCHAR2(20) - Código do transformador (se disponível)
    id_conjunto,                 -- NUMBER(10) - Código do conjunto elétrico

    -- ============================================
    -- TIPO DE ÁREA (Obrigatório para DISE)
    -- ============================================
    tipo_area,                   -- VARCHAR2(10) NOT NULL - 'URBANO' ou 'RURAL'

    -- ============================================
    -- STATUS
    -- ============================================
    status_uc,                   -- VARCHAR2(20) NOT NULL - 'ATIVA', 'SUSPENSA', 'CANCELADA'
    data_ligacao,                -- DATE - Data de ligação da UC
    data_desligamento,           -- DATE - Data de desligamento (se aplicável)

    -- ============================================
    -- INDICADORES ESPECIAIS
    -- ============================================
    cliente_prioritario,         -- NUMBER(1) DEFAULT 0 - 1=prioritário (hospital, etc)
    tipo_prioridade,             -- VARCHAR2(50) - 'HOSPITAL', 'DELEGACIA', 'ASILO', etc.

    -- ============================================
    -- AUDITORIA
    -- ============================================
    data_cadastro,               -- DATE
    data_atualizacao             -- TIMESTAMP

FROM ... -- suas tabelas internas
WHERE status_uc IN ('ATIVA', 'SUSPENSA');  -- Excluir apenas canceladas
```

---

## 5. Consultas que o RADAR Fará

Para ajudar no entendimento, seguem exemplos de como o RADAR utilizará os dados:

### 5.1 Buscar Contatos para Notificação de Interrupção

```sql
-- Quando uma interrupção afeta várias UCs, o RADAR buscará os contatos
SELECT
    c.id_uc,
    c.nome_titular,
    c.telefone_celular_1,
    c.telefone_celular_2,
    c.aceita_sms,
    c.aceita_whatsapp,
    c.endereco_instalacao,
    c.bairro
FROM VW_CONTATOS_RADAR@AJURI_LINK c
WHERE c.id_uc IN (
    SELECT id_uc FROM VW_UCS_INTERRUPCAO_RADAR@SISTEC_LINK
    WHERE id_interrupcao = :p_id_interrupcao
);
```

### 5.2 Buscar Dados de UC para Portal Público

```sql
-- Enriquecer dados de interrupção com informações da UC
SELECT
    u.id_uc,
    u.classe_consumo,
    u.tipo_area,
    u.municipio,
    u.bairro
FROM VW_UNIDADES_CONSUMIDORAS_RADAR@AJURI_LINK u
WHERE u.id_uc = :p_id_uc;
```

### 5.3 Estatísticas por Classe de Consumo

```sql
-- Relatório de impacto por classe de consumo
SELECT
    u.classe_consumo,
    COUNT(*) AS qtd_ucs_afetadas
FROM VW_UNIDADES_CONSUMIDORAS_RADAR@AJURI_LINK u
WHERE u.id_uc IN (SELECT id_uc FROM interrupcoes_ativas)
GROUP BY u.classe_consumo;
```

---

## 6. Usuário para Integração

Solicitamos a criação de um usuário **SOMENTE LEITURA** para o Database Link:

```sql
-- Criar usuário (executar como DBA)
CREATE USER RADAR_READONLY IDENTIFIED BY "[SENHA_A_DEFINIR]"
    DEFAULT TABLESPACE USERS;

-- Permissões mínimas
GRANT CREATE SESSION TO RADAR_READONLY;

-- Permissões de SELECT nas views
GRANT SELECT ON CLIENTE.VW_CONTATOS_RADAR TO RADAR_READONLY;
GRANT SELECT ON CLIENTE.VW_UNIDADES_CONSUMIDORAS_RADAR TO RADAR_READONLY;
```

**Importante:** O usuário terá apenas permissão de SELECT, sem capacidade de modificar dados.

---

## 7. Volume de Dados Estimado

Para dimensionamento, informar:

| Informação | Valor |
|------------|-------|
| Quantidade total de UCs ativas | |
| Quantidade de UCs com telefone cadastrado | |
| Quantidade de UCs com WhatsApp habilitado | |
| Crescimento mensal estimado de UCs | |

---

## 8. Informações Necessárias da Equipe Sistema Comercial

Por favor, preencha e retorne:

### 8.1 Dados de Conexão

| Item | Valor |
|------|-------|
| **Servidor (hostname/IP)** | |
| **Porta** | 1521 |
| **Service Name** | |
| **Usuário criado** | RADAR_READONLY |
| **Senha** | (enviar por canal seguro) |

### 8.2 Mapeamento de Campos - VW_CONTATOS_RADAR

| Campo RADAR | Tabela/Campo Ajuri | Observações |
|-------------|-------------------|-------------|
| id_uc | | Qual campo identifica a UC? |
| nome_titular | | |
| telefone_celular_1 | | Formato atual do telefone? |
| telefone_celular_2 | | |
| aceita_sms | | Existe esse controle? |
| aceita_whatsapp | | Existe esse controle? |
| municipio_ibge | | Já usa código IBGE ou precisa DE-PARA? |

### 8.3 Mapeamento de Campos - VW_UNIDADES_CONSUMIDORAS_RADAR

| Campo RADAR | Tabela/Campo Ajuri | Observações |
|-------------|-------------------|-------------|
| id_uc | | |
| classe_consumo | | Como mapear para os valores esperados? |
| tipo_area | | Como identificar URBANO/RURAL? |
| id_alimentador | | Existe vinculação com rede elétrica? |
| cliente_prioritario | | Existe marcação de cliente prioritário? |

### 8.4 Cronograma

| View | Previsão de Entrega | Responsável |
|------|---------------------|-------------|
| VW_CONTATOS_RADAR | | |
| VW_UNIDADES_CONSUMIDORAS_RADAR | | |

### 8.5 Considerações sobre LGPD

- [ ] Os dados de contato estão em conformidade com LGPD?
- [ ] O cliente autorizou uso dos dados para comunicação de serviços?
- [ ] Existe controle de consentimento para SMS/WhatsApp?

Observações sobre LGPD:
___________________________________________________________
___________________________________________________________

### 8.6 Dúvidas e Pendências

Liste aqui quaisquer dúvidas ou impedimentos:

1.
2.
3.

---

## 9. Requisitos de Performance

| Requisito | Valor |
|-----------|-------|
| Tempo de resposta das views | < 3 segundos |
| Disponibilidade | 24x7 |
| Volume estimado por consulta | Até 10.000 UCs |

---

## 10. Mensagens de Notificação

Para conhecimento, seguem exemplos das mensagens que serão enviadas:

### 10.1 SMS - Início de Interrupção

```
RORAIMA ENERGIA: Identificamos falta de energia na regiao de {bairro}.
Equipes trabalhando. Previsao de retorno: {previsao}.
Info: 0800 591 0196
```

### 10.2 WhatsApp - Início de Interrupção

```
*Roraima Energia - Aviso de Interrupção*

Olá, {nome_titular}!

Identificamos uma interrupção no fornecimento de energia que afeta sua unidade consumidora.

📍 *Local:* {endereco}
⏰ *Início:* {data_hora_inicio}
🔧 *Previsão de retorno:* {previsao}

Nossas equipes já estão trabalhando para normalizar o fornecimento o mais rápido possível.

Para mais informações: 0800 591 0196
```

### 10.3 SMS - Restabelecimento

```
RORAIMA ENERGIA: Energia restabelecida na regiao de {bairro}
as {hora_fim}. Obrigado pela compreensao.
Info: 0800 591 0196
```

---

## 11. Contatos

| Função | Nome | Email | Telefone |
|--------|------|-------|----------|
| Coordenador RADAR | | | |
| DBA RADAR | | | |
| Desenvolvedor RADAR | | | |

---

## 12. Próximos Passos

1. [ ] Equipe Sistema Comercial analisa requisitos
2. [ ] Reunião de alinhamento (se necessário)
3. [ ] Validação de conformidade LGPD
4. [ ] Criação das views no ambiente de desenvolvimento
5. [ ] Criação do usuário RADAR_READONLY
6. [ ] Envio dos dados de conexão
7. [ ] Testes de integração
8. [ ] Homologação
9. [ ] Produção

---

**Prazo para retorno:** ___/___/______

**Dúvidas?** Entrar em contato com a equipe TI do Projeto RADAR.

---

*Documento gerado em 10/12/2025 - Projeto RADAR - Roraima Energia S/A*
