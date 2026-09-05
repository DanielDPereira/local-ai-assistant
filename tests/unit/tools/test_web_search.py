"""Testes para o web_search."""

import urllib.error
from unittest.mock import MagicMock, patch

from assistant.tools.web.search import WebSearchTool


def test_web_search_properties() -> None:
    tool = WebSearchTool()
    assert tool.name == "web_search"
    assert "query" in tool.schema["required"]


@patch("urllib.request.urlopen")
def test_web_search_success(mock_urlopen: MagicMock) -> None:
    html = b'''
    <html><body>
    <table>
      <tr><td><a href="https://example.com" class="result-url">Example Title</a></td></tr>
      <tr><td class="result-snippet">This is an example snippet.</td></tr>
    </table>
    </body></html>
    '''
    mock_response = MagicMock()
    mock_response.read.return_value = html
    mock_urlopen.return_value.__enter__.return_value = mock_response

    tool = WebSearchTool()
    result = tool.execute(query="test")

    assert result.success is True
    assert "Example Title" in result.output
    assert "https://example.com" in result.output
    assert "This is an example snippet" in result.output


@patch("urllib.request.urlopen")
def test_web_search_empty(mock_urlopen: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.read.return_value = b"<html><body></body></html>"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    tool = WebSearchTool()
    result = tool.execute(query="test")

    assert result.success is True
    assert "Nenhum resultado" in result.output


@patch("urllib.request.urlopen")
def test_web_search_error(mock_urlopen: MagicMock) -> None:
    mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

    tool = WebSearchTool()
    result = tool.execute(query="test")

    assert result.success is False
    assert result.error_code == "SEARCH_ERROR"


def test_web_search_missing_query() -> None:
    tool = WebSearchTool()
    result = tool.execute()

    assert result.success is False
    assert result.error_code == "MISSING_PARAMETERS"
