# Guia de Configuração DBLink - Oracle SISTEC

## 1. Visão Geral

Este documento descreve a configuração e manutenção do DBLink utilizado pela API RADAR para acessar dados de interrupções no sistema SISTEC (Sistema Técnico da Roraima Energia).

## 2. Arquitetura de Conexão

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Fluxo de Dados via DBLink                            │
│                                                                              │
│  ┌──────────────────┐        ┌──────────────────┐        ┌────────────────┐ │
│  │    API RADAR     │        │   Oracle RADAR   │        │  Oracle SISTEC │ │
│  │   (FastAPI)      │───────>│   (Banco Local)  │───────>│  (Fonte)       │ │
│  │                  │ SQL    │                  │ DBLink │                │ │
│  │                  │        │  DBLINK_SISTEC   │        │ VW_INTERRUP... │ │
│  └──────────────────┘        └──────────────────┘        └────────────────┘ │
│                                                                              │
│  Network: RADAR -> Oracle Net (1521) -> RADAR DB -> DBLink -> SISTEC DB     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3. Pré-requisitos

### 3.1 Conectividade de Rede

| Origem | Destino | Porta | Protocolo |
|--------|---------|-------|-----------|
| Oracle RADAR | Oracle SISTEC | 1521 | Oracle Net |

### 3.2 Permissões Necessárias

**No banco RADAR:**
- `CREATE DATABASE LINK` privilege para o usuário que criará o DBLink
- Ou `CREATE PUBLIC DATABASE LINK` para DBLink público

**No banco SISTEC:**
- Usuário de serviço com permissões de leitura nas views/tabelas necessárias

## 4. Configuração do TNS

### 4.1 Arquivo tnsnames.ora

```
# $ORACLE_HOME/network/admin/tnsnames.ora

# Entrada para o banco SISTEC
SISTEC.RORAIMAENERGIA.COM.BR =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = sistec-db.roraimaenergia.com.br)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = SISTEC)
    )
  )

# Entrada alternativa com failover
SISTEC_HA =
  (DESCRIPTION =
    (ADDRESS_LIST =
      (ADDRESS = (PROTOCOL = TCP)(HOST = sistec-db-primary.roraimaenergia.com.br)(PORT = 1521))
      (ADDRESS = (PROTOCOL = TCP)(HOST = sistec-db-standby.roraimaenergia.com.br)(PORT = 1521))
    )
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = SISTEC)
      (FAILOVER_MODE =
        (TYPE = SELECT)
        (METHOD = BASIC)
        (RETRIES = 3)
        (DELAY = 5)
      )
    )
  )
```

### 4.2 Verificação de Conectividade

```bash
# Testar resolução do TNS
tnsping SISTEC.RORAIMAENERGIA.COM.BR

# Output esperado:
# OK (10 msec)

# Testar conexão direta
sqlplus radar_sistec/password@SISTEC.RORAIMAENERGIA.COM.BR
```

## 5. Criação do DBLink

### 5.1 DBLink Privado (Recomendado)

```sql
-- Conectar como o usuário que usará o DBLink
CONNECT radar/password@RADAR;

-- Criar DBLink privado
CREATE DATABASE LINK DBLINK_SISTEC
CONNECT TO radar_sistec IDENTIFIED BY "SenhaSegura123!"
USING 'SISTEC.RORAIMAENERGIA.COM.BR';

-- Verificar criação
SELECT db_link, username, host, created
FROM user_db_links
WHERE db_link = 'DBLINK_SISTEC';
```

### 5.2 DBLink Público (Quando necessário)

```sql
-- Conectar como DBA
CONNECT sys/password@RADAR AS SYSDBA;

-- Criar DBLink público
CREATE PUBLIC DATABASE LINK DBLINK_SISTEC
CONNECT TO radar_sistec IDENTIFIED BY "SenhaSegura123!"
USING 'SISTEC.RORAIMAENERGIA.COM.BR';

-- Verificar criação
SELECT db_link, owner, username, host, created
FROM dba_db_links
WHERE db_link = 'DBLINK_SISTEC';
```

### 5.3 Testar DBLink

```sql
-- Teste simples
SELECT * FROM DUAL@DBLINK_SISTEC;

-- Teste de conectividade com tabela real
SELECT COUNT(*) FROM SISTEC.VW_INTERRUPCOES_ATIVAS@DBLINK_SISTEC;

-- Verificar usuário conectado
SELECT USER FROM DUAL@DBLINK_SISTEC;
```

