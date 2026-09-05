"""Cliente para interagir com a API do GitHub."""

import json
import os
import urllib.error
import urllib.request
from typing import Any


class GitHubClient:
    """Cliente simples para a API REST do GitHub."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None) -> None:
        """Inicializa o cliente do GitHub.


        Args:
            token: Token de acesso do GitHub. Se não fornecido, busca na env GITHUB_TOKEN.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN não configurado no ambiente.")

    def _make_request(
        self, endpoint: str, method: str = "GET", data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Faz uma requisição para a API do GitHub.


        Args:
            endpoint: Caminho do endpoint (ex: /repos/user/repo).
            method: Método HTTP (GET, POST, PATCH, etc).
            data: Dados para enviar no corpo da requisição (para POST/PATCH).


        Returns:
            Dicionário com a resposta JSON da API.


        Raises:
            Exception: Se ocorrer erro na requisição HTTP ou se a API retornar erro.
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}",
            "User-Agent": "Local-AI-Assistant",
        }

        req_data = None
        if data is not None:
            req_data = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as response:
                body = response.read().decode("utf-8")
                if not body:
                    return {}
                return dict(json.loads(body))
        except urllib.error.HTTPError as e:
            try:
                error_body = e.read().decode("utf-8")
                error_json = json.loads(error_body)
                error_msg = error_json.get("message", str(e))
            except Exception:
                error_msg = str(e)
            raise Exception(f"GitHub API Error ({e.code}): {error_msg}") from e
        except urllib.error.URLError as e:
            raise Exception(f"Erro de rede ao contatar GitHub: {e.reason}") from e

    def get_issue(self, repo: str, issue_number: int) -> dict[str, Any]:
        """Obtém detalhes de uma issue."""
        return self._make_request(f"/repos/{repo}/issues/{issue_number}")

    def create_issue(self, repo: str, title: str, body: str) -> dict[str, Any]:
        """Cria uma nova issue no repositório."""
        data = {"title": title, "body": body}
        return self._make_request(f"/repos/{repo}/issues", method="POST", data=data)

    def create_pull_request(
        self, repo: str, title: str, head: str, base: str, body: str = ""
    ) -> dict[str, Any]:
        """Cria um novo Pull Request."""
        data = {"title": title, "head": head, "base": base, "body": body}
        return self._make_request(f"/repos/{repo}/pulls", method="POST", data=data)
