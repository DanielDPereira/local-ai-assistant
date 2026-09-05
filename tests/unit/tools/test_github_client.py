"""Testes para o cliente do GitHub."""

import email.message
import os
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from assistant.tools.github.client import GitHubClient


def test_github_client_init_no_token() -> None:
    """Verifica se lança erro quando não há token."""
    with patch.dict(os.environ, clear=True):
        if "GITHUB_TOKEN" in os.environ:
            del os.environ["GITHUB_TOKEN"]

        with pytest.raises(ValueError, match="GITHUB_TOKEN não configurado"):
            GitHubClient()


def test_github_client_init_with_token() -> None:
    """Verifica inicialização com token."""
    client = GitHubClient(token="fake-token")
    assert client.token == "fake-token"


@patch("urllib.request.urlopen")
def test_github_client_make_request_success(mock_urlopen: MagicMock) -> None:
    """Verifica _make_request com sucesso."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"id": 123, "name": "test"}'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    client = GitHubClient(token="fake-token")
    result = client._make_request("/repos/user/repo")

    assert result == {"id": 123, "name": "test"}
    mock_urlopen.assert_called_once()


@patch("urllib.request.urlopen")
def test_github_client_make_request_error(mock_urlopen: MagicMock) -> None:
    """Verifica tratamento de erro HTTP no _make_request."""
    hdrs = email.message.Message()
    mock_error = urllib.error.HTTPError(
        url="https://api.github.com/repos/user/repo",
        code=404,
        msg="Not Found",
        hdrs=hdrs,
        fp=None  # type: ignore
    )
    # Patch the read method of the HTTPError instance
    mock_error.read = MagicMock(return_value=b'{"message": "Not Found"}')
    mock_urlopen.side_effect = mock_error

    client = GitHubClient(token="fake-token")
    with pytest.raises(Exception, match="GitHub API Error \\(404\\): Not Found"):
        client._make_request("/repos/user/repo")
