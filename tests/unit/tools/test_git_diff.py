"""Testes para a tool git diff."""

import subprocess
from unittest.mock import MagicMock, patch

from assistant.tools.git.diff import GitDiffTool


def test_git_diff_tool_properties() -> None:
    """Verifica as propriedades da ferramenta."""
    tool = GitDiffTool()
    assert tool.name == "git_diff"
    assert "diff" in tool.description.lower()
    assert tool.schema["type"] == "object"
    assert "staged" in tool.schema["properties"]
    assert "target" in tool.schema["properties"]


@patch("subprocess.run")
def test_git_diff_success(mock_run: MagicMock) -> None:
    """Verifica a execução com sucesso sem parâmetros."""
    mock_run.return_value.stdout = "diff --git a/file b/file"
    mock_run.return_value.returncode = 0

    tool = GitDiffTool()
    result = tool.execute()

    assert result.success is True
    assert result.output == "diff --git a/file b/file"
    mock_run.assert_called_once_with(["git", "diff"], cwd=None, capture_output=True, text=True, check=True)


@patch("subprocess.run")
def test_git_diff_staged(mock_run: MagicMock) -> None:
    """Verifica a execução com o parâmetro staged."""
    mock_run.return_value.stdout = "diff --git a/file b/file"
    mock_run.return_value.returncode = 0

    tool = GitDiffTool()
    result = tool.execute(staged=True)

    assert result.success is True
    mock_run.assert_called_once_with(["git", "diff", "--staged"], cwd=None, capture_output=True, text=True, check=True)


@patch("subprocess.run")
def test_git_diff_target(mock_run: MagicMock) -> None:
    """Verifica a execução com o parâmetro target."""
    mock_run.return_value.stdout = "diff --git a/file b/file"
    mock_run.return_value.returncode = 0

    tool = GitDiffTool()
    result = tool.execute(target="HEAD~1")

    assert result.success is True
    mock_run.assert_called_once_with(["git", "diff", "HEAD~1"], cwd=None, capture_output=True, text=True, check=True)


@patch("subprocess.run")
def test_git_diff_failure(mock_run: MagicMock) -> None:
    """Verifica a execução com falha."""
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=128,
        cmd=["git", "diff"],
        stderr="fatal: not a git repository"
    )

    tool = GitDiffTool()
    result = tool.execute()

    assert result.success is False
    assert result.error_code == "GIT_DIFF_FAILED"
    assert "fatal: not a git repository" in result.output
