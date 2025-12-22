# Sistema de Subagentes RADAR

## Visualizacao dos Subagentes por Categoria

### Arquitetura e Desenvolvimento

| Emoji | Agente | Cor | Especialidade | Uso Principal |
|:---:|:---|:---:|:---|:---|
| **backend-architect** | Green | Python/FastAPI/Oracle | Design de APIs, arquitetura backend |
| **database-optimizer** | Orange | Oracle 19c/SQL/DBLink | Queries, indices, DBLinks INSERVICE |
| **test-engineer** | Magenta | TDD/Pytest/Coverage | Testes, cobertura, qualidade |

### Seguranca e Compliance

| Emoji | Agente | Cor | Especialidade | Uso Principal |
|:---:|:---|:---:|:---|:---|
| **security-auditor** | Red | OWASP/API Security | Auth, vulnerabilidades, compliance ANEEL |

### Padroes e Principios (ADRs)

| Emoji | Agente | Cor | Especialidade | Uso Principal |
|:---:|:---|:---:|:---|:---|
| **ddd-expert** | Blue | Domain-Driven Design | Bounded contexts, agregados, eventos |
| **clean-architecture-guardian** | Purple | Clean Architecture | Camadas, dependencias, testabilidade |
| **solid-enforcer** | Yellow | SOLID Principles | SRP, OCP, LSP, ISP, DIP |

## Matriz de Responsabilidades

```
                    +-------------------+
                    |  ddd-expert       |
                    +--------+----------+
                             |
              +--------------+--------------+
              |                             |
    +---------v---------+       +-----------v-----------+
    | clean-architecture|       |   solid-enforcer      |
    +---------+---------+       +-----------+-----------+
              |                             |
              +-------------+---------------+
                            |
              +-------------v--------------+
              |    backend-architect       |
              +-------------+--------------+
                            |
         +------------------+------------------+
         |                  |                  |
+--------v--------+ +-------v-------+ +-------v-------+
| database-optim. | | test-engineer | | security-audit|
+-----------------+ +---------------+ +---------------+
```

## Legenda de Cores

- **Verde** - Backend e APIs (Python/FastAPI)
- **Azul** - DDD e Domain Modeling
- **Orange** - Banco de Dados (Oracle/DBLink)
- **Magenta** - Testes (pytest/TDD)
- **Red** - Seguranca (OWASP/ANEEL)
- **Purple** - Clean Architecture
- **Yellow** - SOLID Principles

## Como Usar os Subagentes

### Invocacao Direta
```bash
# Por nome
@backend-architect como estruturar a API de interrupcoes?
@ddd-expert como modelar a entidade Interrupcao?
@test-engineer criar testes para CodigoIBGE

# Por contexto
/agents backend-architect
/agents list  # Ver todos disponiveis
```

### Invocacao Automatica
Claude detecta o contexto e invoca o agente apropriado automaticamente baseado em:
- Palavras-chave no prompt
- Tipo de tarefa
- Arquivos sendo editados
- Contexto da conversa

### Colaboracao entre Agentes
```bash
# Exemplo de task complexa que usa multiplos agentes
"Implementar endpoint de interrupcoes ativas"

1. @ddd-expert - Modelagem do dominio (Interrupcao, CodigoIBGE)
2. @clean-architecture-guardian - Separacao de camadas
3. @solid-enforcer - Aplicar principios SOLID
4. @backend-architect - Estrutura da API FastAPI
5. @database-optimizer - Query Oracle com DBLink
6. @test-engineer - Criar testes TDD
7. @security-auditor - Implementar autenticacao API Key
```

## Casos de Uso por Subagente

### backend-architect
- Design de novas APIs REST (formato ANEEL)
- Estruturacao de endpoints FastAPI
- Configuracao de middlewares
- Integracao com Oracle via DBLink
- Arquitetura de cache (Memory/Redis)

### database-optimizer
- Otimizacao de queries Oracle
- Configuracao de DBLinks (INSERVICE, INDICADORES)
- Criacao de indices
- Queries de agregacao por municipio/conjunto
- Performance tuning

### test-engineer
- Criacao de testes unitarios (pytest)
- Testes de integracao
- Testes E2E com httpx
- Coverage reports (>= 80%)
- TDD implementation

### security-auditor
- Autenticacao via API Key (x-api-key)
- Rate Limiting (12 req/min ANEEL)
- IP Whitelist
- Validacao de inputs
- Protecao contra SQL Injection

### ddd-expert
- Modelagem de Entidades (Interrupcao)
- Value Objects (CodigoIBGE, TipoInterrupcao)
- Agregados (InterrupcaoAgregada)
- Domain Services
- Result Pattern

### clean-architecture-guardian
- Separacao de camadas (domain > application > infrastructure > interfaces)
- Regra de dependencia (imports para dentro)
- Independencia de frameworks
- Testabilidade
- Ports and adapters (Protocols)

### solid-enforcer
- Single Responsibility (classes pequenas)
- Open/Closed (extensao sem modificacao)
- Liskov Substitution (Protocols)
- Interface Segregation (interfaces especificas)
- Dependency Inversion (injecao de dependencias)

## Workflow Recomendado

```
Requisito --> [Tipo?]
                |
      +---------+---------+
      |         |         |
   Feature     Bug     Security
      |         |         |
      v         v         v
 ddd-expert  test-eng  security-audit
      |         |         |
      +----+----+         |
           |              |
           v              |
  clean-architecture <----+
           |
           v
     [Camada?]
           |
    +------+------+
    |             |
    v             v
 backend-    database-
 architect   optimizer
    |             |
    +------+------+
           |
           v
     test-engineer
           |
           v
       Deploy
```

## Metricas de Uso

| Agente | Frequencia | Contexto Principal |
|:---|:---:|:---|
| backend-architect | Alta | APIs, endpoints |
| test-engineer | Muito Alta | Todos os desenvolvimentos |
| ddd-expert | Media | Novas features de dominio |
| database-optimizer | Media | Performance, queries |
| clean-architecture-guardian | Alta | Code reviews |
| solid-enforcer | Alta | Refatoracoes |
| security-auditor | Media | Features com autenticacao |

## Comandos Rapidos

```bash
# Listar todos os agentes
/agents list

# Invocar agente especifico
/agents backend-architect

# Validar arquitetura
@clean-architecture-guardian validate

# Verificar SOLID
@solid-enforcer check

# Otimizar query
@database-optimizer optimize "SELECT..."

# Criar testes
@test-engineer create-tests

# Analise de seguranca
@security-auditor analyze
```

## Integracao entre Agentes

Os agentes podem e devem colaborar:

1. **DDD + Clean Architecture**: Modelagem respeitando camadas
2. **Backend + Database**: APIs otimizadas com queries eficientes
3. **Security + Backend**: API Key e Rate Limiting integrados
4. **Test + All**: Testes TDD em todas as implementacoes
5. **SOLID + All**: Principios aplicados universalmente

---

**Dica**: Use multiplos agentes para tarefas complexas. Eles foram projetados para trabalhar em conjunto!