## 6. Configuração de Segurança

### 6.1 Oracle Wallet (Recomendado para Produção)

```bash
# 1. Criar diretório do wallet
mkdir -p $ORACLE_BASE/admin/RADAR/wallet

# 2. Criar wallet
mkstore -wrl $ORACLE_BASE/admin/RADAR/wallet -create

# 3. Adicionar credenciais
mkstore -wrl $ORACLE_BASE/admin/RADAR/wallet \
  -createCredential SISTEC.RORAIMAENERGIA.COM.BR radar_sistec SenhaSegura123!
```

### 6.2 Configurar sqlnet.ora para Wallet

```
# $ORACLE_HOME/network/admin/sqlnet.ora

WALLET_LOCATION =
  (SOURCE =
    (METHOD = FILE)
    (METHOD_DATA =
      (DIRECTORY = /u01/app/oracle/admin/RADAR/wallet)
    )
  )

SQLNET.WALLET_OVERRIDE = TRUE
```

### 6.3 Criar DBLink com Wallet

```sql
-- DBLink usando credenciais do wallet
CREATE DATABASE LINK DBLINK_SISTEC
CONNECT TO radar_sistec
IDENTIFIED BY VALUES ':1'
USING 'SISTEC.RORAIMAENERGIA.COM.BR';
```

## 7. Views e Objetos Remotos

### 7.1 View de Interrupções (SISTEC)

```sql
-- Estrutura esperada da view no SISTEC
CREATE OR REPLACE VIEW SISTEC.VW_INTERRUPCOES_ATIVAS AS
SELECT
    i.ID_INTERRUPCAO,
    m.CODIGO_IBGE,
    m.NOME_MUNICIPIO,
    i.TIPO_INTERRUPCAO,  -- 1=Programada, 2=Não Programada
    i.DATA_INICIO,
    i.DATA_FIM_PREVISTO,
    i.CAUSA,
    i.QTD_UCS_AFETADAS,
    i.QTD_EQUIPES_ATENDIMENTO,
    i.DATA_ATUALIZACAO
FROM
    SISTEC.TB_INTERRUPCOES i
    INNER JOIN SISTEC.TB_MUNICIPIOS m ON i.ID_MUNICIPIO = m.ID_MUNICIPIO
WHERE
    i.STATUS = 'ATIVA'
    AND i.DATA_FIM IS NULL;

-- Grants necessários
GRANT SELECT ON SISTEC.VW_INTERRUPCOES_ATIVAS TO radar_sistec;
```

### 7.2 Query Utilizada pela API

```sql
-- Query executada pelo OracleInterrupcaoRepository
SELECT
    CODIGO_IBGE as ideMunicipio,
    TIPO_INTERRUPCAO as idcTipoInterrupcao,
    COUNT(*) as qtdInterrupcoes,
    SUM(QTD_UCS_AFETADAS) as qtdUcsInterrompidas,
    SUM(QTD_EQUIPES_ATENDIMENTO) as qtdEquipesDeslocamento,
    TO_CHAR(MAX(DATA_ATUALIZACAO), 'DD/MM/YYYY HH24:MI') as dthUltRecuperacao
FROM
    SISTEC.VW_INTERRUPCOES_ATIVAS@DBLINK_SISTEC
GROUP BY
    CODIGO_IBGE,
    TIPO_INTERRUPCAO
ORDER BY
    CODIGO_IBGE,
    TIPO_INTERRUPCAO;
```

## 8. Otimização de Performance

### 8.1 Hints para Queries Remotas

```sql
-- Forçar execução no site remoto
SELECT /*+ DRIVING_SITE(v) */
    CODIGO_IBGE,
    TIPO_INTERRUPCAO,
    COUNT(*)
FROM
    SISTEC.VW_INTERRUPCOES_ATIVAS@DBLINK_SISTEC v
GROUP BY
    CODIGO_IBGE,
    TIPO_INTERRUPCAO;
```

### 8.2 Materialized View (Alternativa para Alta Performance)

