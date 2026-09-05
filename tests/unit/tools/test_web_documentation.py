"""Testes para docs_lookup."""

from unittest.mock import MagicMock, patch

from assistant.tools.base import ToolResult
from assistant.tools.web.documentation import DocumentationLookupTool


def test_docs_lookup_properties() -> None:
    tool = DocumentationLookupTool()
    assert tool.name == "docs_lookup"
    assert "query" in tool.schema["required"]
    assert "docs_url" in tool.schema["required"]


@patch("assistant.tools.web.documentation.UrlReaderTool")
@patch("assistant.tools.web.documentation.WebSearchTool")
def test_docs_lookup_success(mock_search_class: MagicMock, mock_reader_class: MagicMock) -> None:
    mock_search = mock_search_class.return_value
    mock_search.execute.return_value = ToolResult(
        success=True,
        output="- **Doc**\n  URL: https://docs.com/page\n  Snippet: text"
    )

    mock_reader = mock_reader_class.return_value
    mock_reader.execute.return_value = ToolResult(
        success=True,
        output="Conteudo da pagina"
    )

    tool = DocumentationLookupTool()
    result = tool.execute(query="test", docs_url="docs.com")

    assert result.success is True
    assert "https://docs.com/page" in result.output
    assert "Conteudo da pagina" in result.output

    mock_search.execute.assert_called_once_with(query="site:docs.com test")
    mock_reader.execute.assert_called_once_with(url="https://docs.com/page")


@patch("assistant.tools.web.documentation.WebSearchTool")
def test_docs_lookup_no_results(mock_search_class: MagicMock) -> None:
    mock_search = mock_search_class.return_value
    mock_search.execute.return_value = ToolResult(
        success=True,
        output="Nenhum resultado encontrado para a pesquisa."
    )

    tool = DocumentationLookupTool()
    result = tool.execute(query="test", docs_url="docs.com")

    assert result.success is True
    assert "Nenhum resultado" in result.output


def test_docs_lookup_missing_params() -> None:
    tool = DocumentationLookupTool()
    result = tool.execute(query="test")

    assert result.success is False
    assert result.error_code == "MISSING_PARAMETERS"
