"""Testes para a tool git status."""

import subprocess
from unittest.mock import MagicMock, patch

from assistant.tools.git.status import GitStatusTool


def test_git_status_tool_properties() -> None:
    """Verifica as propriedades da ferramenta."""
    tool = GitStatusTool()
    assert tool.name == "git_status"
    assert "status" in tool.description.lower()
    assert tool.schema["type"] == "object"
    assert "cwd" in tool.schema["properties"]


@patch("subprocess.run")
def test_git_status_success(mock_run: MagicMock) -> None:
    """Verifica a execução com sucesso."""
    mock_run.return_value.stdout = "On branch main"
    mock_run.return_value.returncode = 0

    tool = GitStatusTool()
    result = tool.execute()

    assert result.success is True
    assert result.output == "On branch main"
    mock_run.assert_called_once()


@patch("subprocess.run")
def test_git_status_failure(mock_run: MagicMock) -> None:
    """Verifica a execução com falha (ex: não é um repositório)."""
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=128,
        cmd=["git", "status"],
        stderr="fatal: not a git repository"
    )

    tool = GitStatusTool()
    result = tool.execute()

    assert result.success is False
    assert result.error_code == "GIT_STATUS_FAILED"
    assert "fatal: not a git repository" in result.output
