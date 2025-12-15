#!/usr/bin/env python3
"""
Hook PreToolUse: Valida arquivos Python antes de escrever/editar.
Verifica padroes de Clean Architecture e boas praticas.
"""

import json
import re
import sys
from pathlib import Path

# Padroes de import proibidos por camada
FORBIDDEN_IMPORTS = {
    "domain": [
        (r"from\s+.*infrastructure", "Domain nao pode importar de infrastructure"),
        (r"from\s+.*application", "Domain nao pode importar de application"),
        (r"from\s+.*interfaces", "Domain nao pode importar de interfaces"),
        (r"from\s+fastapi", "Domain nao pode importar FastAPI"),
        (r"from\s+sqlalchemy", "Domain nao pode importar SQLAlchemy"),
        (r"import\s+oracledb", "Domain nao pode importar oracledb"),
    ],
    "application": [
        (r"from\s+.*infrastructure", "Application nao pode importar de infrastructure"),
        (r"from\s+.*interfaces", "Application nao pode importar de interfaces"),
        (r"from\s+fastapi", "Application nao pode importar FastAPI diretamente"),
    ],
}

# Padroes obrigatorios
REQUIRED_PATTERNS = {
    "value_objects": [
        (r"@dataclass\(frozen=True\)", "Value Objects devem ser imutaveis (@dataclass(frozen=True))"),
    ],
    "entities": [
        (r"def\s+__eq__", "Entities devem implementar __eq__"),
        (r"def\s+__hash__", "Entities devem implementar __hash__"),
    ],
    "use_cases": [
        (r"async\s+def\s+execute", "Use Cases devem ter metodo async execute()"),
        (r"Result\[", "Use Cases devem retornar Result"),
    ],
}


def get_layer(file_path: str) -> str | None:
    """Determina a camada do arquivo baseado no path."""
    if "/domain/" in file_path or "\\domain\\" in file_path:
        return "domain"
    if "/application/" in file_path or "\\application\\" in file_path:
        return "application"
    if "/infrastructure/" in file_path or "\\infrastructure\\" in file_path:
        return "infrastructure"
    if "/interfaces/" in file_path or "\\interfaces\\" in file_path:
        return "interfaces"
    return None


def get_component_type(file_path: str) -> str | None:
    """Determina o tipo de componente baseado no path."""
    if "/value_objects/" in file_path or "\\value_objects\\" in file_path:
        return "value_objects"
    if "/entities/" in file_path or "\\entities\\" in file_path:
        return "entities"
    if "/use_cases/" in file_path or "\\use_cases\\" in file_path:
        return "use_cases"
    return None


def validate_content(file_path: str, content: str) -> list[str]:
    """Valida o conteudo do arquivo contra os padroes."""
    issues = []

    # Verificar imports proibidos
    layer = get_layer(file_path)
    if layer and layer in FORBIDDEN_IMPORTS:
        for pattern, message in FORBIDDEN_IMPORTS[layer]:
            if re.search(pattern, content):
                issues.append(f"[{layer.upper()}] {message}")

    # Verificar padroes obrigatorios
    component = get_component_type(file_path)
    if component and component in REQUIRED_PATTERNS:
        for pattern, message in REQUIRED_PATTERNS[component]:
            if not re.search(pattern, content):
                issues.append(f"[{component.upper()}] {message}")

    # Verificar type hints em funcoes
    func_without_return = re.findall(
        r"def\s+\w+\([^)]*\)\s*:",
        content
    )
    for func in func_without_return:
        if "-> " not in func and "__init__" not in func:
            issues.append(f"Funcao sem type hint de retorno: {func[:50]}...")

    return issues


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Erro ao ler JSON: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Apenas verificar arquivos Python
    file_path = tool_input.get("file_path", "")
    if not file_path.endswith(".py"):
        sys.exit(0)

    # Obter conteudo (Write) ou novo conteudo (Edit)
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    if not content:
        sys.exit(0)

    issues = validate_content(file_path, content)

    if issues:
        output = {
            "continue": True,
            "systemMessage": "⚠️ Avisos de padrao:\n" + "\n".join(f"• {i}" for i in issues),
        }
        print(json.dumps(output))
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
