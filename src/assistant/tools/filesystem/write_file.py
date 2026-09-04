"""Ferramenta para escrita de arquivos no workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from assistant.tools.base import BaseTool, ToolResult


class WriteFileTool(BaseTool):
    """Cria ou sobrescreve um arquivo dentro do workspace."""

    def __init__(self, workspace_path: str) -> None:
        """Inicializa a ferramenta.

        Args:
            workspace_path: Caminho raiz do workspace.
        """
        self._workspace = Path(workspace_path).resolve()

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return (
            "Escreve conteúdo em um arquivo no workspace. "
            "Se o arquivo não existir, ele será criado. "
            "Se existir, será sobrescrito com o novo conteúdo."
        )

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Caminho relativo ou absoluto do arquivo.",
                },
                "content": {
                    "type": "string",
                    "description": "Conteúdo a ser escrito no arquivo.",
                },
            },
            "required": ["file_path", "content"],
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        """Escreve o arquivo garantindo que está no workspace."""
        file_path = kwargs.get("file_path")
        content = kwargs.get("content")

        if not file_path:
            return ToolResult(
                success=False,
                output="O argumento 'file_path' é obrigatório.",
                error_code="MISSING_ARGUMENT",
            )
        if content is None:
            return ToolResult(
                success=False,
                output="O argumento 'content' é obrigatório.",
                error_code="MISSING_ARGUMENT",
            )

        try:
            target = Path(file_path)
            if not target.is_absolute():
                target = self._workspace / target

            target = target.resolve()

            # Prevenir path traversal
            if not self._is_within_workspace(target):
                return ToolResult(
                    success=False,
                    output=f"Acesso negado: {file_path} está fora do workspace.",
                    error_code="ACCESS_DENIED",
                )

            if target.is_dir():
                return ToolResult(
                    success=False,
                    output=f"O caminho aponta para um diretório, não um arquivo: {file_path}",
                    error_code="IS_A_DIRECTORY",
                )

            # Criar diretórios pai se não existirem
            target.parent.mkdir(parents=True, exist_ok=True)

            target.write_text(content, encoding="utf-8")
            return ToolResult(
                success=True,
                output=f"Arquivo escrito com sucesso: {file_path}",
            )
        except PermissionError:
            return ToolResult(
                success=False,
                output=f"Sem permissão para escrever no arquivo: {file_path}",
                error_code="PERMISSION_DENIED",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Erro ao escrever no arquivo: {e}",
                error_code="UNKNOWN_ERROR",
            )

    def _is_within_workspace(self, target: Path) -> bool:
        """Verifica se o target está dentro do workspace."""
        try:
            target.relative_to(self._workspace)
            return True
        except ValueError:
            return False
