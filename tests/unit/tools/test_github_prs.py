"""Testes para a tool github pull requests."""

from unittest.mock import MagicMock, patch

from assistant.tools.github.pull_requests import GitHubPRTool


def test_github_pr_tool_properties() -> None:
    """Verifica propriedades da ferramenta."""
    tool = GitHubPRTool()
    assert tool.name == "github_pr"
    assert "pull request" in tool.description.lower()
    for req in ["repo", "title", "head", "base"]:
        assert req in tool.schema["required"]


@patch("assistant.tools.github.pull_requests.GitHubClient")
def test_github_pr_create(mock_client_class: MagicMock) -> None:
    """Verifica criação de PR com sucesso."""
    mock_client = mock_client_class.return_value
    mock_client.create_pull_request.return_value = {"html_url": "https://github.com/pr/1"}

    tool = GitHubPRTool()
    result = tool.execute(
        repo="owner/repo",
        title="Fix bug",
        head="feature",
        base="main",
        body="Details"
    )

    assert result.success is True
    assert "https://github.com/pr/1" in result.output
    mock_client.create_pull_request.assert_called_once_with(
        repo="owner/repo", title="Fix bug", head="feature", base="main", body="Details"
    )


@patch("assistant.tools.github.pull_requests.GitHubClient")
def test_github_pr_api_error(mock_client_class: MagicMock) -> None:
    """Verifica tratamento de erro da API."""
    mock_client = mock_client_class.return_value
    mock_client.create_pull_request.side_effect = Exception("API Error")

    tool = GitHubPRTool()
    result = tool.execute(
        repo="owner/repo",
        title="Fix bug",
        head="feature",
        base="main"
    )

    assert result.success is False
    assert result.error_code == "GITHUB_API_ERROR"
    assert "API Error" in result.output
