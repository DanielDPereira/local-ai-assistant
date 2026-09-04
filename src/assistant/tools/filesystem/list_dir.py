"""Ferramenta para listagem de diretórios no workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from assistant.tools.base import BaseTool, ToolResult


class ListDirTool(BaseTool):
    """Lista o conteúdo de um diretório dentro do workspace."""

    def __init__(self, workspace_path: str) -> None:
        """Inicializa a ferramenta.

        Args:
            workspace_path: Caminho raiz do workspace.
        """
        self._workspace = Path(workspace_path).resolve()

    @property
    def name(self) -> str:
        return "list_dir"

    @property
    def description(self) -> str:
        return (
            "Lista os arquivos e diretórios dentro de um caminho especificado. "
            "Se nenhum caminho for fornecido, lista a raiz do workspace."
        )

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dir_path": {
                    "type": "string",
                    "description": "Caminho do diretório a ser listado (opcional, padrão = raiz).",
                },
            },
            "required": [],
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        """Lista os arquivos do diretório se estiver no workspace."""
        dir_path = kwargs.get("dir_path", "")

        try:
            target = Path(dir_path)
            if not target.is_absolute():
                target = self._workspace / target

            target = target.resolve()

            # Prevenir path traversal
            if not self._is_within_workspace(target):
                return ToolResult(
                    success=False,
                    output=f"Acesso negado: {dir_path} está fora do workspace.",
                    error_code="ACCESS_DENIED",
                )

            if not target.exists():
                return ToolResult(
                    success=False,
                    output=f"Diretório não encontrado: {dir_path}",
                    error_code="NOT_FOUND",
                )

            if not target.is_dir():
                return ToolResult(
                    success=False,
                    output=f"O caminho aponta para um arquivo, não um diretório: {dir_path}",
                    error_code="NOT_A_DIRECTORY",
                )

            items = []
            for item in target.iterdir():
                item_type = "DIR" if item.is_dir() else "FILE"
                items.append(f"[{item_type}] {item.name}")

            # Ordenar alfabeticamente para previsibilidade
            items.sort()

            content = "(diretório vazio)" if not items else "\n".join(items)

            return ToolResult(
                success=True,
                output=content,
            )
        except PermissionError:
            return ToolResult(
                success=False,
                output=f"Sem permissão para listar o diretório: {dir_path}",
                error_code="PERMISSION_DENIED",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Erro ao listar o diretório: {e}",
                error_code="UNKNOWN_ERROR",
            )

    def _is_within_workspace(self, target: Path) -> bool:
        """Verifica se o target está dentro do workspace."""
        try:
            target.relative_to(self._workspace)
            return True
        except ValueError:
            return False
