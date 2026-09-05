"""Tool para gerenciar Pull Requests do GitHub."""

from typing import Any

from assistant.tools.base import BaseTool, ToolResult
from assistant.tools.github.client import GitHubClient


class GitHubPRTool(BaseTool):
    """Ferramenta para criar Pull Requests no GitHub."""

    @property
    def name(self) -> str:
        return "github_pr"

    @property
    def description(self) -> str:
        return "Permite criar um novo Pull Request em um repositório do GitHub."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Nome do repositório no formato 'owner/repo'."
                },
                "title": {
                    "type": "string",
                    "description": "Título do Pull Request."
                },
                "head": {
                    "type": "string",
                    "description": "Nome da branch com as mudanças (ex: 'feature/nova-branch')."
                },
                "base": {
                    "type": "string",
                    "description": "Nome da branch destino (ex: 'main')."
                },
                "body": {
                    "type": "string",
                    "description": "Corpo/descrição do Pull Request."
                }
            },
            "required": ["repo", "title", "head", "base"],
            "additionalProperties": False
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        repo = kwargs.get("repo")
        title = kwargs.get("title")
        head = kwargs.get("head")
        base = kwargs.get("base")
        body = kwargs.get("body", "")

        try:
            client = GitHubClient()
        except ValueError as e:
            return ToolResult(success=False, output=str(e), error_code="MISSING_GITHUB_TOKEN")

        try:
            result = client.create_pull_request(
                repo=str(repo),
                title=str(title),
                head=str(head),
                base=str(base),
                body=str(body)
            )
            return ToolResult(
                success=True,
                output=f"Pull Request criado com sucesso: {result.get('html_url')}",
                data=result
            )
        except Exception as e:
            return ToolResult(success=False, output=str(e), error_code="GITHUB_API_ERROR")
