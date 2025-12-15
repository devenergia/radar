# Mapeamento de Equipes e Sistemas - Projeto RADAR
## Roraima Energia

**Versão:** 1.0
**Data:** 10/12/2025
**Objetivo:** Identificar todas as equipes e sistemas envolvidos no Projeto RADAR

---

## 1. Visão Geral da Integração

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MAPA DE SISTEMAS E EQUIPES - RADAR                        │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │     ANEEL       │
                              │  (Consumidor)   │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │     RADAR       │
                              │   (Orquestrador)│
                              └────────┬────────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  SISTEMA TÉCNICO    │    │  SISTEMA COMERCIAL  │    │       CRM           │
│     (Oracle)        │    │    AJURI (Oracle)   │    │     (Oracle)        │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ • Interrupções      │    │ • Cadastro UCs      │    │ • Demandas          │
│ • Equipes Campo     │    │ • Contatos          │    │ • Protocolos        │
│ • Conjuntos         │    │ • Dados Titulares   │    │ • Tipologias        │
│ • Alimentadores     │    │                     │    │ • Canais            │
│ • DISE              │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  EQUIPES:           │    │  EQUIPES:           │    │  EQUIPES:           │
│  • COD/Operação     │    │  • Comercial        │    │  • Call Center      │
│  • Inservice        │    │  • Cadastro         │    │  • Agências         │
│  • Eng. Distribuição│    │  • TI Comercial     │    │  • Portal/App       │
│  • GIS              │    │                     │    │  • Ouvidoria        │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                       │
                                       ▼
                          ┌─────────────────────┐
                          │  SISTEMA MEDIÇÃO    │
                          │   (Se aplicável)    │
                          ├─────────────────────┤
                          │ • AMI/MDM           │
                          │ • Leituras          │
                          │ • Eventos           │
                          └─────────────────────┘
                                       │
                                       ▼
                          ┌─────────────────────┐
                          │  EQUIPES:           │
                          │  • Medição          │
                          │  • AMI              │
                          └─────────────────────┘
