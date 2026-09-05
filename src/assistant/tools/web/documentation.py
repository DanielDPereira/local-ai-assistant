"""Tool para busca em documentações."""

from typing import Any

from assistant.tools.base import BaseTool, ToolResult
from assistant.tools.web.reader import UrlReaderTool
from assistant.tools.web.search import WebSearchTool


class DocumentationLookupTool(BaseTool):
    """Ferramenta para buscar em documentações específicas na web."""

    @property
    def name(self) -> str:
        return "docs_lookup"

    @property
    def description(self) -> str:
        return "Busca um termo em uma documentação específica (URL base) e retorna o conteúdo principal do melhor resultado."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termo a ser pesquisado (ex: 'fastapi background tasks')."
                },
                "docs_url": {
                    "type": "string",
                    "description": "URL base da documentação (ex: 'fastapi.tiangolo.com')."
                }
            },
            "required": ["query", "docs_url"],
            "additionalProperties": False
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        query = kwargs.get("query")
        docs_url = kwargs.get("docs_url")

        if not query or not docs_url:
            return ToolResult(
                success=False,
                output="Os parâmetros 'query' e 'docs_url' são obrigatórios.",
                error_code="MISSING_PARAMETERS"
            )

        # Prepara a query de pesquisa restrita ao site
        search_query = f"site:{docs_url} {query}"

        search_tool = WebSearchTool()
        search_result = search_tool.execute(query=search_query)

        if not search_result.success:
            return search_result

        output_str = str(search_result.output)
        if "Nenhum resultado" in output_str:
            return ToolResult(
                success=True,
                output=f"Nenhum resultado encontrado para '{query}' em {docs_url}."
            )

        # Extrai a primeira URL do resultado (formato: - **Titulo**\n  URL: <link>)
        first_url = None
        for line in output_str.splitlines():
            line = line.strip()
            if line.startswith("URL:"):
                first_url = line.replace("URL:", "").strip()
                break

        if not first_url:
            return ToolResult(
                success=False,
                output="Não foi possível extrair a URL do resultado da pesquisa.",
                error_code="PARSING_ERROR"
            )

        # Usa o UrlReader para ler a página da documentação
        reader_tool = UrlReaderTool()
        reader_result = reader_tool.execute(url=first_url)

        if not reader_result.success:
            return ToolResult(
                success=False,
                output=f"Falha ao ler a documentação ({first_url}): {reader_result.output}",
                error_code="READER_ERROR"
            )

        return ToolResult(
            success=True,
            output=f"Fonte: {first_url}\n\n{reader_result.output}"
        )
