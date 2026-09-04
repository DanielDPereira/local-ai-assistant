"""Tool para realizar git push controlado."""

from __future__ import annotations

import subprocess
from typing import Any

from assistant.tools.base import BaseTool, ToolResult


class GitPushTool(BaseTool):
    """Ferramenta para realizar push de commits para o repositório remoto."""

    @property
    def name(self) -> str:
        return "git_push"

    @property
    def description(self) -> str:
        return "Realiza 'git push' das mudanças locais para o repositório remoto."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "remote": {
                    "type": "string",
                    "description": "Nome do remoto (padrão: origin)."
                },
                "branch": {
                    "type": "string",
                    "description": "Nome da branch para empurrar. Se omitido, empurra a branch atual."
                },
                "force": {
                    "type": "boolean",
                    "description": "Realiza push forçado (apenas se extremamente necessário)."
                },
                "cwd": {
                    "type": "string",
                    "description": "Diretório de trabalho opcional. Se não fornecido, usa o diretório atual."
                }
            },
            "additionalProperties": False
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        remote = kwargs.get("remote", "origin")
        branch = kwargs.get("branch")
        force = kwargs.get("force", False)
        cwd = kwargs.get("cwd")

        cmd = ["git", "push"]
        if force:
            cmd.append("--force-with-lease")

        cmd.append(remote)
        if branch:
            cmd.append(branch)

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
                output=result.stderr or result.stdout or "Push realizado com sucesso."
            )
        except subprocess.CalledProcessError as e:
            return ToolResult(
                success=False,
                output=e.stderr or e.stdout or str(e),
                error_code="GIT_PUSH_FAILED"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=str(e),
                error_code="INTERNAL_ERROR"
            )
