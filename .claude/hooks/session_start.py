#!/usr/bin/env python3
"""
Hook SessionStart: Carrega contexto inicial do projeto RADAR.
Fornece informacoes uteis no inicio da sessao.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_project_status(project_dir: str) -> dict:
    """Coleta informacoes sobre o estado atual do projeto."""
    status = {
        "has_uncommitted_changes": False,
        "current_branch": "unknown",
        "test_coverage": "unknown",
        "last_test_run": "unknown",
    }

    # Verificar git status
    git_dir = Path(project_dir) / ".git"
    if git_dir.exists():
        try:
            import subprocess
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            status["has_uncommitted_changes"] = bool(result.stdout.strip())

            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            status["current_branch"] = result.stdout.strip() or "main"
        except Exception:
            pass

    return status


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    source = input_data.get("source", "startup")

    # Coletar status do projeto
    status = get_project_status(project_dir)

    # Construir contexto inicial
    context_parts = [
        "🎯 Projeto RADAR - Sistema de Monitoramento ANEEL",
        f"📅 Sessao iniciada: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"🌿 Branch: {status['current_branch']}",
    ]

    if status["has_uncommitted_changes"]:
        context_parts.append("⚠️ Existem mudancas nao commitadas")

    context_parts.extend([
        "",
        "📚 Comandos disponiveis:",
        "  /create-entity [Nome] - Criar Entity DDD",
        "  /create-value-object [Nome] - Criar Value Object",
        "  /create-usecase [Nome] - Criar Use Case",
        "  /create-repository [Nome] - Criar Repository",
        "  /create-test [tipo] [modulo] - Criar teste TDD",
        "  /create-endpoint [nome] [metodo] [api] - Criar endpoint",
        "  /review-code [arquivo] - Revisar codigo",
        "  /validate-architecture - Validar arquitetura",
        "  /run-tests [tipo] - Executar testes",
        "  /commit [tipo] [escopo] [msg] - Criar commit",
        "",
        "📋 Padroes obrigatorios:",
        "  • Clean Architecture (domain > application > infrastructure)",
        "  • TDD (teste PRIMEIRO, codigo depois)",
        "  • SOLID principles",
        "  • Result Pattern para erros",
    ])

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(context_parts),
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
