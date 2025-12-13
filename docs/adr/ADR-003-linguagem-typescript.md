# ADR-003: TypeScript como Linguagem Principal

## Status

Aceito

## Data

2025-12-12

## Contexto

Precisamos escolher a linguagem de programação para desenvolver a API RADAR. Requisitos:

1. Boa integração com Oracle Database
2. Performance adequada para API de tempo real
3. Tipagem para evitar erros em tempo de execução
4. Ecossistema maduro para desenvolvimento de APIs
5. Facilidade de manutenção e onboarding de novos desenvolvedores

## Decisão

Utilizaremos **TypeScript** como linguagem principal do projeto.

### Versão

- TypeScript: ^5.3.0
- Node.js: ^20.x LTS
- Target: ES2022

### Configuração Base (tsconfig.json)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "paths": {
      "@domain/*": ["./src/domain/*"],
      "@application/*": ["./src/application/*"],
      "@infrastructure/*": ["./src/infrastructure/*"],
      "@interfaces/*": ["./src/interfaces/*"],
      "@shared/*": ["./src/shared/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### Convenções de Código

- **Naming**: camelCase para variáveis/funções, PascalCase para classes/interfaces/types
- **Arquivos**: kebab-case para nomes de arquivos
- **Exports**: Named exports preferidos sobre default exports
- **Interfaces**: Prefixo `I` não usado (ex: `InterrupcaoRepository`, não `IInterrupcaoRepository`)

## Consequências

### Positivas

- **Type Safety**: Erros detectados em tempo de compilação
- **IntelliSense**: Autocomplete e documentação inline nas IDEs
- **Refactoring**: Renomeações e refatorações seguras
- **Documentação**: Tipos servem como documentação viva
- **Ecossistema**: Vasto ecossistema npm com tipagens (@types/*)
- **Onboarding**: Muitos desenvolvedores conhecem TypeScript/JavaScript

### Negativas

- **Build Step**: Necessidade de compilar antes de executar
- **Complexidade**: Tipos avançados podem ser complexos
- **Overhead**: Tempo adicional para definir tipos corretamente

### Neutras

- Necessidade de manter tipagens atualizadas
- Curva de aprendizado para recursos avançados do TS

## Alternativas Consideradas

### Alternativa 1: Java com Spring Boot

Framework enterprise consolidado.

**Rejeitado porque**: Mais verboso, maior consumo de recursos, equipe tem mais experiência com TypeScript/Node.js.

### Alternativa 2: Python com FastAPI

Framework moderno com tipagem opcional.

**Rejeitado porque**: Tipagem não é obrigatória (pode ser ignorada), menor performance que Node.js para I/O intensivo, driver Oracle menos maduro.

### Alternativa 3: JavaScript Puro

Sem compilação, direto no Node.js.

**Rejeitado porque**: Sem type safety, mais propenso a erros em runtime, dificulta manutenção de código grande.

### Alternativa 4: Go

Linguagem compilada de alta performance.

**Rejeitado porque**: Menor ecossistema para APIs REST, driver Oracle menos maduro, curva de aprendizado maior para a equipe.

## Referências

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [Node.js with TypeScript](https://nodejs.org/en/learn/getting-started/nodejs-with-typescript)
