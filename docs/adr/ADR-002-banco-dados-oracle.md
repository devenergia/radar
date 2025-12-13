# ADR-002: Banco de Dados Oracle com DBLinks

## Status

Aceito

## Data

2025-12-12

## Contexto

O Projeto RADAR precisa consultar dados de múltiplos sistemas fonte:

1. **INSERVICE**: Sistema técnico com eventos de interrupção, equipes, dispositivos
2. **INDICADORES**: Tabela com códigos IBGE dos municípios
3. **AJURI** (futuro): Sistema comercial para outras APIs

Esses sistemas já possuem bancos Oracle em produção. A Roraima Energia possui infraestrutura Oracle estabelecida.

## Decisão

Criaremos um **banco de dados Oracle dedicado para o RADAR** que utilizará **DBLinks** para acessar os sistemas fonte.

### Arquitetura de Dados

```
┌─────────────────────────────────────────────────────────────────┐
│                     BANCO RADAR (Principal)                      │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │  Tabelas RADAR   │  │    Views RADAR   │  │    DBLinks    │  │
│  │  (histórico,     │  │  (agregações)    │  │               │  │
│  │   cache, logs)   │  │                  │  │               │  │
│  └──────────────────┘  └──────────────────┘  └───────┬───────┘  │
│                                                      │          │
└──────────────────────────────────────────────────────┼──────────┘
                                                       │
           ┌───────────────────────────────────────────┼───────────┐
           │                                           │           │
           ▼                                           ▼           ▼
┌──────────────────┐              ┌──────────────────┐    ┌───────────────┐
│    INSERVICE     │              │   INDICADORES    │    │     AJURI     │
│                  │              │                  │    │   (futuro)    │
│ AGENCY_EVENT     │              │ IND_UNIVERSOS    │    │               │
│ SWITCH_PLAN_TASKS│              │                  │    │               │
│ OMS_CONNECTIVITY │              │                  │    │               │
│ CONSUMIDORES_... │              │                  │    │               │
└──────────────────┘              └──────────────────┘    └───────────────┘
```

### Configuração dos DBLinks

```sql
-- Criar DBLink para Inservice
CREATE DATABASE LINK INSERVICE_LINK
CONNECT TO radar_readonly IDENTIFIED BY "****"
USING 'INSERVICE_TNS';

-- Criar DBLink para Indicadores
CREATE DATABASE LINK INDICADORES_LINK
CONNECT TO radar_readonly IDENTIFIED BY "****"
USING 'INDICADORES_TNS';

-- Criar sinônimos para facilitar acesso
CREATE SYNONYM AGENCY_EVENT FOR INSERVICE.AGENCY_EVENT@INSERVICE_LINK;
CREATE SYNONYM IND_UNIVERSOS FOR INDICADORES.IND_UNIVERSOS@INDICADORES_LINK;
```

### Usuário da Aplicação

```sql
-- Criar usuário para a API RADAR
CREATE USER radar_api IDENTIFIED BY "****"
DEFAULT TABLESPACE radar_data
QUOTA UNLIMITED ON radar_data;

-- Conceder permissões
GRANT CREATE SESSION TO radar_api;
GRANT SELECT ON schema.tabela TO radar_api;
```

## Consequências

### Positivas

- **Acesso Direto**: Dados em tempo real dos sistemas fonte
- **Sem Replicação**: Não precisa sincronizar dados entre bancos
- **Transações Distribuídas**: Oracle gerencia transações entre DBLinks
- **Infraestrutura Existente**: Aproveita expertise Oracle da equipe
- **Performance**: Oracle otimiza queries distribuídas

### Negativas

- **Dependência de Rede**: Falha de rede afeta disponibilidade
- **Acoplamento**: Mudanças nos sistemas fonte podem afetar RADAR
- **Complexidade de Debug**: Queries distribuídas mais difíceis de debugar
- **Licenciamento**: Pode haver custos adicionais de licença Oracle

### Neutras

- Necessidade de monitorar latência dos DBLinks
- Queries devem ser otimizadas para minimizar round-trips

## Mitigações

1. **Cache Local**: Implementar cache em memória para reduzir consultas
2. **Circuit Breaker**: Implementar fallback quando DBLink estiver indisponível
3. **Monitoring**: Alertas para latência elevada nos DBLinks
4. **Retry**: Implementar retry com backoff exponencial

## Alternativas Consideradas

### Alternativa 1: Replicação de Dados (ETL)

Copiar dados dos sistemas fonte para o banco RADAR periodicamente.

**Rejeitado porque**: Dados não seriam em tempo real, complexidade de manutenção do ETL, possível inconsistência.

### Alternativa 2: APIs Internas

Cada sistema fonte expõe uma API interna que o RADAR consome.

**Rejeitado porque**: Os sistemas fonte (Inservice) não possuem APIs, seria necessário desenvolvimento adicional significativo.

### Alternativa 3: Banco PostgreSQL

Usar PostgreSQL com Foreign Data Wrappers para Oracle.

**Rejeitado porque**: Infraestrutura existente é Oracle, FDW adiciona camada de complexidade, equipe não tem expertise em PostgreSQL.

## Referências

- Oracle Database Links Documentation
- Oracle Distributed Database Concepts
