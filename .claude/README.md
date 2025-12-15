# Claude Code Configuration - Projeto RADAR

Esta pasta contem a configuracao do Claude Code para garantir que os padroes de desenvolvimento do projeto RADAR sejam seguidos.

## Estrutura

```
.claude/
├── README.md              # Este arquivo
├── settings.json          # Configuracao de hooks
├── commands/              # Slash commands (user-invoked)
│   ├── create-entity.md
│   ├── create-value-object.md
│   ├── create-usecase.md
│   ├── create-repository.md
│   ├── create-test.md
│   ├── create-endpoint.md
│   ├── review-code.md
│   ├── validate-architecture.md
│   ├── run-tests.md
│   └── commit.md
├── agents/                # Subagents especializados
│   ├── architecture-validator.md  # Valida Clean Architecture
│   ├── tdd-enforcer.md           # Garante TDD
│   ├── ddd-expert.md             # Especialista DDD
│   ├── code-reviewer.md          # Code review completo
│   ├── test-runner.md            # Executa e analisa testes
│   ├── python-expert.md          # Python/FastAPI expert
│   └── security-checker.md       # Verifica vulnerabilidades
├── skills/                # Agent Skills (model-invoked)
│   ├── radar-entity/      # Criacao de Entities DDD
│   ├── radar-value-object/# Criacao de Value Objects
│   ├── radar-usecase/     # Criacao de Use Cases
│   ├── radar-repository/  # Criacao de Repositories
│   ├── radar-test/        # Criacao de Testes TDD
│   ├── radar-endpoint/    # Criacao de Endpoints FastAPI
│   └── radar-review/      # Code Review contra padroes
├── rules/                 # Regras modulares por contexto
│   ├── clean-architecture.md
│   ├── solid-principles.md
│   ├── ddd.md
│   ├── tdd.md
│   ├── clean-code.md
│   └── python-fastapi.md
└── hooks/                 # Scripts de automacao
    ├── validate_python_file.py
    ├── post_write_check.py
    ├── inject_context.py
    └── session_start.py
```

## Subagents Especializados

Subagents sao agentes especializados que o Claude pode invocar para tarefas complexas. Cada um tem ferramentas e conhecimento especifico.

| Subagent | Funcao | Ferramentas |
|----------|--------|-------------|
| `architecture-validator` | Valida Clean Architecture | Read, Grep, Glob |
| `tdd-enforcer` | Garante ciclo TDD | Read, Write, Edit, Glob, Grep |
| `ddd-expert` | Modelagem DDD | Read, Write, Edit, Glob, Grep |
| `code-reviewer` | Review completo | Read, Grep, Glob |
| `test-runner` | Executa testes | Bash, Read, Grep, Glob |
| `python-expert` | Python/FastAPI | Read, Write, Edit, Glob, Grep |
| `security-checker` | Seguranca | Read, Grep, Glob |

### Quando Sao Ativados

- **architecture-validator**: Apos escrever codigo em backend/
- **tdd-enforcer**: Antes de implementar codigo de producao
- **ddd-expert**: Ao criar Entities, VOs, Aggregates
- **code-reviewer**: Antes de commits
- **test-runner**: Ao executar ou analisar testes
- **python-expert**: Para orientacao Python/FastAPI
- **security-checker**: Ao criar endpoints ou queries

## Agent Skills (Ativacao Automatica)

Skills sao capacidades que o Claude ativa **automaticamente** baseado no contexto da conversa.

| Skill | Ativada Quando |
|-------|----------------|
| `radar-entity` | Pede para criar entidade, entity, ou conceito com identidade |
| `radar-value-object` | Pede para criar value object, VO, codigo, tipo |
| `radar-usecase` | Pede para criar use case, caso de uso, funcionalidade |
| `radar-repository` | Pede para criar repositorio, acesso a dados, queries |
| `radar-test` | Pede para criar testes, TDD, pytest, cobertura |
| `radar-endpoint` | Pede para criar endpoint, rota, API REST |
| `radar-review` | Pede para revisar codigo, code review, validar |

### Diferenca entre Skills e Commands

