"""Tool para realizar commits semânticos no git."""

from __future__ import annotations

import subprocess
from typing import Any

from assistant.tools.base import BaseTool, ToolResult


class GitCommitTool(BaseTool):
    """Ferramenta para realizar commits semânticos no repositório Git."""

    @property
    def name(self) -> str:
        return "git_commit"

    @property
    def description(self) -> str:
        return "Cria um commit no repositório Git seguindo Conventional Commits. Opcionalmente pode adicionar arquivos ao staging antes do commit."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Mensagem do commit (ex: 'feat: adiciona nova funcionalidade')."
                },
                "add_all": {
                    "type": "boolean",
                    "description": "Se verdadeiro, executa 'git add -A' antes do commit."
                },
                "cwd": {
                    "type": "string",
                    "description": "Diretório de trabalho opcional. Se não fornecido, usa o diretório atual."
                }
            },
            "required": ["message"],
            "additionalProperties": False
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        message = kwargs.get("message")
        add_all = kwargs.get("add_all", False)
        cwd = kwargs.get("cwd")

        if not message:
            return ToolResult(
                success=False,
                output="message é obrigatório.",
                error_code="MISSING_PARAMETERS"
            )

        try:
            if add_all:
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    check=True
                )

            result = subprocess.run(
                ["git", "commit", "-m", str(message)],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            return ToolResult(
                success=True,
                output=result.stdout
            )
        except subprocess.CalledProcessError as e:
            return ToolResult(
                success=False,
                output=e.stderr or e.stdout or str(e),
                error_code="GIT_COMMIT_FAILED"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=str(e),
                error_code="INTERNAL_ERROR"
            )
