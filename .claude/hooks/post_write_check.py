#!/usr/bin/env python3
"""
Hook PostToolUse: Verifica arquivos apos escrita/edicao.
Sugere acoes como criar testes ou rodar lint.
"""

import json
import sys
from pathlib import Path


def get_test_path(file_path: str) -> str | None:
    """Retorna o caminho esperado do teste para um arquivo."""
    if "/tests/" in file_path or r"\tests\\" in file_path:
        return None  # Ja e um teste

    if not file_path.endswith(".py"):
        return None

    # Determinar tipo de teste baseado na camada
    if "/domain/value_objects/" in file_path or r"\domain\value_objects\\" in file_path:
        filename = Path(file_path).stem
        return f"backend/tests/unit/domain/value_objects/test_{filename}.py"

    if "/domain/entities/" in file_path or r"\domain\entities\\" in file_path:
        filename = Path(file_path).stem
        return f"backend/tests/unit/domain/entities/test_{filename}.py"

    if "/domain/services/" in file_path or r"\domain\services\\" in file_path:
        filename = Path(file_path).stem
        return f"backend/tests/unit/domain/services/test_{filename}.py"

    if "/application/use_cases/" in file_path or r"\application\use_cases\\" in file_path:
        filename = Path(file_path).stem
        return f"backend/tests/integration/use_cases/test_{filename}.py"

    if "/infrastructure/repositories/" in file_path or r"\infrastructure\repositories\\" in file_path:
        filename = Path(file_path).stem
        return f"backend/tests/integration/repositories/test_{filename}.py"

    return None


def check_test_exists(test_path: str, project_dir: str) -> bool:
    """Verifica se o arquivo de teste existe."""
    full_path = Path(project_dir) / test_path
    return full_path.exists()


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    cwd = input_data.get("cwd", ".")

    file_path = tool_input.get("file_path", "")

    if not file_path.endswith(".py"):
        sys.exit(0)

    suggestions = []

    # Verificar se teste existe
    test_path = get_test_path(file_path)
    if test_path and not check_test_exists(test_path, cwd):
        suggestions.append(
            f"TDD: Crie o teste em {test_path} (use /create-test)"
        )

    # Sugerir lint para arquivos de producao
    if "/tests/" not in file_path and r"\tests\\" not in file_path:
        suggestions.append("Execute ruff check para verificar o codigo")

    if suggestions:
        output = {
            "additionalContext": "\n".join(suggestions),
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
