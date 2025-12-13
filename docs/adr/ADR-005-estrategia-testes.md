# ADR-005: Estratégia de Testes (TDD)

## Status

Aceito

## Data

2025-12-12

## Contexto

O Projeto RADAR é uma API regulatória crítica que deve:

1. Atender requisitos específicos da ANEEL com precisão
2. Garantir disponibilidade 24x7
3. Retornar dados corretos e consistentes
4. Ser auditável e rastreável

Erros podem resultar em penalidades regulatórias e impacto na imagem da empresa.

## Decisão

Adotaremos **Test-Driven Development (TDD)** como prática de desenvolvimento, com foco em:

### Pirâmide de Testes

```
                    ┌───────────┐
                    │   E2E     │  10%
                    │  Tests    │
                 ┌──┴───────────┴──┐
                 │  Integration    │  30%
                 │     Tests       │
              ┌──┴─────────────────┴──┐
              │      Unit Tests       │  60%
              │                       │
              └───────────────────────┘
```

### Ferramentas

| Ferramenta | Uso |
|------------|-----|
| **Vitest** | Test runner e assertions |
| **@fastify/inject** | Testes HTTP sem servidor real |
| **testcontainers** | Banco Oracle para testes de integração |
| **MSW** | Mock de APIs externas (se houver) |
| **c8/istanbul** | Cobertura de código |

### Estrutura de Testes

```
tests/
├── unit/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── interrupcao.entity.spec.ts
│   │   └── services/
│   │       └── calcular-tipo-interrupcao.spec.ts
│   ├── application/
│   │   └── use-cases/
│   │       └── get-interrupcoes-ativas.spec.ts
│   └── shared/
│       └── utils/
│           └── date-formatter.spec.ts
│
├── integration/
│   ├── repositories/
│   │   └── interrupcao.repository.spec.ts
│   └── database/
│       └── oracle-connection.spec.ts
│
└── e2e/
    ├── interrupcoes.e2e.spec.ts
    ├── demandas.e2e.spec.ts
    └── health.e2e.spec.ts
```

### Convenções de Nomenclatura

```typescript
// Arquivo: get-interrupcoes-ativas.spec.ts

describe('GetInterrupcoesAtivasUseCase', () => {
  describe('execute', () => {
    it('should return empty array when no interrupcoes are active', async () => {
      // Arrange
      // Act
      // Assert
    });

    it('should classify interrupcao as PROGRAMADA when PLAN_ID exists', async () => {
      // ...
    });

    it('should return IBGE code from IND_UNIVERSOS', async () => {
      // ...
    });

    it('should throw when database connection fails', async () => {
      // ...
    });
  });
});
```

### Metas de Cobertura

| Métrica | Meta Mínima |
|---------|-------------|
| **Statements** | 80% |
| **Branches** | 75% |
| **Functions** | 85% |
| **Lines** | 80% |

### Configuração Vitest

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.spec.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'dist/', 'tests/'],
      thresholds: {
        statements: 80,
        branches: 75,
        functions: 85,
        lines: 80,
      },
    },
    setupFiles: ['./tests/setup.ts'],
  },
  resolve: {
    alias: {
      '@domain': path.resolve(__dirname, './src/domain'),
      '@application': path.resolve(__dirname, './src/application'),
      '@infrastructure': path.resolve(__dirname, './src/infrastructure'),
      '@interfaces': path.resolve(__dirname, './src/interfaces'),
      '@shared': path.resolve(__dirname, './src/shared'),
    },
  },
});
```

## Ciclo TDD

```
┌─────────────────────────────────────────────────────────┐
│                     CICLO TDD                            │
└─────────────────────────────────────────────────────────┘

    ┌──────────┐
    │  RED     │  1. Escrever teste que falha
    │  (Fail)  │
    └────┬─────┘
         │
         ▼
    ┌──────────┐
    │  GREEN   │  2. Escrever código mínimo para passar
    │  (Pass)  │
    └────┬─────┘
         │
         ▼
    ┌──────────┐
    │ REFACTOR │  3. Refatorar mantendo testes verdes
    │          │
    └────┬─────┘
         │
         └──────► Repetir
```

## Consequências

### Positivas

- **Confiança**: Mudanças podem ser feitas com segurança
- **Documentação Viva**: Testes documentam comportamento esperado
- **Design Melhor**: TDD força design desacoplado e testável
- **Debugging Rápido**: Falhas são detectadas imediatamente
- **Conformidade ANEEL**: Requisitos testados automaticamente
- **Regressão**: Evita quebrar funcionalidades existentes

### Negativas

- **Tempo Inicial**: Desenvolvimento mais lento no início
- **Manutenção**: Testes precisam ser mantidos junto com código
- **Curva de Aprendizado**: TDD requer prática para fazer bem

### Neutras

- Necessidade de ambiente de teste configurado
- CI/CD deve executar testes em cada push

## Alternativas Consideradas

### Alternativa 1: Testes Apenas de Integração/E2E

Testar apenas o sistema completo end-to-end.

**Rejeitado porque**: Testes lentos, difíceis de debugar, não testam edge cases adequadamente.

### Alternativa 2: Testes Manuais

Testar manualmente antes de cada release.

**Rejeitado porque**: Não escala, propenso a erros humanos, não detecta regressões.

### Alternativa 3: Testes Apenas Pós-Desenvolvimento

Escrever testes depois do código.

**Rejeitado porque**: Código tende a ser menos testável, cobertura geralmente menor, testes viram afterthought.

## Referências

- Kent Beck - Test-Driven Development by Example
- Martin Fowler - [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Vitest Documentation](https://vitest.dev/)
