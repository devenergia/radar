#!/usr/bin/env python3
"""
Hook UserPromptSubmit: Injeta contexto relevante baseado no prompt do usuario.
Detecta intencoes e adiciona lembretes sobre padroes.
"""

import json
import re
import sys

# Padroes de deteccao de intencao
INTENT_PATTERNS = {
    "create_entity": [
        r"criar?\s+(uma?\s+)?entidade",
        r"create\s+entity",
        r"nova\s+entidade",
    ],
    "create_value_object": [
        r"criar?\s+(um?\s+)?value\s*object",
        r"criar?\s+(um?\s+)?vo\b",
        r"novo\s+value\s*object",
    ],
    "create_test": [
        r"criar?\s+(um?\s+)?teste",
        r"escrever?\s+(um?\s+)?teste",
        r"adicionar?\s+testes?",
        r"tdd",
    ],
    "create_usecase": [
        r"criar?\s+(um?\s+)?use\s*case",
        r"novo\s+use\s*case",
        r"caso\s+de\s+uso",
    ],
    "create_repository": [
        r"criar?\s+(um?\s+)?reposit[oó]rio",
        r"novo\s+reposit[oó]rio",
    ],
    "create_endpoint": [
        r"criar?\s+(um?\s+)?endpoint",
        r"nova?\s+rota",
        r"adicionar?\s+(uma?\s+)?api",
    ],
    "refactor": [
        r"refatorar?",
        r"melhorar?\s+c[oó]digo",
        r"refactor",
    ],
    "review": [
        r"revisar?",
        r"review",
        r"verificar?\s+c[oó]digo",
    ],
}

# Lembretes por intencao
REMINDERS = {
    "create_entity": [
        "Use @dataclass com atributos privados (_campo)",
        "Implemente __eq__ e __hash__ baseados no ID",
        "Factory method create() deve retornar Result",
        "Comando disponivel: /create-entity [Nome]",
    ],
    "create_value_object": [
        "Use @dataclass(frozen=True) para imutabilidade",
        "Validacao no __post_init__",
        "Factory method create() deve retornar Result",
        "Comando disponivel: /create-value-object [Nome]",
    ],
    "create_test": [
        "TDD: Escreva o teste ANTES do codigo",
        "Use padrao AAA (Arrange-Act-Assert)",
        "Nomenclatura: test_deve_<comportamento>_quando_<condicao>",
        "Comando disponivel: /create-test [tipo] [modulo]",
    ],
    "create_usecase": [
        "Use Cases dependem apenas de Protocols (DIP)",
        "Metodo principal: async execute() -> Result",
        "NAO importe de infrastructure",
        "Comando disponivel: /create-usecase [Nome]",
    ],
    "create_repository": [
        "Protocol no domain, implementacao em infrastructure",
        "Metodos sao async",
        "Retorne entidades de dominio (nao dicts)",
        "Comando disponivel: /create-repository [Nome]",
    ],
    "create_endpoint": [
        "Use Pydantic para schemas de request/response",
        "Dependency Injection via Depends()",
        "Formato de resposta ANEEL para APIs regulatorias",
        "Comando disponivel: /create-endpoint [nome] [metodo] [api]",
    ],
    "refactor": [
        "Mantenha testes passando durante refatoracao",
        "Verifique Clean Architecture apos mudancas",
        "Use /validate-architecture para verificar",
    ],
    "review": [
        "Use /review-code [arquivo] para revisao completa",
        "Verifique SOLID, Clean Code, TDD",
    ],
}


def detect_intent(prompt: str) -> list[str]:
    """Detecta intencoes no prompt do usuario."""
    intents = []
    prompt_lower = prompt.lower()

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, prompt_lower):
                intents.append(intent)
                break

    return intents


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Se nao conseguir ler JSON, sair silenciosamente
        sys.exit(0)

    prompt = input_data.get("prompt", "")

    if not prompt:
        sys.exit(0)

    intents = detect_intent(prompt)

    if not intents:
        # Sem intencoes detectadas - sair sem output
        sys.exit(0)

    # Construir contexto com lembretes
    context_parts = []

    for intent in intents[:2]:  # Limitar a 2 intencoes
        if intent in REMINDERS:
            context_parts.append(f"Lembretes para {intent.replace('_', ' ')}:")
            for reminder in REMINDERS[intent]:
                context_parts.append(f"  - {reminder}")

    if context_parts:
        output = {
            "additionalContext": "\n".join(context_parts),
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
