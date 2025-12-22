#!/usr/bin/env python3
"""Hook para validar uso do ambiente virtual correto.

Bloqueia comandos pip/pytest que nao usam o venv do projeto.
"""

import json
import os
import sys

# Caminho do venv do projeto
PROJECT_VENV = r"D:\Projeto Radar\venv"
VENV_SCRIPTS = os.path.join(PROJECT_VENV, "Scripts")

# Comandos que devem usar o venv
VENV_COMMANDS = ["pip", "pytest", "python", "mypy", "ruff"]


def main() -> None:
    """Valida se comandos Python usam o venv correto."""
    # Ler input do hook
    input_data = json.loads(sys.stdin.read())

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Apenas validar comandos Bash
    if tool_name != "Bash":
        print(json.dumps({"decision": "approve"}))
        return

    command = tool_input.get("command", "")

    # Verificar se e um comando que precisa do venv
    needs_venv = False
    for cmd in VENV_COMMANDS:
        # Verifica se o comando comeca com pip, pytest, etc
        # mas ignora se ja esta usando o caminho do venv
        if command.strip().startswith(cmd) or f" {cmd} " in command:
            needs_venv = True
            break

    if not needs_venv:
        print(json.dumps({"decision": "approve"}))
        return

    # Verificar se esta usando o venv correto
    uses_correct_venv = (
        PROJECT_VENV in command
        or VENV_SCRIPTS in command
        or "venv\\Scripts\\" in command
        or "venv/Scripts/" in command
    )

    # Comandos com caminho absoluto do venv sao permitidos
    if uses_correct_venv:
        print(json.dumps({"decision": "approve"}))
        return

    # Bloquear comandos que nao usam o venv
    error_msg = f"""
BLOQUEADO: Comando deve usar o ambiente virtual do projeto.

Comando bloqueado: {command}

Use o venv correto:
  - pytest: {VENV_SCRIPTS}\\pytest.exe
  - pip: {VENV_SCRIPTS}\\pip.exe
  - python: {VENV_SCRIPTS}\\python.exe

Exemplo correto:
  {VENV_SCRIPTS}\\pytest.exe backend/tests/ -v
  {VENV_SCRIPTS}\\pip.exe install package-name
"""

    print(json.dumps({"decision": "block", "reason": error_msg.strip()}))


if __name__ == "__main__":
    main()
