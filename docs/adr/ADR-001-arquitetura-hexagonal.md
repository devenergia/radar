# ADR-001: Adoção de Arquitetura Hexagonal (Ports and Adapters)

## Status

Aceito

## Data

2025-12-12

## Contexto

O Projeto RADAR é uma API crítica que deve atender aos requisitos da ANEEL com prazo regulatório. A aplicação precisa:

1. Integrar com múltiplos sistemas fonte (Inservice, Indicadores) via DBLinks Oracle
2. Ser facilmente testável para garantir conformidade com os requisitos da ANEEL
3. Permitir evolução independente das camadas (ex: trocar framework HTTP sem afetar regras de negócio)
4. Manter o código organizado e de fácil manutenção
5. Facilitar a adição de novas APIs conforme demandado pela ANEEL

## Decisão

Adotaremos a **Arquitetura Hexagonal (Ports and Adapters)** combinada com princípios de **Clean Architecture** e **DDD**.

### Estrutura de Camadas

```
src/
├── domain/           # Núcleo - Entidades e Regras de Negócio
│   ├── entities/     # Entidades do domínio
│   ├── value-objects/# Objetos de valor
│   ├── repositories/ # Interfaces (Ports) de repositórios
│   └── services/     # Serviços de domínio
│
├── application/      # Casos de Uso
│   ├── use-cases/    # Implementação dos casos de uso
│   ├── dtos/         # Data Transfer Objects
│   └── mappers/      # Mapeadores entre camadas
│
├── infrastructure/   # Adapters de Saída (Driven)
│   ├── database/     # Conexões e queries Oracle
│   ├── repositories/ # Implementações dos repositórios
│   └── cache/        # Implementações de cache
│
├── interfaces/       # Adapters de Entrada (Driving)
│   └── http/
│       ├── controllers/
│       ├── middlewares/
│       ├── routes/
│       └── validators/
│
└── shared/           # Código compartilhado
    ├── config/
    ├── errors/
    └── utils/
```

### Regra de Dependência

As dependências sempre apontam para dentro:
- `interfaces` → `application` → `domain`
- `infrastructure` → `application` → `domain`

O `domain` não conhece nenhuma outra camada.

## Consequências

### Positivas

- **Testabilidade**: O domínio pode ser testado em isolamento, sem banco de dados ou HTTP
- **Flexibilidade**: Adapters podem ser trocados sem afetar o núcleo (ex: trocar Oracle por PostgreSQL)
- **Manutenibilidade**: Regras de negócio concentradas no domínio, fácil de entender e modificar
- **Conformidade ANEEL**: Regras específicas da ANEEL ficam encapsuladas e documentadas
- **Independência de Framework**: O domínio não depende de Fastify, Express ou qualquer framework

### Negativas

- **Complexidade Inicial**: Mais arquivos e camadas que uma arquitetura MVC simples
- **Curva de Aprendizado**: Equipe precisa entender os conceitos de DDD e Ports/Adapters
- **Overhead para CRUDs Simples**: Para operações triviais, pode parecer verboso

### Neutras

- Necessidade de mapeadores entre camadas (DTOs ↔ Entities)
- Interfaces explícitas para repositórios

## Alternativas Consideradas

### Alternativa 1: MVC Tradicional

Arquitetura mais simples com Controllers → Services → Repositories.

**Rejeitado porque**: Acoplamento alto entre camadas, dificuldade de testar regras de negócio isoladamente, tendência a "fat controllers" com lógica de negócio.

### Alternativa 2: Clean Architecture Pura

Camadas concêntricas com Entities → Use Cases → Interface Adapters → Frameworks.

**Rejeitado porque**: Muito similar à Hexagonal, mas a nomenclatura de Ports/Adapters é mais clara para integrações externas que são o foco do RADAR.

## Referências

- Alistair Cockburn - [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- Robert C. Martin - Clean Architecture
- Eric Evans - Domain-Driven Design
