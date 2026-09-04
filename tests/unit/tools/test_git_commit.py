"""Testes para a tool git commit."""

import subprocess
from unittest.mock import MagicMock, call, patch

from assistant.tools.git.commit import GitCommitTool


def test_git_commit_tool_properties() -> None:
    """Verifica as propriedades da ferramenta."""
    tool = GitCommitTool()
    assert tool.name == "git_commit"
    assert "commit" in tool.description.lower()
    assert tool.schema["type"] == "object"
    assert "message" in tool.schema["required"]


@patch("subprocess.run")
def test_git_commit_success(mock_run: MagicMock) -> None:
    """Verifica commit semântico com sucesso."""
    mock_run.return_value.stdout = "[main 1234567] feat: nova funcionalidade"
    mock_run.return_value.returncode = 0

    tool = GitCommitTool()
    result = tool.execute(message="feat: nova funcionalidade")

    assert result.success is True
    assert "1234567" in result.output
    mock_run.assert_called_once_with(["git", "commit", "-m", "feat: nova funcionalidade"], cwd=None, capture_output=True, text=True, check=True)


@patch("subprocess.run")
def test_git_commit_with_add_all(mock_run: MagicMock) -> None:
    """Verifica commit com add_all=True."""
    mock_run.return_value.stdout = "[main 1234567] fix: bug resolvido"
    mock_run.return_value.returncode = 0

    tool = GitCommitTool()
    result = tool.execute(message="fix: bug resolvido", add_all=True)

    assert result.success is True

    assert mock_run.call_count == 2
    mock_run.assert_has_calls([
        call(["git", "add", "-A"], cwd=None, capture_output=True, text=True, check=True),
        call(["git", "commit", "-m", "fix: bug resolvido"], cwd=None, capture_output=True, text=True, check=True)
    ])


def test_git_commit_missing_param() -> None:
    """Verifica erro quando falta message."""
    tool = GitCommitTool()
    result = tool.execute()

    assert result.success is False
    assert result.error_code == "MISSING_PARAMETERS"


@patch("subprocess.run")
def test_git_commit_failure(mock_run: MagicMock) -> None:
    """Verifica a execução com falha."""
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["git", "commit", "-m", "test"],
        stderr="nothing to commit, working tree clean"
    )

    tool = GitCommitTool()
    result = tool.execute(message="test")

    assert result.success is False
    assert result.error_code == "GIT_COMMIT_FAILED"
    assert "nothing to commit" in result.output
