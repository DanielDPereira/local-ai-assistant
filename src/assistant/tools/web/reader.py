"""Tool para leitura de URLs."""

import urllib.request
from typing import Any
from urllib.error import URLError

from bs4 import BeautifulSoup

from assistant.tools.base import BaseTool, ToolResult


class UrlReaderTool(BaseTool):
    """Ferramenta para extrair o texto principal de uma URL."""

    @property
    def name(self) -> str:
        return "url_reader"

    @property
    def description(self) -> str:
        return "Lê uma URL da web e extrai o conteúdo de texto principal, removendo HTML desnecessário (scripts, estilos, navegação)."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL da página web a ser lida."
                }
            },
            "required": ["url"],
            "additionalProperties": False
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        url = kwargs.get("url")
        if not url:
            return ToolResult(
                success=False, output="O parâmetro 'url' é obrigatório.", error_code="MISSING_PARAMETERS"
            )

        try:
            req = urllib.request.Request(
                str(url),
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read()

            soup = BeautifulSoup(html, "html.parser")

            # Remove tags não textuais
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()

            # Pega o texto e limpa espaços
            text = soup.get_text(separator="\n")
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = "\n".join(chunk for chunk in chunks if chunk)

            if len(clean_text) > 4000:
                clean_text = clean_text[:4000] + "\n\n...[Conteúdo truncado]..."

            return ToolResult(
                success=True,
                output=clean_text
            )
        except URLError as e:
            return ToolResult(
                success=False, output=f"Falha ao carregar a URL: {e.reason}", error_code="URL_ERROR"
            )
        except Exception as e:
            return ToolResult(
                success=False, output=str(e), error_code="INTERNAL_ERROR"
            )
