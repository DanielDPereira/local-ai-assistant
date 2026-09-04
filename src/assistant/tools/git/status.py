"""Tool para executar git status."""

from __future__ import annotations

import subprocess
from typing import Any

from assistant.tools.base import BaseTool, ToolResult


class GitStatusTool(BaseTool):
    """Ferramenta para obter o status atual do repositório Git."""

    @property
    def name(self) -> str:
        return "git_status"

    @property
    def description(self) -> str:
        return "Obtém o status atual do repositório Git (arquivos modificados, branch atual, etc)."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "cwd": {
                    "type": "string",
                    "description": "Diretório de trabalho opcional. Se não fornecido, usa o diretório atual."
                }
            },
            "additionalProperties": False
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        cwd = kwargs.get("cwd")

        try:
            result = subprocess.run(
                ["git", "status"],
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
                error_code="GIT_STATUS_FAILED"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=str(e),
                error_code="INTERNAL_ERROR"
            )
