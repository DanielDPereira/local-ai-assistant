"""Tool para pesquisa na web."""

import urllib.parse
import urllib.request
from typing import Any
from urllib.error import URLError

from bs4 import BeautifulSoup

from assistant.tools.base import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    """Ferramenta para realizar pesquisas na web."""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Realiza uma pesquisa na web e retorna os principais resultados com título, URL e um trecho do conteúdo."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "O termo ou frase a ser pesquisado."
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        query = kwargs.get("query")
        if not query:
            return ToolResult(
                success=False, output="O parâmetro 'query' é obrigatório.", error_code="MISSING_PARAMETERS"
            )

        try:
            # Usa DuckDuckGo Lite para obter resultados sem JS
            url = "https://lite.duckduckgo.com/lite/"
            data = urllib.parse.urlencode({"q": str(query)}).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=data,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read()

            soup = BeautifulSoup(html, "html.parser")
            results = []

            # DDG Lite retorna resultados em tabelas/td com class 'result-snippet'
            for tr in soup.find_all("tr"):
                td = tr.find("td", class_="result-snippet")
                if td:
                    # Encontrar a tag anterior que tem o link
                    prev_tr = tr.find_previous_sibling("tr")
                    if prev_tr:
                        a_tag = prev_tr.find("a", class_="result-url")
                        if not a_tag:
                            a_tag = prev_tr.find("a")

                        if a_tag:
                            href = a_tag.get("href", "")
                            link = str(href[0] if isinstance(href, list) else href)
                            title = a_tag.get_text(strip=True)
                            snippet = td.get_text(strip=True)

                            # Ignora links relativos ou do próprio DDG
                            if link.startswith("http") and "duckduckgo.com" not in link:
                                results.append(f"- **{title}**\n  URL: {link}\n  Snippet: {snippet}")

            if not results:
                return ToolResult(
                    success=True,
                    output="Nenhum resultado encontrado para a pesquisa."
                )

            # Limita aos top 5 resultados
            return ToolResult(
                success=True,
                output="\n\n".join(results[:5])
            )
        except URLError as e:
            return ToolResult(
                success=False, output=f"Falha ao pesquisar na web: {e.reason}", error_code="SEARCH_ERROR"
            )
        except Exception as e:
            return ToolResult(
                success=False, output=str(e), error_code="INTERNAL_ERROR"
            )
