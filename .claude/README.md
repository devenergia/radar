# Claude Code Configuration - Projeto RADAR

Esta pasta contem a configuracao do Claude Code para o projeto RADAR.

## Estrutura

```
.claude/
├── README.md              # Este arquivo
├── settings.json          # Configuracao de hooks (compartilhado)
├── settings.local.json    # Permissoes locais (no .gitignore)
├── commands/              # Slash commands
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
    └── inject_context.py
```

## Slash Commands

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
- Alerta sobre padroes obrigatorios

### PostToolUse (Write/Edit)
- Sugere criacao de testes correspondentes (TDD)
- Lembra de executar lint

### UserPromptSubmit
- Detecta intencao do usuario
- Injeta lembretes sobre padroes relevantes

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

### Interfaces (`backend/**/interfaces/**`)
- Pode importar de todas as camadas
- FastAPI routes e controllers

## Uso dos Comandos

```
/create-entity Interrupcao
/create-value-object CodigoIBGE
/create-usecase GetInterrupcoesAtivas
/run-tests unit
/validate-architecture
```

## Personalizacao

### Adicionar Novo Comando
1. Crie arquivo `.claude/commands/nome-comando.md`
2. Adicione frontmatter com `description` e `allowed-tools`
3. Escreva o prompt em Markdown

### Modificar Hooks
1. Edite `.claude/settings.json` para eventos
2. Modifique scripts em `.claude/hooks/`
