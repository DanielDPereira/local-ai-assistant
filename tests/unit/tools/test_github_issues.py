"""Testes para a tool github issues."""

from unittest.mock import MagicMock, patch

from assistant.tools.github.issues import GitHubIssuesTool


def test_github_issues_tool_properties() -> None:
    """Verifica propriedades da ferramenta."""
    tool = GitHubIssuesTool()
    assert tool.name == "github_issues"
    assert "issue" in tool.description.lower()
    assert "action" in tool.schema["required"]
    assert "repo" in tool.schema["required"]


@patch("assistant.tools.github.issues.GitHubClient")
def test_github_issues_get(mock_client_class: MagicMock) -> None:
    """Verifica consultar issue."""
    mock_client = mock_client_class.return_value
    mock_client.get_issue.return_value = {"id": 1, "title": "Bug"}

    tool = GitHubIssuesTool()
    result = tool.execute(action="get", repo="owner/repo", issue_number=10)

    assert result.success is True
    assert "Bug" in result.output
    mock_client.get_issue.assert_called_once_with("owner/repo", 10)


@patch("assistant.tools.github.issues.GitHubClient")
def test_github_issues_create(mock_client_class: MagicMock) -> None:
    """Verifica criar issue."""
    mock_client = mock_client_class.return_value
    mock_client.create_issue.return_value = {"html_url": "https://github.com"}

    tool = GitHubIssuesTool()
    result = tool.execute(action="create", repo="owner/repo", title="New feature", body="Details")

    assert result.success is True
    assert "https://github.com" in result.output
    mock_client.create_issue.assert_called_once_with("owner/repo", "New feature", "Details")


@patch("assistant.tools.github.issues.GitHubClient")
def test_github_issues_missing_param_get(mock_client_class: MagicMock) -> None:
    """Verifica falta de parametro no get."""
    tool = GitHubIssuesTool()
    result = tool.execute(action="get", repo="owner/repo")

    assert result.success is False
    assert result.error_code == "MISSING_PARAMETERS"


@patch("assistant.tools.github.issues.GitHubClient")
def test_github_issues_missing_param_create(mock_client_class: MagicMock) -> None:
    """Verifica falta de parametro no create."""
    tool = GitHubIssuesTool()
    result = tool.execute(action="create", repo="owner/repo")

    assert result.success is False
    assert result.error_code == "MISSING_PARAMETERS"
