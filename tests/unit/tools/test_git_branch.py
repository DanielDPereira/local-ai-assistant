"""Testes para a tool git branch."""

import subprocess
from unittest.mock import MagicMock, patch

from assistant.tools.git.branch import GitBranchTool


def test_git_branch_tool_properties() -> None:
    """Verifica as propriedades da ferramenta."""
    tool = GitBranchTool()
    assert tool.name == "git_branch"
    assert "branch" in tool.description.lower()
    assert tool.schema["type"] == "object"
    assert "action" in tool.schema["required"]


@patch("subprocess.run")
def test_git_branch_list(mock_run: MagicMock) -> None:
    """Verifica listar branches."""
    mock_run.return_value.stdout = "* main\n  feature/test"
    mock_run.return_value.returncode = 0

    tool = GitBranchTool()
    result = tool.execute(action="list")

    assert result.success is True
    assert "main" in result.output
    mock_run.assert_called_once_with(["git", "branch", "-a"], cwd=None, capture_output=True, text=True, check=True)


@patch("subprocess.run")
def test_git_branch_create(mock_run: MagicMock) -> None:
    """Verifica criar branch."""
    mock_run.return_value.stdout = ""
    mock_run.return_value.returncode = 0

    tool = GitBranchTool()
    result = tool.execute(action="create", branch_name="nova-branch")

    assert result.success is True
    mock_run.assert_called_once_with(["git", "checkout", "-b", "nova-branch"], cwd=None, capture_output=True, text=True, check=True)


def test_git_branch_missing_param() -> None:
    """Verifica erro quando falta nome da branch."""
    tool = GitBranchTool()
    result = tool.execute(action="create")

    assert result.success is False
    assert result.error_code == "MISSING_PARAMETERS"


@patch("subprocess.run")
def test_git_branch_failure(mock_run: MagicMock) -> None:
    """Verifica a execução com falha."""
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["git", "checkout", "inexistente"],
        stderr="error: pathspec 'inexistente' did not match any file(s) known to git"
    )

    tool = GitBranchTool()
    result = tool.execute(action="checkout", branch_name="inexistente")

    assert result.success is False
    assert result.error_code == "GIT_BRANCH_FAILED"
    assert "error: pathspec" in result.output
