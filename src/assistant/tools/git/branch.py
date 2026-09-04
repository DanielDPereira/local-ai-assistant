"""Tool para gerenciamento de branches do git."""

from __future__ import annotations

import subprocess
from typing import Any

from assistant.tools.base import BaseTool, ToolResult


class GitBranchTool(BaseTool):
    """Ferramenta para gerenciar branches no repositório Git."""

    @property
    def name(self) -> str:
        return "git_branch"

    @property
    def description(self) -> str:
        return "Gerencia branches no repositório Git. Pode listar, criar ou deletar branches, e realizar checkout."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "create", "delete", "checkout"],
                    "description": "Ação a ser executada."
                },
                "branch_name": {
                    "type": "string",
                    "description": "Nome da branch (obrigatório para create, delete e checkout)."
                },
                "cwd": {
                    "type": "string",
                    "description": "Diretório de trabalho opcional. Se não fornecido, usa o diretório atual."
                }
            },
            "required": ["action"],
            "additionalProperties": False
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        action = kwargs.get("action")
        branch_name = kwargs.get("branch_name")
        cwd = kwargs.get("cwd")

        if action in ["create", "delete", "checkout"] and not branch_name:
            return ToolResult(
                success=False,
                output="branch_name é obrigatório para esta ação.",
                error_code="MISSING_PARAMETERS"
            )

        cmd = ["git"]
        if action == "list":
            cmd.extend(["branch", "-a"])
        elif action == "create":
            cmd.extend(["checkout", "-b", str(branch_name)])
        elif action == "delete":
            cmd.extend(["branch", "-D", str(branch_name)])
        elif action == "checkout":
            cmd.extend(["checkout", str(branch_name)])

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
                output=result.stdout or f"Ação '{action}' concluída com sucesso."
            )
        except subprocess.CalledProcessError as e:
            return ToolResult(
                success=False,
                output=e.stderr or e.stdout or str(e),
                error_code="GIT_BRANCH_FAILED"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=str(e),
                error_code="INTERNAL_ERROR"
            )
