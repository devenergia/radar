#!/usr/bin/env python3
"""Hook para validar que branches de feature sao criadas a partir de 'hm'.

REGRA DO PROJETO RADAR:
- Todas as branches de feature devem ser criadas a partir da branch 'hm'
- A branch 'main' e usada apenas para releases
"""

import json
import os
import subprocess
import sys


def get_current_branch() -> str:
    """Retorna o nome da branch atual."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=os.environ.get("CLAUDE_PROJECT_DIR", "."),
    )
    return result.stdout.strip()


def main() -> None:
    """Valida a criacao de branches."""
    # Ler input do hook
    input_data = json.loads(sys.stdin.read())

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Apenas validar comandos Bash
    if tool_name != "Bash":
        print(json.dumps({"decision": "approve"}))
        return

    command = tool_input.get("command", "")

    # Verifica se e um comando de criacao de branch
    if "checkout -b" in command:
        current_branch = get_current_branch()

        # Se nao estamos em 'hm', bloqueia criacao de branch
        if current_branch not in ("hm", "main"):
            # Permite se ja estamos em uma branch de feature
            print(json.dumps({"decision": "approve"}))
            return

        if current_branch == "main":
            print(
                json.dumps(
                    {
                        "decision": "block",
                        "reason": "Branches de feature devem ser criadas a partir de 'hm', nao de 'main'. "
                        "Use: git checkout hm && git checkout -b <branch>",
                    }
                )
            )
            return

    # Se estamos tentando fazer checkout para main para criar branch, avisa
    if "checkout main" in command and "checkout -b" in command:
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": "Nao crie branches a partir de 'main'. Use 'hm' como base.",
                }
            )
        )
        return

    print(json.dumps({"decision": "approve"}))


if __name__ == "__main__":
    main()
