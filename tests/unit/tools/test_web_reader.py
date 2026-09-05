"""Testes para o url_reader."""

import urllib.error
from unittest.mock import MagicMock, patch

from assistant.tools.web.reader import UrlReaderTool


def test_url_reader_properties() -> None:
    tool = UrlReaderTool()
    assert tool.name == "url_reader"
    assert "url" in tool.schema["required"]


@patch("urllib.request.urlopen")
def test_url_reader_success(mock_urlopen: MagicMock) -> None:
    html = b"<html><body><h1>Title</h1><script>ignore</script><p>Some text.</p></body></html>"
    mock_response = MagicMock()
    mock_response.read.return_value = html
    mock_urlopen.return_value.__enter__.return_value = mock_response

    tool = UrlReaderTool()
    result = tool.execute(url="http://example.com")

    assert result.success is True
    assert "Title" in result.output
    assert "Some text." in result.output
    assert "ignore" not in result.output


@patch("urllib.request.urlopen")
def test_url_reader_error(mock_urlopen: MagicMock) -> None:
    mock_urlopen.side_effect = urllib.error.URLError("Not Found")

    tool = UrlReaderTool()
    result = tool.execute(url="http://example.com")

    assert result.success is False
    assert result.error_code == "URL_ERROR"
    assert "Not Found" in result.output


def test_url_reader_missing_url() -> None:
    tool = UrlReaderTool()
    result = tool.execute()

    assert result.success is False
    assert result.error_code == "MISSING_PARAMETERS"
