---
description: Revisa codigo contra os padroes do projeto RADAR
argument-hint: [caminho/do/arquivo.py]
allowed-tools: Read, Glob, Grep, Bash
---

# Code Review - Projeto RADAR

Faca uma revisao completa do arquivo `$ARGUMENTS` verificando TODOS os criterios abaixo.

## Checklist de Revisao

### 1. Clean Architecture
- [ ] Respeita a regra de dependencia (domain <- application <- infrastructure <- interfaces)
- [ ] NAO importa de camadas externas para internas
- [ ] Usa Dependency Injection corretamente

### 2. SOLID Principles
- [ ] **S**: Classe tem apenas UMA responsabilidade?
- [ ] **O**: Pode ser estendido sem modificacao?
- [ ] **L**: Implementacoes respeitam contratos (Protocol)?
- [ ] **I**: Interfaces sao pequenas e focadas?
- [ ] **D**: Depende de abstracoes (Protocol), nao implementacoes?

### 3. DDD (se aplicavel)
- [ ] Value Objects sao imutaveis (`frozen=True`)?
- [ ] Entities tem igualdade por ID?
- [ ] Factory methods retornam `Result`?
- [ ] Linguagem ubiqua esta correta (termos em portugues)?

### 4. Clean Code
- [ ] Nomes revelam intencao?
- [ ] Funcoes sao pequenas (< 20 linhas)?
- [ ] Funcoes fazem apenas UMA coisa?
- [ ] Sem comentarios obvios ou desatualizados?
- [ ] Formatacao consistente?

### 5. Python/FastAPI
- [ ] Type hints em TODAS as funcoes?
- [ ] Async/await usado corretamente?
- [ ] Pydantic para validacao?
- [ ] Logging com structlog?

### 6. Testes
- [ ] Existe teste correspondente?
- [ ] Cobertura adequada?
- [ ] Padrao AAA seguido?

## Formato do Output

```markdown
## Code Review: [arquivo]

### Conformidade

| Criterio | Status | Observacao |
|----------|--------|------------|
| Clean Architecture | OK/FALHA | ... |
| SOLID | OK/FALHA | ... |
| DDD | OK/FALHA/N/A | ... |
| Clean Code | OK/FALHA | ... |
| Python/FastAPI | OK/FALHA | ... |
| Testes | OK/FALHA | ... |

### Problemas Encontrados

1. **[Severidade: ALTA/MEDIA/BAIXA]** Descricao do problema
   - Linha: X
   - Sugestao: ...

### Sugestoes de Melhoria

1. ...

### Veredicto Final

[ ] APROVADO - Codigo pode ser mergeado
[ ] APROVADO COM RESSALVAS - Pequenos ajustes necessarios
[ ] REPROVADO - Correcoes obrigatorias necessarias
```

## Referencias para Consulta
- @docs/development/01-clean-architecture.md
- @docs/development/02-solid-principles.md
- @docs/development/03-domain-driven-design.md
- @docs/development/04-tdd-test-driven-development.md
- @docs/development/05-clean-code.md
