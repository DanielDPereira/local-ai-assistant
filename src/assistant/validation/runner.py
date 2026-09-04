"""Componente responsável por executar validações de código estruturadas."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from assistant.telemetry.context import ExecutionContext
from assistant.telemetry.tracker import TelemetryTracker


@dataclass
class ValidationResult:
    """Resultado estruturado de uma execução de validação."""
    tool: str
    success: bool
    output: str
    duration: float


class ValidationRunner:
    """Executa verificações (ruff, mypy, pytest, build) no workspace."""

    def __init__(
        self,
        workspace_path: str,
        telemetry_tracker: TelemetryTracker | None = None,
        execution_context: ExecutionContext | None = None,
    ) -> None:
        """Inicializa o runner.

        Args:
            workspace_path: Diretório onde as validações serão executadas.
            telemetry_tracker: Opcional rastreador de telemetria.
            execution_context: Opcional contexto para telemetria.
        """
        self._workspace = Path(workspace_path).resolve()
        self._tracker = telemetry_tracker
        self._context = execution_context

    def _run_tool(self, tool_name: str, command: str) -> ValidationResult:
        """Executa uma ferramenta específica e retorna o resultado estruturado."""
        start = time.monotonic()
        try:
            result = subprocess.run(
                command,
                cwd=str(self._workspace),
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            success = result.returncode == 0

            output_parts = []
            if result.stdout:
                output_parts.append(result.stdout.strip())
            if result.stderr:
                output_parts.append(f"[STDERR]\n{result.stderr.strip()}")

            output = "\n".join(output_parts) if output_parts else "(sem saída)"


            duration = time.monotonic() - start
            if self._tracker and self._context:
                summary = output[:200] + "..." if len(output) > 200 else output
                self._tracker.track_validation(
                    self._context,
                    validation_name=tool_name,
                    duration=duration,
                    success=success,
                    output_summary=summary,
                )

            return ValidationResult(
                tool=tool_name,
                success=success,
                output=output,
                duration=duration,
            )
        except Exception as e:
            duration = time.monotonic() - start
            error_msg = f"Erro fatal executando {tool_name}: {e}"
            if self._tracker and self._context:
                self._tracker.track_validation(
                    self._context,
                    validation_name=tool_name,
                    duration=duration,
                    success=False,
                    output_summary="",
                    error=error_msg,
                )

            return ValidationResult(
                tool=tool_name,
                success=False,
                output=error_msg,
                duration=duration,
            )

    def run_ruff(self) -> ValidationResult:
        """Executa linter Ruff."""
        # Se .venv/Scripts/ruff não existir, vai usar global se der, ou dar erro de comando não encontrado.
        return self._run_tool("Ruff", "ruff check .")

    def run_mypy(self) -> ValidationResult:
        """Executa checador de tipos Mypy."""
        return self._run_tool("Mypy", "mypy .")

    def run_pytest(self) -> ValidationResult:
        """Executa testes Pytest."""
        return self._run_tool("Pytest", "pytest -v")

    def run_build(self) -> ValidationResult:
        """Executa o build system local (hatchling via python -m build)."""
        return self._run_tool("Build", "python -m build")

    def run_all(self) -> dict[str, ValidationResult]:
        """Executa todas as validações e retorna um dicionário com os resultados."""
        return {
            "Ruff": self.run_ruff(),
            "Mypy": self.run_mypy(),
            "Pytest": self.run_pytest(),
            "Build": self.run_build(),
        }
