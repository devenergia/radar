# API 4 - Tempo Real para ANEEL (REN 1.137 Art. 113)
## Projeto RADAR - Roraima Energia

**Versão:** 1.0
**Data:** 10/12/2025
**Prazo ANEEL:** 60 dias após instruções da ANEEL
**Base Legal:** REN 1.137/2025 - Artigo 113

---

## 1. Resumo Executivo

| Item | Descrição |
|------|-----------|
| **Endpoint** | A definir pela ANEEL |
| **Objetivo** | Permitir que a ANEEL extraia dados em tempo real diretamente do sistema da distribuidora |
| **Frequência de Consulta** | Tempo real / sob demanda ANEEL |
| **Criticidade** | **ALTA** - 60 dias após instruções |
| **Autenticação** | A definir pela ANEEL |

---

## 2. Base Legal

### 2.1 Artigo 113 - REN 1.137/2025

> *"A distribuidora deve disponibilizar à ANEEL sistema que permita a extração de dados em tempo real, conforme especificações técnicas a serem definidas pela Agência."*

### 2.2 Interpretação

- A ANEEL ainda não publicou as especificações técnicas detalhadas
- O prazo de 60 dias conta a partir da publicação das instruções
- O sistema deve estar **preparado** para implementar rapidamente quando as especificações forem definidas

---

## 3. Arquitetura Preparatória

### 3.1 Cenários Possíveis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                CENÁRIOS DE INTEGRAÇÃO TEMPO REAL                             │
└─────────────────────────────────────────────────────────────────────────────┘

CENÁRIO A: API REST (mais provável)
┌──────────┐         ┌──────────┐         ┌──────────┐
│  ANEEL   │ ─────── │  RADAR   │ ─────── │ Sistemas │
│          │  HTTPS  │   API    │  Oracle │ Internos │
└──────────┘         └──────────┘         └──────────┘

CENÁRIO B: Acesso direto ao banco (menos provável)
┌──────────┐                              ┌──────────┐
│  ANEEL   │ ──────────────────────────── │  Oracle  │
│          │    Oracle Database Link      │  RADAR   │
└──────────┘                              └──────────┘

CENÁRIO C: API GraphQL (possível)
┌──────────┐         ┌──────────┐         ┌──────────┐
│  ANEEL   │ ─────── │  RADAR   │ ─────── │ Sistemas │
│          │ GraphQL │   API    │  Oracle │ Internos │
└──────────┘         └──────────┘         └──────────┘

