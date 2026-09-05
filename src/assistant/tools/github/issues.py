"""Tool para gerenciar issues do GitHub."""

import json
from typing import Any

from assistant.tools.base import BaseTool, ToolResult
from assistant.tools.github.client import GitHubClient


class GitHubIssuesTool(BaseTool):
    """Ferramenta para buscar e criar Issues no GitHub."""

    @property
    def name(self) -> str:
        return "github_issues"

    @property
    def description(self) -> str:
        return "Permite consultar uma issue existente ou criar uma nova em um repositório do GitHub."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["get", "create"],
                    "description": "Ação a realizar: 'get' para consultar, 'create' para criar."
                },
                "repo": {
                    "type": "string",
                    "description": "Nome do repositório no formato 'owner/repo'."
                },
                "issue_number": {
                    "type": "integer",
                    "description": "Número da issue (obrigatório para action='get')."
                },
                "title": {
                    "type": "string",
                    "description": "Título da issue (obrigatório para action='create')."
                },
                "body": {
                    "type": "string",
                    "description": "Corpo/descrição da issue."
                }
            },
            "required": ["action", "repo"],
            "additionalProperties": False
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        action = kwargs.get("action")
        repo = kwargs.get("repo")

        try:
            client = GitHubClient()
        except ValueError as e:
            return ToolResult(success=False, output=str(e), error_code="MISSING_GITHUB_TOKEN")

        try:
            if action == "get":
                issue_number = kwargs.get("issue_number")
                if not issue_number:
                    return ToolResult(success=False, output="issue_number é obrigatório para action='get'", error_code="MISSING_PARAMETERS")

                result = client.get_issue(str(repo), int(issue_number))
                return ToolResult(success=True, output=json.dumps(result, indent=2), data=result)

            elif action == "create":
                title = kwargs.get("title")
                body = kwargs.get("body", "")
                if not title:
                    return ToolResult(success=False, output="title é obrigatório para action='create'", error_code="MISSING_PARAMETERS")

                result = client.create_issue(str(repo), str(title), str(body))
                return ToolResult(success=True, output=f"Issue criada com sucesso: {result.get('html_url')}", data=result)

            else:
                return ToolResult(success=False, output=f"Ação inválida: {action}", error_code="INVALID_ACTION")

        except Exception as e:
            return ToolResult(success=False, output=str(e), error_code="GITHUB_API_ERROR")
