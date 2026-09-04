"""Testes para a tool git push."""

import subprocess
from unittest.mock import MagicMock, patch

from assistant.tools.git.push import GitPushTool


def test_git_push_tool_properties() -> None:
    """Verifica as propriedades da ferramenta."""
    tool = GitPushTool()
    assert tool.name == "git_push"
    assert "push" in tool.description.lower()
    assert tool.schema["type"] == "object"
    assert "remote" in tool.schema["properties"]


@patch("subprocess.run")
def test_git_push_success(mock_run: MagicMock) -> None:
    """Verifica push com sucesso."""
    mock_run.return_value.stderr = "To github.com:user/repo.git\n   123..456  main -> main"
    mock_run.return_value.returncode = 0

    tool = GitPushTool()
    result = tool.execute()

    assert result.success is True
    assert "main -> main" in result.output
    mock_run.assert_called_once_with(["git", "push", "origin"], cwd=None, capture_output=True, text=True, check=True)


@patch("subprocess.run")
def test_git_push_with_branch_and_force(mock_run: MagicMock) -> None:
    """Verifica push com branch específica e force-with-lease."""
    mock_run.return_value.stderr = "To github.com:user/repo.git\n + 123..456  feature -> feature (forced update)"
    mock_run.return_value.returncode = 0

    tool = GitPushTool()
    result = tool.execute(remote="upstream", branch="feature", force=True)

    assert result.success is True
    assert "forced update" in result.output
    mock_run.assert_called_once_with(["git", "push", "--force-with-lease", "upstream", "feature"], cwd=None, capture_output=True, text=True, check=True)


@patch("subprocess.run")
def test_git_push_failure(mock_run: MagicMock) -> None:
    """Verifica a execução com falha (ex: conflito)."""
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["git", "push", "origin"],
        stderr="error: failed to push some refs to 'github.com:user/repo.git'"
    )

    tool = GitPushTool()
    result = tool.execute()

    assert result.success is False
    assert result.error_code == "GIT_PUSH_FAILED"
    assert "failed to push" in result.output