```

---

## 2. Matriz de Responsabilidades por API

### 2.1 API 1 - Quantitativo de Interrupções Ativas

| Sistema/Equipe | Responsabilidade | Prioridade | Documento Ref. |
|----------------|------------------|------------|----------------|
| **Sistema Técnico (Inservice)** | Fornecedor principal de dados | CRÍTICA | API_01_*.md |
| COD/Operação | Dados de interrupções | CRÍTICA | |
| Eng. Distribuição | Dados de alimentadores/conjuntos | ALTA | |
| **Ajuri (Comercial)** | Dados complementares de UCs | MÉDIA | |

**Nota:** O Inservice integra internamente com o SCADA (SAGE). O RADAR não integra diretamente com o SCADA.

### 2.2 API 2 - Dados de Demanda

| Sistema/Equipe | Responsabilidade | Prioridade | Documento Ref. |
|----------------|------------------|------------|----------------|
| **CRM** | Fornecedor principal de dados | CRÍTICA | API_02_*.md |
| Call Center | Demandas telefônicas | CRÍTICA | |
| Agências | Demandas presenciais | ALTA | |
| Portal/App | Demandas digitais | ALTA | |
| Ouvidoria | Demandas 3º nível | ALTA | |
| **Ajuri (Comercial)** | Dados de UCs/Titulares | MÉDIA | |

### 2.3 API 3 - Quantitativo de Demandas Diversas

| Sistema/Equipe | Responsabilidade | Prioridade | Documento Ref. |
|----------------|------------------|------------|----------------|
| **CRM** | Fornecedor único de dados | CRÍTICA | API_03_*.md |
| Call Center | Demandas telefônicas | CRÍTICA | |
| Agências | Demandas presenciais | ALTA | |
| Portal/App | Demandas digitais | ALTA | |
| Ouvidoria | Demandas 3º nível | ALTA | |

### 2.4 API 4 - Tempo Real (REN 1.137)

| Sistema/Equipe | Responsabilidade | Prioridade | Documento Ref. |
|----------------|------------------|------------|----------------|
| **Sistema Técnico** | Dados em tempo real | CRÍTICA | API_04_*.md |
| **Ajuri (Comercial)** | Dados cadastrais | ALTA | |
| **CRM** | Demandas em tempo real | ALTA | |
| **Medição** | Dados de medidores (possível) | MÉDIA | |
| **Infraestrutura** | Conectividade/Segurança | CRÍTICA | |

---

## 3. Listagem Completa de Equipes

### 3.1 SISTEMA TÉCNICO

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SISTEMA TÉCNICO                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: COD (Centro de Operação da Distribuição)                           │
│  ─────────────────────────────────────────────────                          │
│  Responsabilidades:                                                         │
│  • Gerenciamento de interrupções                                            │
│  • Despacho de equipes de campo                                             │
│  • Monitoramento em tempo real                                              │
│                                                                             │
│  Dados fornecidos:                                                          │
│  • VW_INTERRUPCOES_ATIVAS_RADAR                                             │
│  • VW_EQUIPES_CAMPO_RADAR                                                   │
│  • VW_UCS_INTERRUPCAO_RADAR                                                 │
│                                                                             │
│  Contatos:                                                                  │
│  | Função           | Nome | Email | Telefone |                             │
│  |------------------|------|-------|----------|                             │
│  | Gerente COD      |      |       |          |                             │
│  | Supervisor       |      |       |          |                             │
│  | Analista Técnico |      |       |          |                             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SISTEMA: INSERVICE                                                         │
│  ─────────────────────                                                      │
│  Descrição:                                                                 │
│  • Sistema que gerencia as interrupções no Sistema Técnico                  │
│  • Integra internamente com o SCADA (SAGE)                                  │
│  • O RADAR não integra diretamente com SCADA - apenas com Inservice         │
│                                                                             │
│  Dados fornecidos (via Sistema Técnico):                                    │
│  • Interrupções ativas e histórico                                          │
│  • Status de alimentadores                                                  │
│  • Eventos e alarmes (já processados do SCADA)                              │
│                                                                             │
│  Contatos:                                                                  │
│  | Função              | Nome | Email | Telefone |                          │
│  |---------------------|------|-------|----------|                          │
│  | Gestor Inservice    |      |       |          |                          │
│  | Analista/Desenvolv. |      |       |          |                          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: ENGENHARIA DE DISTRIBUIÇÃO                                         │
│  ─────────────────────────────────────                                      │
│  Responsabilidades:                                                         │
│  • Cadastro de rede elétrica                                                │
│  • Conjuntos e alimentadores                                                │
│  • Indicadores DEC/FEC/DISE                                                 │
│                                                                             │
│  Dados fornecidos:                                                          │
│  • VW_CONJUNTOS_RADAR                                                       │
│  • VW_ALIMENTADORES_RADAR                                                   │
│  • VW_DISE_RADAR                                                            │
│  • VW_HISTORICO_INTERRUPCOES_RADAR                                          │
│                                                                             │
│  Contatos:                                                                  │
│  | Função                 | Nome | Email | Telefone |                       │
│  |------------------------|------|-------|----------|                       │
│  | Gerente Eng. Distrib.  |      |       |          |                       │
│  | Engenheiro de Rede     |      |       |          |                       │
│  | Analista de Indicadores|      |       |          |                       │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: GIS (Sistema de Informação Geográfica)                             │
│  ─────────────────────────────────────────────────                          │
│  Responsabilidades:                                                         │
│  • Base georreferenciada                                                    │
│  • Coordenadas de equipamentos                                              │
│  • Mapas de rede                                                            │
│                                                                             │
│  Dados fornecidos:                                                          │
│  • Coordenadas (latitude/longitude)                                         │
│  • Vinculação UC x Rede                                                     │
│                                                                             │
│  Contatos:                                                                  │
│  | Função          | Nome | Email | Telefone |                              │
│  |-----------------|------|-------|----------|                              │
│  | Analista GIS    |      |       |          |                              │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: DBA SISTEMA TÉCNICO                                                │
│  ────────────────────────────                                               │
│  Responsabilidades:                                                         │
│  • Criação de views                                                         │
│  • Criação de usuário RADAR_READONLY                                        │
│  • Configuração de Database Link                                            │
│  • Performance e índices                                                    │
│                                                                             │
│  Contatos:                                                                  │
│  | Função          | Nome | Email | Telefone |                              │
│  |-----------------|------|-------|----------|                              │
│  | DBA Principal   |      |       |          |                              │
│  | DBA Backup      |      |       |          |                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.2 SISTEMA COMERCIAL (AJURI)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SISTEMA COMERCIAL (AJURI)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: CADASTRO COMERCIAL                                                 │
│  ────────────────────────────                                               │
│  Responsabilidades:                                                         │
│  • Cadastro de unidades consumidoras                                        │
│  • Dados de titulares                                                       │
│  • Endereços e localização                                                  │
│                                                                             │
│  Dados fornecidos:                                                          │
│  • VW_UNIDADES_CONSUMIDORAS_RADAR                                           │
│                                                                             │
│  Contatos:                                                                  │
│  | Função               | Nome | Email | Telefone |                         │
│  |----------------------|------|-------|----------|                         │
│  | Gerente Comercial    |      |       |          |                         │
│  | Supervisor Cadastro  |      |       |          |                         │
│  | Analista Cadastro    |      |       |          |                         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: RELACIONAMENTO COM CLIENTE                                         │
│  ─────────────────────────────────────                                      │
│  Responsabilidades:                                                         │
│  • Gestão de contatos                                                       │
│  • Consentimento LGPD para comunicações                                     │
│  • Atualização cadastral                                                    │
│                                                                             │
│  Dados fornecidos:                                                          │
│  • VW_CONTATOS_RADAR                                                        │
│                                                                             │
│  Contatos:                                                                  │
│  | Função                | Nome | Email | Telefone |                        │
│  |-----------------------|------|-------|----------|                        │
│  | Gerente Relacionamento|      |       |          |                        │
│  | Analista              |      |       |          |                        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: TI COMERCIAL / DBA AJURI                                           │
│  ─────────────────────────────────                                          │
│  Responsabilidades:                                                         │
│  • Suporte ao sistema Ajuri                                                 │
│  • Criação de views                                                         │
│  • Criação de usuário RADAR_READONLY                                        │
│  • Configuração de Database Link                                            │
│                                                                             │
│  Contatos:                                                                  │
│  | Função          | Nome | Email | Telefone |                              │
│  |-----------------|------|-------|----------|                              │
│  | Gestor TI Com.  |      |       |          |                              │
│  | DBA Ajuri       |      |       |          |                              │
│  | Desenvolvedor   |      |       |          |                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.3 SISTEMA CRM / ATENDIMENTO

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SISTEMA CRM / ATENDIMENTO                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: CALL CENTER                                                        │
│  ─────────────────────                                                      │
│  Responsabilidades:                                                         │
│  • Atendimento telefônico (0800)                                            │
│  • Registro de demandas - Canal 2 (Telefone)                                │
│  • 1º nível de atendimento                                                  │
│                                                                             │
│  Dados fornecidos:                                                          │
│  • Demandas telefônicas                                                     │
│  • Protocolos de atendimento                                                │
│                                                                             │
│  Sistema utilizado: _______________                                         │
│                                                                             │
│  Contatos:                                                                  │
│  | Função              | Nome | Email | Telefone |                          │
│  |---------------------|------|-------|----------|                          │
│  | Gerente Call Center |      |       |          |                          │
│  | Supervisor          |      |       |          |                          │
│  | Analista Qualidade  |      |       |          |                          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: AGÊNCIAS DE ATENDIMENTO                                            │
│  ────────────────────────────────                                           │
│  Responsabilidades:                                                         │
│  • Atendimento presencial                                                   │
│  • Registro de demandas - Canal 1 (Presencial)                              │
│  • 1º nível de atendimento                                                  │
│                                                                             │
│  Dados fornecidos:                                                          │
│  • Demandas presenciais                                                     │
│                                                                             │
│  Sistema utilizado: _______________                                         │
│  (Mesmo do Call Center? [ ] Sim [ ] Não)                                    │
│                                                                             │
│  Contatos:                                                                  │
│  | Função               | Nome | Email | Telefone |                         │
│  |----------------------|------|-------|----------|                         │
│  | Coordenador Agências |      |       |          |                         │
│  | Supervisor           |      |       |          |                         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: CANAIS DIGITAIS (Portal/App)                                       │
│  ──────────────────────────────────────                                     │
│  Responsabilidades:                                                         │
│  • Portal do Cliente (site)                                                 │
│  • Aplicativo mobile                                                        │
│  • Registro de demandas - Canal 3 (Internet) e 4 (App)                      │
│                                                                             │
│  Dados fornecidos:                                                          │
│  • Demandas digitais                                                        │
│  • Auto-atendimento                                                         │
│                                                                             │
│  Sistema utilizado: _______________                                         │
│  (Integra com CRM? [ ] Sim [ ] Não)                                         │
│                                                                             │
│  Contatos:                                                                  │
│  | Função              | Nome | Email | Telefone |                          │
│  |---------------------|------|-------|----------|                          │
│  | Gestor Canais Dig.  |      |       |          |                          │
│  | Desenvolvedor       |      |       |          |                          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: RETAGUARDA / 2º NÍVEL                                              │
│  ────────────────────────────────                                           │
│  Responsabilidades:                                                         │
│  • Análise técnica de demandas                                              │
│  • 2º nível de atendimento                                                  │
│  • Resolução de casos complexos                                             │
│                                                                             │
│  Sistema utilizado: _______________                                         │
│                                                                             │
│  Contatos:                                                                  │
│  | Função            | Nome | Email | Telefone |                            │
│  |-------------------|------|-------|----------|                            │
│  | Coord. Retaguarda |      |       |          |                            │
│  | Analista          |      |       |          |                            │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: OUVIDORIA                                                          │
│  ───────────────────                                                        │
│  Responsabilidades:                                                         │
│  • Atendimento de última instância                                          │
│  • 3º nível de atendimento                                                  │
│  • Demandas ANEEL                                                           │
│                                                                             │
│  Sistema utilizado: _______________                                         │
│  (Mesmo do CRM? [ ] Sim [ ] Não)                                            │
│                                                                             │
│  Contatos:                                                                  │
│  | Função         | Nome | Email | Telefone |                               │
│  |----------------|------|-------|----------|                               │
│  | Ouvidor        |      |       |          |                               │
│  | Analista       |      |       |          |                               │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: TI CRM / DBA                                                       │
│  ──────────────────────                                                     │
│  Responsabilidades:                                                         │
│  • Suporte ao sistema CRM                                                   │
│  • Criação de views                                                         │
│  • Criação de usuário RADAR_READONLY                                        │
│  • Integração entre sistemas de atendimento                                 │
│                                                                             │
│  Contatos:                                                                  │
│  | Função          | Nome | Email | Telefone |                              │
│  |-----------------|------|-------|----------|                              │
│  | Gestor TI CRM   |      |       |          |                              │
│  | DBA             |      |       |          |                              │
│  | Desenvolvedor   |      |       |          |                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.4 SISTEMA DE MEDIÇÃO (Se Aplicável)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SISTEMA DE MEDIÇÃO                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: MEDIÇÃO                                                            │
│  ─────────────────                                                          │
│  Responsabilidades:                                                         │
│  • Gestão de medidores                                                      │
│  • Leitura e coleta de dados                                                │
│  • Medição inteligente (AMI)                                                │
│                                                                             │
│  Dados fornecidos (potenciais):                                             │
│  • Leituras de energia                                                      │
│  • Eventos de falta de energia                                              │
│  • Qualidade de energia                                                     │
│                                                                             │
│  Sistema utilizado: _______________                                         │
│  Fornecedor: _______________                                                │
│  Banco de dados: [ ] Oracle [ ] Outro: _______________                      │
│                                                                             │
│  Possui medição inteligente? [ ] Sim [ ] Não                                │
│  Quantidade de medidores smart: _______________                             │
│  % de cobertura: _____%                                                     │
│                                                                             │
│  Contatos:                                                                  │
│  | Função           | Nome | Email | Telefone |                             │
│  |------------------|------|-------|----------|                             │
│  | Gerente Medição  |      |       |          |                             │
│  | Engenheiro AMI   |      |       |          |                             │
│  | Analista         |      |       |          |                             │
│  | DBA              |      |       |          |                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.5 INFRAESTRUTURA / TI

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INFRAESTRUTURA / TI                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: INFRAESTRUTURA DE TI                                               │
│  ────────────────────────────────                                           │
│  Responsabilidades:                                                         │
│  • Servidores                                                               │
│  • Redes e conectividade                                                    │
│  • Firewall e segurança de perímetro                                        │
│  • Links de comunicação                                                     │
│                                                                             │
│  Ações para o RADAR:                                                        │
│  • Provisionar servidores para API                                          │
│  • Configurar conectividade externa                                         │
│  • Liberar regras de firewall                                               │
│                                                                             │
│  Contatos:                                                                  │
│  | Função            | Nome | Email | Telefone |                            │
│  |-------------------|------|-------|----------|                            │
│  | Gerente Infra     |      |       |          |                            │
│  | Admin. Rede       |      |       |          |                            │
│  | Admin. Servidores |      |       |          |                            │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: SEGURANÇA DA INFORMAÇÃO                                            │
│  ─────────────────────────────────                                          │
│  Responsabilidades:                                                         │
│  • Políticas de segurança                                                   │
│  • Certificados SSL                                                         │
│  • Controle de acesso                                                       │
│  • Auditoria                                                                │
│                                                                             │
│  Ações para o RADAR:                                                        │
│  • Validar arquitetura de segurança                                         │
│  • Provisionar certificados                                                 │
│  • Aprovar exposição externa                                                │
│                                                                             │
│  Contatos:                                                                  │
│  | Função            | Nome | Email | Telefone |                            │
│  |-------------------|------|-------|----------|                            │
│  | Gestor Segurança  |      |       |          |                            │
│  | Analista Seg.     |      |       |          |                            │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EQUIPE: DBA CORPORATIVO                                                    │
│  ─────────────────────────                                                  │
│  Responsabilidades:                                                         │
│  • Administração de bancos Oracle                                           │
│  • Criação de Database Links                                                │
│  • Performance e tuning                                                     │
│  • Backup e recovery                                                        │
│                                                                             │
│  Ações para o RADAR:                                                        │
│  • Configurar Database Links entre sistemas                                 │
│  • Criar banco do RADAR                                                     │
│  • Otimizar views e índices                                                 │
│                                                                             │
│  Contatos:                                                                  │
│  | Função          | Nome | Email | Telefone |                              │
│  |-----------------|------|-------|----------|                              │
│  | DBA Sênior      |      |       |          |                              │
│  | DBA             |      |       |          |                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Cronograma de Engajamento das Equipes

### 4.1 Fase 1 - API 1 (Prazo: Dezembro/2025)

| Semana | Equipes | Ação |
|--------|---------|------|
| 1-2 | Sistema Técnico, DBA | Análise de requisitos, mapeamento de dados |
| 2-3 | Sistema Técnico, DBA | Criação das views |
| 3-4 | Sistema Técnico, Infra | Configuração de conectividade |
| 4-5 | TI RADAR | Desenvolvimento e testes |
| 5-6 | Todas | Homologação |

### 4.2 Fase 2 - APIs 2 e 3 (Prazo: Abril-Maio/2026)

| Semana | Equipes | Ação |
|--------|---------|------|
| 1-2 | CRM, Call Center, Ouvidoria | Análise de requisitos, mapeamento |
| 2-4 | CRM, DBA | Criação das views |
| 4-5 | CRM, Canais Digitais | Integração de fontes |
| 5-6 | TI RADAR | Desenvolvimento e testes |
| 6-8 | Todas | Homologação |

### 4.3 Fase 3 - API 4 Tempo Real (Prazo: 60 dias após instruções)

| Semana | Equipes | Ação |
|--------|---------|------|
| 1 | Todas | Análise das instruções ANEEL |
| 1-2 | Sistema Técnico, Ajuri, CRM | Identificação de gaps |
| 2-4 | Todas | Implementação de novos requisitos |
| 4-6 | TI RADAR, Infra | Desenvolvimento e infraestrutura |
| 6-8 | Todas | Homologação |

---

## 5. Formulário de Identificação de Equipes

**INSTRUÇÕES:** Preencha este formulário e distribua para os gestores de cada área.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│          FORMULÁRIO DE IDENTIFICAÇÃO DE EQUIPES - PROJETO RADAR              │
└─────────────────────────────────────────────────────────────────────────────┘

Data de preenchimento: ___/___/______
Preenchido por: _________________________
Área: _________________________

1. SISTEMA/ÁREA DE RESPONSABILIDADE

   [ ] Sistema Técnico (COD/Inservice/Eng. Distribuição)
   [ ] Sistema Comercial (Ajuri)
   [ ] CRM / Atendimento
   [ ] Call Center
   [ ] Agências
   [ ] Canais Digitais
   [ ] Ouvidoria
   [ ] Medição
   [ ] Infraestrutura
   [ ] Segurança da Informação
   [ ] DBA
   [ ] Outro: _______________

2. SISTEMA DE INFORMAÇÃO UTILIZADO

   Nome do sistema: _______________
   Fornecedor: _______________
   Versão: _______________
   Banco de dados: [ ] Oracle [ ] Outro: _______________
   Versão do banco: _______________

3. RESPONSÁVEIS PELA INTEGRAÇÃO

   | Papel | Nome | Email | Telefone | Pode criar views? |
   |-------|------|-------|----------|-------------------|
   | Gestor da área | | | | |
   | Responsável técnico | | | | |
   | DBA | | | | |
   | Desenvolvedor | | | | |
   | Backup/Substituto | | | | |

4. DISPONIBILIDADE PARA O PROJETO

   4.1. A equipe pode participar de reuniões de alinhamento?
        [ ] Sim
        [ ] Não - Restrição: _______________

   4.2. Disponibilidade semanal estimada para o projeto: _____ horas

   4.3. Período de férias/indisponibilidade previsto:
        De ___/___/______ a ___/___/______

5. CONHECIMENTO DO SISTEMA

   5.1. Quem conhece a estrutura de dados (tabelas/campos)?
        Nome: _______________

   5.2. Quem pode criar views/stored procedures?
        Nome: _______________

   5.3. Existe documentação do sistema?
        [ ] Sim - Localização: _______________
        [ ] Não

6. DEPENDÊNCIAS E INTEGRAÇÕES

   6.1. O sistema integra com outros sistemas?
        [ ] Não
        [ ] Sim - Quais?
            _______________
            _______________
            _______________

   6.2. Existem jobs/processos batch que atualizam dados?
        [ ] Não
        [ ] Sim - Frequência: _______________

7. OBSERVAÇÕES

   ___________________________________________________________
   ___________________________________________________________
   ___________________________________________________________

8. ASSINATURA

   Nome: _________________________
   Cargo: _________________________
   Data: ___/___/______

└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Resumo de Documentos por Equipe

| Equipe | Documentos a Receber |
|--------|---------------------|
| **Sistema Técnico** | REQUISITOS_SISTEMA_TECNICO_RADAR.md, API_01_*.md, API_04_*.md |
| **Sistema Comercial (Ajuri)** | REQUISITOS_SISTEMA_COMERCIAL_RADAR.md, API_01_*.md, API_04_*.md |
| **CRM / Atendimento** | API_02_*.md, API_03_*.md, API_04_*.md |
| **Call Center** | API_02_*.md, API_03_*.md |
| **Agências** | API_02_*.md, API_03_*.md |
| **Canais Digitais** | API_02_*.md, API_03_*.md |
| **Ouvidoria** | API_02_*.md, API_03_*.md |
| **Medição** | API_04_*.md |
| **Infraestrutura** | API_04_*.md |
| **Segurança** | API_04_*.md |

---

## 7. Próximos Passos

1. [ ] Identificar gestores de cada área
2. [ ] Distribuir documentos específicos para cada equipe
3. [ ] Agendar reunião de kick-off com todas as equipes
4. [ ] Coletar formulários de identificação preenchidos
5. [ ] Criar grupo de comunicação (email/Teams/WhatsApp)
6. [ ] Definir cronograma detalhado com cada equipe
7. [ ] Iniciar desenvolvimento da API 1

---

## 8. Contatos do Projeto RADAR

| Função | Nome | Email | Telefone |
|--------|------|-------|----------|
| Patrocinador | | | |
| Coordenador | | | |
| Gerente de Projeto | | | |
| Arquiteto de Solução | | | |

---

*Documento gerado em 10/12/2025 - Projeto RADAR - Roraima Energia S/A*
