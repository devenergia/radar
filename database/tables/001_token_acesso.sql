-- ============================================================================
-- Tabela: TOKEN_ACESSO
-- Schema: RADAR_API
-- Descricao: Gerenciamento de API Keys para autenticacao ANEEL
-- Fonte: Adaptado de RADAR_ANEEL.TOKEN_ACESSO (radar-backend)
-- Data: 2025-12-19
-- ============================================================================

-- ============================================================================
-- Criacao da Tabela
-- ============================================================================
CREATE TABLE RADAR_API.TOKEN_ACESSO (
    ID                  VARCHAR2(100)   NOT NULL,
    NOME                VARCHAR2(300)   NOT NULL,
    DESCRICAO           VARCHAR2(500)   NULL,
    CHAVE               VARCHAR2(100)   NOT NULL,
    ATIVO               CHAR(1)         DEFAULT 'S' NOT NULL,
    DATA_CRIACAO        DATE            DEFAULT SYSDATE NOT NULL,
    DATA_EXPIRACAO      DATE            NULL,
    ULTIMO_ACESSO       DATE            NULL,
    TOTAL_ACESSOS       NUMBER          DEFAULT 0 NOT NULL,
    IP_ORIGEM_PERMITIDO VARCHAR2(500)   NULL,

    -- Constraints
    CONSTRAINT TOKEN_ACESSO_PK PRIMARY KEY (ID),
    CONSTRAINT TOKEN_ACESSO_CHAVE_UK UNIQUE (CHAVE),
    CONSTRAINT TOKEN_ACESSO_ATIVO_CK CHECK (ATIVO IN ('S', 'N'))
);

-- ============================================================================
-- Indices
-- ============================================================================
CREATE INDEX RADAR_API.IDX_TOKEN_ACESSO_CHAVE ON RADAR_API.TOKEN_ACESSO(CHAVE);
CREATE INDEX RADAR_API.IDX_TOKEN_ACESSO_ATIVO ON RADAR_API.TOKEN_ACESSO(ATIVO);

-- ============================================================================
-- Comentarios
-- ============================================================================
COMMENT ON TABLE RADAR_API.TOKEN_ACESSO IS
    'Tabela de gerenciamento de API Keys para autenticacao ANEEL';

COMMENT ON COLUMN RADAR_API.TOKEN_ACESSO.ID IS
    'Identificador unico do token (UUID)';

COMMENT ON COLUMN RADAR_API.TOKEN_ACESSO.NOME IS
    'Nome descritivo do cliente/sistema (ex: ANEEL-PRODUCAO)';

COMMENT ON COLUMN RADAR_API.TOKEN_ACESSO.DESCRICAO IS
    'Descricao detalhada do proposito do token';

COMMENT ON COLUMN RADAR_API.TOKEN_ACESSO.CHAVE IS
    'API Key para autenticacao via header x-api-key';

COMMENT ON COLUMN RADAR_API.TOKEN_ACESSO.ATIVO IS
    'Flag indicando se o token esta ativo (S/N)';

COMMENT ON COLUMN RADAR_API.TOKEN_ACESSO.DATA_CRIACAO IS
    'Data de criacao do token';

COMMENT ON COLUMN RADAR_API.TOKEN_ACESSO.DATA_EXPIRACAO IS
    'Data de expiracao do token (NULL = sem expiracao)';

COMMENT ON COLUMN RADAR_API.TOKEN_ACESSO.ULTIMO_ACESSO IS
    'Data/hora do ultimo acesso com este token';

COMMENT ON COLUMN RADAR_API.TOKEN_ACESSO.TOTAL_ACESSOS IS
    'Contador de acessos realizados com este token';

COMMENT ON COLUMN RADAR_API.TOKEN_ACESSO.IP_ORIGEM_PERMITIDO IS
    'Lista de IPs permitidos (separados por virgula), NULL = todos';

-- ============================================================================
-- Dados Iniciais (Token ANEEL de Producao)
-- ============================================================================
-- IMPORTANTE: Alterar a CHAVE antes de usar em producao!
INSERT INTO RADAR_API.TOKEN_ACESSO (
    ID,
    NOME,
    DESCRICAO,
    CHAVE,
    ATIVO,
    IP_ORIGEM_PERMITIDO
) VALUES (
    SYS_GUID(),
    'ANEEL-PRODUCAO',
    'Token de producao para consultas da ANEEL',
    'ALTERAR_ESTA_CHAVE_ANTES_DE_PRODUCAO',
    'S',
    NULL  -- Configurar IPs da ANEEL quando disponivel
);

COMMIT;

-- ============================================================================
-- Grants
-- ============================================================================
-- GRANT SELECT, INSERT, UPDATE ON RADAR_API.TOKEN_ACESSO TO RADAR_APP;