| Aspecto | Skills | Commands |
|---------|--------|----------|
| Ativacao | Automatica (modelo decide) | Manual (usuario digita `/`) |
| Complexidade | Capacidades completas | Prompts simples |
| Descoberta | Por contexto | Por comando explicito |

## Slash Commands (Invocacao Manual)

| Comando | Descricao |
|---------|-----------|
| `/create-entity [Nome]` | Cria uma Entity DDD |
| `/create-value-object [Nome]` | Cria um Value Object imutavel |
| `/create-usecase [Nome]` | Cria um Use Case Clean Architecture |
| `/create-repository [Nome]` | Cria Protocol + Implementacao |
| `/create-test [tipo] [modulo]` | Cria teste TDD (unit/integration/e2e) |
| `/create-endpoint [nome] [metodo] [api]` | Cria endpoint FastAPI completo |
| `/review-code [arquivo]` | Revisa codigo contra padroes |
| `/validate-architecture` | Valida Clean Architecture |
| `/run-tests [tipo]` | Executa testes (unit/all/coverage) |
| `/commit [tipo] [escopo] [msg]` | Cria commit Conventional Commits |

## Hooks Configurados

### PreToolUse (Write/Edit)
- Valida padroes de Clean Architecture
- Verifica imports proibidos por camada
- Alerta sobre padroes obrigatorios (Value Objects imutaveis, etc)

### PostToolUse (Write/Edit)
- Sugere criacao de testes correspondentes (TDD)
- Lembra de executar lint

### UserPromptSubmit
- Detecta intencao do usuario
- Injeta lembretes sobre padroes relevantes
- Sugere comandos disponiveis

### Stop
- Verifica se padroes foram seguidos
- Pode bloquear se Clean Architecture foi violada

### SessionStart
- Mostra status do projeto
- Lista comandos disponiveis
- Lembra padroes obrigatorios

## Regras por Camada

### Domain (`backend/**/domain/**`)
- NAO pode importar de outras camadas
- NAO pode importar frameworks (FastAPI, SQLAlchemy)
- Value Objects: `@dataclass(frozen=True)`
- Entities: `__eq__` e `__hash__` por ID
- Repository: apenas `Protocol`

### Application (`backend/**/application/**`)
- Pode importar de `domain`
- NAO pode importar de `infrastructure` ou `interfaces`
- Use Cases: `async execute() -> Result`

### Infrastructure (`backend/**/infrastructure/**`)
- Pode importar de `domain` e `application`
- Implementacoes concretas de Repositories
- Acesso a banco, cache, servicos externos

### Interfaces (`backend/**/interfaces/**`)
- Pode importar de todas as camadas
- FastAPI routes e controllers
- Pydantic schemas

## Uso

### Iniciar Sessao
Ao iniciar uma sessao, o hook `session_start.py` mostrara:
- Status do projeto (branch, mudancas pendentes)
- Lista de comandos disponiveis
- Lembretes de padroes

### Criar Componentes
Use os comandos de criacao para garantir estrutura correta:
```
/create-entity Interrupcao
/create-value-object CodigoIBGE
/create-usecase GetInterrupcoesAtivas
```

### Revisar Codigo
```
/review-code backend/shared/domain/entities/interrupcao.py
/validate-architecture
```

### Executar Testes
```
/run-tests unit
/run-tests coverage
```

## Personalizacao

### Adicionar Novo Comando
1. Crie arquivo `.claude/commands/nome-comando.md`
2. Adicione frontmatter com `description` e `allowed-tools`
3. Escreva o prompt em Markdown

### Modificar Hooks
1. Edite `.claude/settings.json` para eventos
2. Modifique scripts em `.claude/hooks/`
3. Reinicie sessao para aplicar mudancas

## Referencias

- [Claude Code Docs - Skills](https://code.claude.com/docs/en/skills)
- [Claude Code Docs - Hooks](https://code.claude.com/docs/en/hooks)
- [Claude Code Docs - Commands](https://code.claude.com/docs/en/slash-commands)
- [Claude Code Docs - Memory](https://code.claude.com/docs/en/memory)
