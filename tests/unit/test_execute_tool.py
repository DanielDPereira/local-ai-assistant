"""Testes para a ferramenta de execução de comandos."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

import pytest

from assistant.tools.terminal.execute import ExecuteCommandTool


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Fixture que provê um workspace temporário."""
    return tmp_path


@pytest.fixture
def tool(workspace: Path) -> ExecuteCommandTool:
    """Fixture que provê o ExecuteCommandTool."""
    return ExecuteCommandTool(workspace_path=str(workspace), default_timeout=2)


class TestExecuteCommandTool:
    """Testes para ExecuteCommandTool."""

    def test_execute_success(self, tool: ExecuteCommandTool) -> None:
        """Executa um comando com sucesso."""
        cmd = "echo Hello" if sys.platform == "win32" else "echo 'Hello'"
        result = tool.execute(command=cmd)

        assert result.success is True
        assert "Hello" in result.output
        assert result.data is not None
        assert result.data["exit_code"] == 0
        assert result.data["status"] == "success"
        assert result.data["duration"] >= 0

    def test_execute_failure(self, tool: ExecuteCommandTool) -> None:
        """Executa um comando que falha."""
        # Um comando que não existe ou falha propositalmente
        cmd = "exit 1" if sys.platform == "win32" else "false"
        result = tool.execute(command=cmd)

        assert result.success is False
        assert result.error_code == "COMMAND_FAILED"
        assert result.data is not None
        assert result.data["exit_code"] != 0
        assert result.data["status"] == "failed"

    def test_execute_timeout(self, tool: ExecuteCommandTool) -> None:
        """Testa o timeout de um comando."""
        cmd = "ping 127.0.0.1 -n 5" if sys.platform == "win32" else "sleep 5"

        result = tool.execute(command=cmd, timeout=1)

        assert result.success is False
        assert result.error_code == "TIMEOUT"
        assert "Timeout atingido após 1s" in result.output
        assert result.data is not None
        assert result.data["status"] == "timeout"
        assert result.data["exit_code"] == -1

    def test_missing_argument(self, tool: ExecuteCommandTool) -> None:
        """Falha se não receber o comando."""
        result = tool.execute()

        assert result.success is False
        assert result.error_code == "MISSING_ARGUMENT"

    def test_cwd_is_workspace(self, tool: ExecuteCommandTool, workspace: Path) -> None:
        """Comando roda dentro do workspace."""
        cmd = "cd" if sys.platform == "win32" else "pwd"
        result = tool.execute(command=cmd)

        assert result.success is True
        assert str(workspace.resolve()) in result.output

    def test_capture_stderr(self, tool: ExecuteCommandTool) -> None:
        """Testa a captura do stderr."""
        # Redireciona stdout para stderr
        cmd = "echo ErrorMessage 1>&2"
        result = tool.execute(command=cmd)

        assert "ErrorMessage" in result.output
        assert "[STDERR]" in result.output
        assert result.data is not None
        assert "ErrorMessage" in result.data["stderr"]

    def test_unknown_error(self, tool: ExecuteCommandTool) -> None:
        """Testa captura de exceções inesperadas (como OSError em caso de falha bizarra)."""
        with mock.patch("subprocess.run", side_effect=OSError("OS failed")):
            result = tool.execute(command="echo")

        assert result.success is False
        assert result.error_code == "UNKNOWN_ERROR"
        assert "OS failed" in result.output