```sql
-- Criar Materialized View Log no SISTEC (se permitido)
CREATE MATERIALIZED VIEW LOG ON SISTEC.VW_INTERRUPCOES_ATIVAS
WITH PRIMARY KEY, ROWID
INCLUDING NEW VALUES;

-- Criar Materialized View no RADAR
CREATE MATERIALIZED VIEW MV_INTERRUPCOES_ATIVAS
BUILD IMMEDIATE
REFRESH FAST ON DEMAND
AS
SELECT *
FROM SISTEC.VW_INTERRUPCOES_ATIVAS@DBLINK_SISTEC;

-- Job para refresh
BEGIN
    DBMS_SCHEDULER.CREATE_JOB(
        job_name        => 'REFRESH_MV_INTERRUPCOES',
        job_type        => 'PLSQL_BLOCK',
        job_action      => 'BEGIN DBMS_MVIEW.REFRESH(''MV_INTERRUPCOES_ATIVAS'', ''F''); END;',
        start_date      => SYSTIMESTAMP,
        repeat_interval => 'FREQ=MINUTELY; INTERVAL=5',
        enabled         => TRUE
    );
END;
/
```

### 8.3 Parâmetros de Otimização

```sql
-- Verificar parâmetros atuais
SHOW PARAMETER db_link;
SHOW PARAMETER open_links;
SHOW PARAMETER global_names;

-- Ajustar se necessário (como DBA)
ALTER SYSTEM SET open_links=10 SCOPE=SPFILE;
ALTER SYSTEM SET open_links_per_instance=10 SCOPE=SPFILE;
```

## 9. Monitoramento

### 9.1 Verificar Status do DBLink

```sql
-- Listar DBLinks
SELECT db_link, username, host, created
FROM user_db_links;

-- Verificar se conexão está ativa
SELECT
    'DBLINK_SISTEC' as dblink,
    CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'FAIL' END as status
FROM DUAL@DBLINK_SISTEC;
```

### 9.2 Monitorar Uso

```sql
-- Sessões via DBLink
SELECT
    s.sid,
    s.serial#,
    s.username,
    d.db_link,
    d.owner_id,
    d.logged_on,
    d.open_cursors
FROM
    v$dblink d
    JOIN v$session s ON d.owner_id = s.saddr;

-- Performance de queries distribuídas
SELECT
    sql_text,
    executions,
    elapsed_time/1000000 as elapsed_secs,
    rows_processed
FROM
    v$sql
WHERE
    sql_text LIKE '%DBLINK_SISTEC%'
ORDER BY
    elapsed_time DESC;
```

### 9.3 Script de Health Check

```sql
-- health_check_dblink.sql
SET SERVEROUTPUT ON;
DECLARE
    v_count NUMBER;
    v_start TIMESTAMP;
    v_elapsed NUMBER;
BEGIN
    v_start := SYSTIMESTAMP;

    BEGIN
        SELECT COUNT(*) INTO v_count
        FROM SISTEC.VW_INTERRUPCOES_ATIVAS@DBLINK_SISTEC;

        v_elapsed := EXTRACT(SECOND FROM (SYSTIMESTAMP - v_start)) * 1000;

        DBMS_OUTPUT.PUT_LINE('Status: OK');
        DBMS_OUTPUT.PUT_LINE('Records: ' || v_count);
        DBMS_OUTPUT.PUT_LINE('Time (ms): ' || v_elapsed);

    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Status: FAIL');
            DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
    END;
END;
/
```

## 10. Troubleshooting

### 10.1 Erros Comuns

#### ORA-02019: connection description for remote database not found

**Causa**: TNS entry não encontrada

**Solução**:
```bash
# Verificar tnsnames.ora
cat $ORACLE_HOME/network/admin/tnsnames.ora | grep -A5 SISTEC

# Testar TNS
tnsping SISTEC.RORAIMAENERGIA.COM.BR

# Verificar variável de ambiente
echo $TNS_ADMIN
```

#### ORA-01017: invalid username/password; logon denied

**Causa**: Credenciais inválidas no DBLink

**Solução**:
```sql
-- Recriar DBLink com credenciais corretas
DROP DATABASE LINK DBLINK_SISTEC;

CREATE DATABASE LINK DBLINK_SISTEC
CONNECT TO radar_sistec IDENTIFIED BY "NovaSenha123!"
USING 'SISTEC.RORAIMAENERGIA.COM.BR';
```

#### ORA-12170: TNS:Connect timeout occurred

