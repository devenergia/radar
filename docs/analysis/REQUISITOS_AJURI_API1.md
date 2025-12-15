# Requisitos para Sistema Comercial (Ajuri)
## API 1 - Quantitativo de Interrupções Ativas

**Projeto:** RADAR - Rede de Acompanhamento e Diagnóstico da Distribuição
**Base Legal:** Ofício Circular nº 14/2025-SFE/ANEEL V4
**Prazo:** Dezembro/2025
**Data do Documento:** Dezembro/2025
**Última Atualização:** Dezembro/2025

---

## STATUS: NÃO NECESSÁRIO PARA API 1

A integração com o **Sistema Comercial (Ajuri)** **não é mais necessária** para a implementação da **API 1 - Quantitativo de Interrupções Ativas**.

---

## 1. Justificativa

Anteriormente, o Sistema Ajuri seria responsável por fornecer:

1. ~~**VW_MUNICIPIOS_IBGE_RADAR**~~ - Mapeamento de códigos locais para códigos IBGE
2. ~~**VW_UCS_CONJUNTO_MUNICIPIO_RADAR**~~ - Total de UCs por conjunto/município

### 1.1 Nova Fonte de Dados

Após análise detalhada, foram identificadas fontes de dados alternativas no Sistema Técnico:

| Dado | Fonte Anterior (Ajuri) | Nova Fonte |
|------|------------------------|------------|
| **Código IBGE** | `VW_MUNICIPIOS_IBGE_RADAR` | `INDICADORES.IND_UNIVERSOS` (campo `CD_UNIVERSO`) |
| **UCs Atingidas** | Contagem de UCs | `INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW` ou `AGENCY_EVENT.NUM_CUST` |

---

## 2. Como o Código IBGE é Obtido Agora

O código IBGE do município é obtido diretamente da tabela `INDICADORES.IND_UNIVERSOS`:

```sql
-- JOIN para obter código IBGE do município
JOIN INDICADORES.IND_UNIVERSOS u
    ON u.ID_DISPOSITIVO = a.dev_id
    AND u.CD_TIPO_UNIVERSO = 2

-- O campo CD_UNIVERSO já contém o código IBGE de 7 dígitos
```

| Campo | Descrição |
|-------|-----------|
| `ID_DISPOSITIVO` | Chave para JOIN com `AGENCY_EVENT.dev_id` |
| `CD_UNIVERSO` | Código IBGE do município (7 dígitos) |
| `CD_TIPO_UNIVERSO` | Filtro = 2 (para município) |

---

## 3. Como as UCs Atingidas são Obtidas Agora

As UCs atingidas por evento são obtidas de duas formas:

### 3.1 Quantidade Total (campo direto)

```sql
-- Campo NUM_CUST da tabela AGENCY_EVENT
SELECT NUM_CUST AS qtd_ucs_afetadas
FROM INSERVICE.AGENCY_EVENT
WHERE num_1 = :id_evento;
```

### 3.2 Lista Detalhada de UCs

```sql
-- View CONSUMIDORES_ATINGIDOS_VIEW
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

## 4. Impacto na Documentação

Os seguintes requisitos foram **removidos** do escopo do Ajuri para a API 1:

| Requisito Original | Status |
|--------------------|--------|
| Criar `VW_MUNICIPIOS_IBGE_RADAR` | **CANCELADO** - Não necessário |
| Criar `VW_UCS_CONJUNTO_MUNICIPIO_RADAR` | **CANCELADO** - Não necessário |
| Conceder permissões ao INSERVICE | **CANCELADO** - Não necessário |
| Conceder permissões ao RADAR_API | **CANCELADO** - Não necessário |

---

## 5. APIs Futuras

O Sistema Ajuri **poderá ser necessário** para outras APIs do Projeto RADAR, como:

- **API 2** - Dados de Demanda
- **API 3** - Quantitativo de Demandas Diversas

Para essas APIs, os requisitos serão especificados em documentos separados.

---

## 6. Arquitetura Atual da API 1

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARQUITETURA API 1 - SEM AJURI                             │
└─────────────────────────────────────────────────────────────────────────────┘

           ┌──────────────────────────────────────────────────────┐
           │                 SISTEMA TÉCNICO                       │
           │           (INSERVICE + INDICADORES)                   │
           └──────────────────────────────────────────────────────┘
                    │                           │
                    ▼                           ▼
        ┌───────────────────────┐   ┌───────────────────────┐
        │ INSERVICE             │   │ INDICADORES           │
        │                       │   │                       │
        │ AGENCY_EVENT          │   │ IND_UNIVERSOS         │
        │ SWITCH_PLAN_TASKS     │   │ (Código IBGE)         │
        │ OMS_CONNECTIVITY      │   │                       │
        │ CONSUMIDORES_ATINGIDOS│   │                       │
        └───────────────────────┘   └───────────────────────┘
                    │                           │
                    └───────────┬───────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      API RADAR        │
                    │ /quantitativointerrup │
                    │ coesativas            │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │        ANEEL          │
                    └───────────────────────┘


    ┌───────────────────────────────────────────────────────────┐
    │                                                           │
    │   ╔═══════════════════════════════════════════════════╗   │
    │   ║  SISTEMA AJURI - NÃO NECESSÁRIO PARA API 1        ║   │
    │   ╚═══════════════════════════════════════════════════╝   │
    │                                                           │
    └───────────────────────────────────────────────────────────┘
```

---

## 7. Resumo

| Item | Status |
|------|--------|
| **Integração com Ajuri para API 1** | NÃO NECESSÁRIA |
| **Código IBGE** | Obtido de `INDICADORES.IND_UNIVERSOS` |
| **UCs Atingidas** | Obtido de `INSERVICE.CONSUMIDORES_ATINGIDOS_VIEW` |
| **Views do Ajuri** | NÃO precisam ser criadas para API 1 |

---

## 8. Contatos

Para dúvidas sobre esta atualização, entrar em contato com a equipe do Projeto RADAR:

| Função | Contato |
|--------|---------|
| Coordenação do Projeto | [A definir] |
| Equipe de Desenvolvimento API | ti.radar@roraimaenergia.com.br |

---

*Documento atualizado em Dezembro/2025 - Projeto RADAR - Roraima Energia S/A*
