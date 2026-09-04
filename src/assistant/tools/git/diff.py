"""Tool para executar git diff."""

from __future__ import annotations

import subprocess
from typing import Any

from assistant.tools.base import BaseTool, ToolResult


class GitDiffTool(BaseTool):
    """Ferramenta para visualizar diffs no repositório Git."""

    @property
    def name(self) -> str:
        return "git_diff"

    @property
    def description(self) -> str:
        return "Obtém as diferenças (diff) do repositório Git atual. Pode ser usado para ver mudanças não commitadas ou diff entre commits/branches."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "staged": {
                    "type": "boolean",
                    "description": "Se verdadeiro, mostra as mudanças em staging (git diff --staged)."
                },
                "target": {
                    "type": "string",
                    "description": "Alvo específico para o diff (ex: commit hash, branch, arquivo)."
                },
                "cwd": {
                    "type": "string",
                    "description": "Diretório de trabalho opcional. Se não fornecido, usa o diretório atual."
                }
            },
            "additionalProperties": False
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        staged = kwargs.get("staged", False)
        target = kwargs.get("target")
        cwd = kwargs.get("cwd")

        cmd = ["git", "diff"]
        if staged:
            cmd.append("--staged")
        if target:
            cmd.append(str(target))

        try:
            result = subprocess.run(
                cmd,
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
                error_code="GIT_DIFF_FAILED"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=str(e),
                error_code="INTERNAL_ERROR"
            )