CENÁRIO D: Streaming (WebSocket/SSE)
┌──────────┐         ┌──────────┐         ┌──────────┐
│  ANEEL   │ ═══════ │  RADAR   │ ─────── │ Sistemas │
│          │WebSocket│   API    │  Oracle │ Internos │
└──────────┘         └──────────┘         └──────────┘
```

### 3.2 Preparação Recomendada

Para estar pronto para qualquer cenário, o RADAR deve:

1. **Dados consolidados e atualizados** - Materialized Views com refresh frequente
2. **Infraestrutura escalável** - Capacidade de responder a múltiplas requisições simultâneas
3. **Segurança robusta** - Autenticação, autorização, criptografia, auditoria
4. **Documentação OpenAPI** - Pronta para qualquer endpoint que a ANEEL solicite

---

## 4. Dados que Provavelmente Serão Solicitados

### 4.1 Baseado nas outras APIs e na REN 1.137

| Categoria | Dados | Sistema Fonte |
|-----------|-------|---------------|
| **Interrupções** | Todas interrupções ativas em tempo real | Sistema Técnico |
| **Interrupções** | Histórico de interrupções | Sistema Técnico |
| **Demandas** | Todas demandas abertas | CRM |
| **Demandas** | Histórico de demandas | CRM |
| **UCs** | Cadastro de unidades consumidoras | Ajuri (Comercial) |
| **Indicadores** | DEC, FEC, DISE | Sistema Técnico |
| **Geográfico** | Dados de alimentadores, conjuntos | Sistema Técnico |
| **Notificações** | Status de envio SMS/WhatsApp | RADAR |

### 4.2 Granularidade Esperada

A API de tempo real provavelmente exigirá dados mais granulares que as APIs 1, 2 e 3:

| API Atual | Granularidade | API Tempo Real (provável) |
|-----------|---------------|---------------------------|
| API 1 | Agregado por município | Individual por interrupção |
| API 2 | Por protocolo | Por protocolo + histórico |
| API 3 | Agregado | Detalhado por demanda |

---

## 5. Sistemas Fonte de Dados

### 5.1 SISTEMA TÉCNICO (Obrigatório)

| Dado | View Necessária | Prioridade |
|------|-----------------|------------|
| Interrupções detalhadas | VW_INTERRUPCOES_DETALHES_RADAR | ALTA |
| UCs por interrupção | VW_UCS_INTERRUPCAO_RADAR | ALTA |
| Equipes em campo | VW_EQUIPES_CAMPO_RADAR | MÉDIA |
| Indicadores DEC/FEC | VW_INDICADORES_RADAR | MÉDIA |
| DISE | VW_DISE_RADAR | ALTA |

**Equipe Responsável:** Sistema Técnico / COD

**Nota:** O Sistema Técnico já recebe dados do SCADA (SAGE) internamente. O RADAR não integra diretamente com o SCADA.

### 5.2 SISTEMA COMERCIAL - AJURI (Obrigatório)

| Dado | View Necessária | Prioridade |
|------|-----------------|------------|
| Cadastro de UCs | VW_UNIDADES_CONSUMIDORAS_RADAR | ALTA |
| Contatos | VW_CONTATOS_RADAR | MÉDIA |

**Equipe Responsável:** Sistema Comercial / Ajuri

### 5.3 SISTEMA CRM (Obrigatório)

| Dado | View Necessária | Prioridade |
|------|-----------------|------------|
| Demandas detalhadas | VW_DEMANDAS_RADAR | ALTA |
| Histórico demandas | VW_DEMANDAS_HISTORICO_RADAR | MÉDIA |

**Equipe Responsável:** CRM / Atendimento

### 5.4 SISTEMA DE MEDIÇÃO (Possível)

A ANEEL pode solicitar dados de medição em tempo real:

| Dado | Fonte | Prioridade |
|------|-------|------------|
| Leitura de medidores | Sistema de Medição | A DEFINIR |
| Curva de carga | AMI/MDM | A DEFINIR |
| Qualidade de energia | PQ Meters | A DEFINIR |

**Equipe Responsável:** Medição / AMI

---

## 6. Requisitos por Equipe

### 6.1 EQUIPE SISTEMA TÉCNICO

**Prioridade: ALTA**
**Prazo: Preparação imediata**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - SISTEMA TÉCNICO - API TEMPO REAL                   │
└─────────────────────────────────────────────────────────────────────────────┘

1. CAPACIDADE DE TEMPO REAL

   1.1. Os dados de interrupções são atualizados em tempo real?
        [ ] Sim - Latência: _______________
        [ ] Não - Frequência de atualização: _______________

   1.2. O sistema suporta consultas frequentes (a cada segundo)?
        [ ] Sim
        [ ] Não - Limite recomendado: _______________

   1.3. Existe log de auditoria das consultas?
        [ ] Sim
        [ ] Não

2. DADOS ADICIONAIS

   2.1. Quais dados adicionais podem ser fornecidos além dos já especificados?
        [ ] Dados de qualidade de energia
        [ ] Alarmes e eventos (já integrados do SCADA/SAGE)
        [ ] Outros: _______________
        (Nota: O RADAR não integra diretamente com SCADA - dados vêm via Sistema Técnico)

   2.2. Existe limite de volume por consulta?
        [ ] Não
        [ ] Sim - Limite: _______________

3. CONECTIVIDADE

   3.1. O banco suporta conexões simultâneas adicionais?
        [ ] Sim - Quantas? _______________
        [ ] Não - Limite atual: _______________

   3.2. Existe redundância/failover?
        [ ] Sim
        [ ] Não

4. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Gestor Sistema Técnico | | | |
   | Analista/Desenvolvedor | | | |
   | DBA | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 6.2 EQUIPE SISTEMA COMERCIAL (AJURI)

**Prioridade: ALTA**
**Prazo: Preparação imediata**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - AJURI - API TEMPO REAL                             │
└─────────────────────────────────────────────────────────────────────────────┘

1. CAPACIDADE DE TEMPO REAL

   1.1. Com que frequência os dados cadastrais são atualizados?
        [ ] Tempo real (transacional)
        [ ] Batch - Frequência: _______________

   1.2. O sistema suporta consultas frequentes?
        [ ] Sim
        [ ] Não - Limite: _______________

2. DADOS ADICIONAIS

   2.1. Quais dados adicionais podem ser fornecidos?
        [ ] Histórico de consumo
        [ ] Débitos/inadimplência
        [ ] Contratos
        [ ] Outros: _______________

3. CONECTIVIDADE

   3.1. O banco suporta conexões simultâneas adicionais?
        [ ] Sim - Quantas? _______________
        [ ] Não - Limite atual: _______________

4. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Gestor Comercial | | | |
   | DBA Ajuri | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 6.3 EQUIPE CRM

**Prioridade: ALTA**
**Prazo: Preparação imediata**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - CRM - API TEMPO REAL                               │
└─────────────────────────────────────────────────────────────────────────────┘

1. CAPACIDADE DE TEMPO REAL

   1.1. As demandas são registradas em tempo real?
        [ ] Sim
        [ ] Não - Delay: _______________

   1.2. Todas as fontes (Call Center, Agências, Digital) estão integradas?
        [ ] Sim - Tempo de sincronização: _______________
        [ ] Não - Quais não? _______________

2. DADOS ADICIONAIS

   2.1. Quais dados adicionais podem ser fornecidos?
        [ ] Gravações de chamadas (metadados)
        [ ] Tempo de espera
        [ ] Transferências entre níveis
        [ ] Outros: _______________

3. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Gestor CRM | | | |
   | DBA | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 6.4 EQUIPE DE MEDIÇÃO (Potencial)

**Prioridade: MÉDIA**
**Prazo: Quando solicitado pela ANEEL**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - MEDIÇÃO - API TEMPO REAL                           │
└─────────────────────────────────────────────────────────────────────────────┘

1. SISTEMA DE MEDIÇÃO

   1.1. Qual sistema de medição é utilizado?
        [ ] AMI (Advanced Metering Infrastructure)
        [ ] MDM (Meter Data Management)
        [ ] Sistema próprio: _______________
        [ ] Não possui medição inteligente

   1.2. Fornecedor do sistema: _______________

   1.3. Banco de dados:
        [ ] Oracle
        [ ] Outro: _______________

2. DADOS DISPONÍVEIS

   2.1. Quais dados podem ser fornecidos?
        [ ] Leituras de energia ativa
        [ ] Leituras de energia reativa
        [ ] Demanda
        [ ] Tensão
        [ ] Corrente
        [ ] Fator de potência
        [ ] Eventos de falta de energia
        [ ] Outros: _______________

   2.2. Frequência das leituras:
        [ ] 15 minutos
        [ ] 1 hora
        [ ] Diária
        [ ] Outra: _______________

3. COBERTURA

   3.1. Quantidade de medidores inteligentes: _______________
   3.2. % de cobertura do parque: _____%
   3.3. Foco: [ ] Residencial [ ] Comercial [ ] Industrial [ ] Todos

4. INTEGRAÇÃO

   4.1. Existe integração com outros sistemas?
        [ ] Sistema Técnico
        [ ] Comercial (Ajuri)
        [ ] Faturamento
        [ ] Outros: _______________

   4.2. É possível criar views para consulta externa?
        [ ] Sim
        [ ] Não - Por quê? _______________

5. PERFORMANCE

   5.1. O sistema suporta consultas em tempo real?
        [ ] Sim
        [ ] Não - Alternativa: _______________

   5.2. Volume de dados diário: _______________

6. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Gestor Medição | | | |
   | Engenheiro AMI | | | |
   | DBA | | | |
   | Fornecedor | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 6.5 EQUIPE DE INFRAESTRUTURA/TI

**Prioridade: ALTA**
**Prazo: Preparação imediata**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FORMULÁRIO - INFRAESTRUTURA - API TEMPO REAL                    │
└─────────────────────────────────────────────────────────────────────────────┘

1. CONECTIVIDADE EXTERNA

   1.1. Existe link dedicado para ANEEL?
        [ ] Sim - Capacidade: _______________
        [ ] Não - Pode ser provisionado?

   1.2. IPs públicos disponíveis: _______________

   1.3. Firewall permite conexões externas controladas?
        [ ] Sim
        [ ] Não - Processo para liberação: _______________

2. SEGURANÇA

   2.1. Existe certificado SSL válido?
        [ ] Sim - Emissor: _______________
        [ ] Não - Pode ser adquirido?

   2.2. Existe WAF (Web Application Firewall)?
        [ ] Sim
        [ ] Não

   2.3. Existe IDS/IPS?
        [ ] Sim
        [ ] Não

3. MONITORAMENTO

   3.1. Existe monitoramento 24x7?
        [ ] Sim - Ferramenta: _______________
        [ ] Não

   3.2. Existe NOC (Network Operations Center)?
        [ ] Sim
        [ ] Não

4. SERVIDORES

   4.1. Servidores disponíveis para API tempo real:
        | Servidor | CPU | RAM | Disco | SO |
        |----------|-----|-----|-------|-----|
        | | | | | |

   4.2. Existe ambiente de contingência?
        [ ] Sim
        [ ] Não

5. RESPONSÁVEIS

   | Função | Nome | Email | Telefone |
   |--------|------|-------|----------|
   | Gestor Infraestrutura | | | |
   | Administrador Rede | | | |
   | Segurança da Informação | | | |

└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Ações Preparatórias Recomendadas

### 7.1 Imediatas (antes das instruções ANEEL)

| # | Ação | Responsável | Prazo |
|---|------|-------------|-------|
| 1 | Garantir que todas as views das APIs 1, 2 e 3 estejam funcionando | Todas equipes | Imediato |
| 2 | Criar índices para consultas frequentes | DBAs | 2 semanas |
| 3 | Configurar Materialized Views com refresh frequente | DBAs | 2 semanas |
| 4 | Provisionar capacidade adicional de conexões | Infra/DBAs | 2 semanas |
| 5 | Revisar segurança (firewalls, certificados) | Segurança | 2 semanas |
| 6 | Documentar todas as views disponíveis | Todas equipes | 3 semanas |

### 7.2 Quando Instruções Forem Publicadas

| # | Ação | Responsável | Prazo |
|---|------|-------------|-------|
| 1 | Analisar especificações técnicas | TI RADAR | 1 semana |
| 2 | Identificar gaps e novos requisitos | TI RADAR | 1 semana |
| 3 | Implementar novos endpoints/views | Todas equipes | 4 semanas |
| 4 | Testes e homologação | TI RADAR | 2 semanas |
| 5 | Disponibilização para ANEEL | TI RADAR | Até 60 dias |

---

## 8. Checklist de Preparação

### 8.1 Sistema Técnico

- [ ] Views das APIs 1-3 funcionando
- [ ] Índices otimizados
- [ ] Capacidade de conexões verificada
- [ ] Dados em tempo real confirmados
- [ ] Responsável técnico identificado

### 8.2 Sistema Comercial (Ajuri)

- [ ] Views das APIs 1-3 funcionando
- [ ] Dados cadastrais atualizados
- [ ] Capacidade de conexões verificada
- [ ] Responsável técnico identificado

### 8.3 CRM

- [ ] Views das APIs 2-3 funcionando
- [ ] Todas fontes integradas
- [ ] Capacidade de conexões verificada
- [ ] Responsável técnico identificado

### 8.4 Medição (se aplicável)

- [ ] Sistema identificado
- [ ] Dados disponíveis mapeados
- [ ] Possibilidade de integração avaliada
- [ ] Responsável técnico identificado

### 8.5 Infraestrutura

- [ ] Conectividade externa verificada
- [ ] Certificados SSL válidos
- [ ] Firewall preparado para liberações
- [ ] Monitoramento ativo
- [ ] Capacidade de servidores verificada

---

## 9. Próximos Passos

1. **Preencher todos os formulários** deste documento
2. **Identificar responsáveis** de cada sistema
3. **Executar ações preparatórias** imediatas
4. **Aguardar publicação** das instruções técnicas da ANEEL
5. **Implementar em 60 dias** após publicação

---

## 10. Contatos do Projeto RADAR

| Função | Nome | Email | Telefone |
|--------|------|-------|----------|
| Coordenador | | | |
| Arquiteto | | | |
| DBA | | | |

---

**IMPORTANTE:** Este documento deve ser atualizado assim que a ANEEL publicar as instruções técnicas para a API de tempo real.

---

*Documento gerado em 10/12/2025 - Projeto RADAR - Roraima Energia S/A*