**Causa**: Problemas de rede ou firewall

**Solução**:
```bash
# Testar conectividade de rede
telnet sistec-db.roraimaenergia.com.br 1521

# Verificar firewall
iptables -L -n | grep 1521

# Aumentar timeout no sqlnet.ora
# SQLNET.INBOUND_CONNECT_TIMEOUT=180
```

#### ORA-02068: following severe error from [dblink]

**Causa**: Problema no banco remoto

**Solução**:
```sql
-- Verificar status do banco remoto
SELECT status FROM v$instance@DBLINK_SISTEC;

-- Verificar espaço em tablespace remoto
SELECT tablespace_name, status
FROM dba_tablespaces@DBLINK_SISTEC;
```

### 10.2 Diagnóstico de Performance

```sql
-- Trace de queries distribuídas
ALTER SESSION SET EVENTS '10046 trace name context forever, level 12';

-- Executar query problemática
SELECT * FROM SISTEC.VW_INTERRUPCOES_ATIVAS@DBLINK_SISTEC WHERE ROWNUM < 10;

ALTER SESSION SET EVENTS '10046 trace name context off';

-- Analisar trace file
-- tkprof tracefile.trc output.txt explain=radar/password
```

## 11. Backup e Recovery

### 11.1 Backup da Configuração

```bash
#!/bin/bash
# backup_dblink_config.sh

BACKUP_DIR="/backup/oracle/dblink/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup tnsnames.ora
cp $ORACLE_HOME/network/admin/tnsnames.ora $BACKUP_DIR/

# Backup sqlnet.ora
cp $ORACLE_HOME/network/admin/sqlnet.ora $BACKUP_DIR/

# Export DBLink DDL
sqlplus -S radar/password@RADAR << EOF > $BACKUP_DIR/dblink_ddl.sql
SET LONG 10000
SELECT DBMS_METADATA.GET_DDL('DB_LINK', 'DBLINK_SISTEC') FROM DUAL;
EOF

echo "Backup completed: $BACKUP_DIR"
```

### 11.2 Procedimento de Recovery

```sql
-- 1. Verificar backup
SELECT * FROM user_db_links;

-- 2. Dropar DBLink corrompido
DROP DATABASE LINK DBLINK_SISTEC;

-- 3. Recriar a partir do backup
@/backup/oracle/dblink/20251210/dblink_ddl.sql

-- 4. Testar
SELECT * FROM DUAL@DBLINK_SISTEC;
```

## 12. Manutenção

### 12.1 Rotina de Verificação Diária

```sql
-- daily_check.sql
PROMPT === DBLink Daily Check ===
PROMPT

PROMPT 1. DBLink Status:
SELECT db_link, username, host FROM user_db_links;

PROMPT 2. Connection Test:
SELECT 'OK' as status FROM DUAL@DBLINK_SISTEC;

PROMPT 3. Data Count:
SELECT COUNT(*) as interrupcoes_ativas
FROM SISTEC.VW_INTERRUPCOES_ATIVAS@DBLINK_SISTEC;

PROMPT 4. Last Update:
SELECT MAX(DATA_ATUALIZACAO) as ultima_atualizacao
FROM SISTEC.VW_INTERRUPCOES_ATIVAS@DBLINK_SISTEC;
```

### 12.2 Rotação de Senhas

```sql
-- 1. Criar novo DBLink com nova senha
CREATE DATABASE LINK DBLINK_SISTEC_NEW
CONNECT TO radar_sistec IDENTIFIED BY "NovaSenha456!"
USING 'SISTEC.RORAIMAENERGIA.COM.BR';

-- 2. Testar novo DBLink
SELECT * FROM DUAL@DBLINK_SISTEC_NEW;

-- 3. Dropar DBLink antigo
DROP DATABASE LINK DBLINK_SISTEC;

-- 4. Renomear novo DBLink (não suportado diretamente)
-- Criar sinônimo ou atualizar aplicação
```

## 13. Referências

- [Oracle Database Link Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/admin/managing-a-distributed-database.html)
- [Oracle Net Services Configuration](https://docs.oracle.com/en/database/oracle/oracle-database/19/netag/)
- [Oracle Wallet Manager](https://docs.oracle.com/en/database/oracle/oracle-database/19/dbseg/managing-security-for-oracle-database-users.html)
