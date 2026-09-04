"""Ferramenta para execução de comandos no terminal."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

from assistant.tools.base import BaseTool, ToolResult


class ExecuteCommandTool(BaseTool):
    """Executa comandos no workspace com timeout."""

    def __init__(self, workspace_path: str, default_timeout: int = 30) -> None:
        """Inicializa a ferramenta.

        Args:
            workspace_path: Diretório de trabalho padrão.
            default_timeout: Timeout padrão em segundos.
        """
        self._workspace = Path(workspace_path).resolve()
        self._default_timeout = default_timeout

    @property
    def name(self) -> str:
        return "execute_command"

    @property
    def description(self) -> str:
        return (
            "Executa um comando no terminal dentro do workspace. "
            "Retorna stdout e stderr. Use timeouts adequados."
        )

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Comando a ser executado.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout opcional em segundos (padrão 30).",
                },
            },
            "required": ["command"],
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        """Executa o comando fornecido."""
        command = kwargs.get("command")
        if not command:
            return ToolResult(
                success=False,
                output="O argumento 'command' é obrigatório.",
                error_code="MISSING_ARGUMENT",
            )

        timeout = kwargs.get("timeout", self._default_timeout)

        start_time = time.monotonic()
        try:
            # shell=True permite usar &&, | e variáveis de ambiente,
            # o que é comum e útil para o agente.
            result = subprocess.run(
                command,
                cwd=str(self._workspace),
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace"
            )

            duration = time.monotonic() - start_time
            success = result.returncode == 0

            output_parts = []
            if result.stdout:
                output_parts.append(result.stdout.strip())
            if result.stderr:
                output_parts.append(f"[STDERR]\n{result.stderr.strip()}")

            combined_output = "\n".join(output_parts) if output_parts else "(sem saída)"

            data = {
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration,
                "status": "success" if success else "failed"
            }

            return ToolResult(
                success=success,
                output=combined_output,
                data=data,
                error_code=None if success else "COMMAND_FAILED",
            )

        except subprocess.TimeoutExpired as e:
            duration = time.monotonic() - start_time
            data = {
                "command": command,
                "exit_code": -1,
                "stdout": e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""),
                "stderr": e.stderr.decode(errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or ""),
                "duration": duration,
                "status": "timeout"
            }
            return ToolResult(
                success=False,
                output=f"Timeout atingido após {timeout}s: {command}",
                data=data,
                error_code="TIMEOUT",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Erro ao executar o comando: {e}",
                error_code="UNKNOWN_ERROR",
            )
