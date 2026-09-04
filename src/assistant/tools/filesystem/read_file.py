"""Ferramenta para leitura de arquivos no workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from assistant.tools.base import BaseTool, ToolResult


class ReadFileTool(BaseTool):
    """Lê o conteúdo de um arquivo dentro do workspace."""

    def __init__(self, workspace_path: str) -> None:
        """Inicializa a ferramenta.

        Args:
            workspace_path: Caminho raiz do workspace. Arquivos fora
                            deste caminho não poderão ser lidos.
        """
        self._workspace = Path(workspace_path).resolve()

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return (
            "Lê o conteúdo de um arquivo texto do workspace. "
            "Requer o caminho relativo ou absoluto do arquivo."
        )

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Caminho do arquivo a ser lido.",
                },
            },
            "required": ["file_path"],
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        """Lê o arquivo se estiver dentro do workspace."""
        file_path = kwargs.get("file_path")
        if not file_path:
            return ToolResult(
                success=False,
                output="O argumento 'file_path' é obrigatório.",
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

            if not target.exists():
                return ToolResult(
                    success=False,
                    output=f"Arquivo não encontrado: {file_path}",
                    error_code="NOT_FOUND",
                )

            if not target.is_file():
                return ToolResult(
                    success=False,
                    output=f"O caminho não é um arquivo: {file_path}",
                    error_code="NOT_A_FILE",
                )

            content = target.read_text(encoding="utf-8")
            return ToolResult(
                success=True,
                output=content,
            )
        except PermissionError:
            return ToolResult(
                success=False,
                output=f"Sem permissão para ler o arquivo: {file_path}",
                error_code="PERMISSION_DENIED",
            )
        except UnicodeDecodeError:
            return ToolResult(
                success=False,
                output=f"O arquivo parece ser binário ou tem encoding inválido: {file_path}",
                error_code="DECODE_ERROR",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Erro ao ler o arquivo: {e}",
                error_code="UNKNOWN_ERROR",
            )

    def _is_within_workspace(self, target: Path) -> bool:
        """Verifica se o target está dentro do workspace."""
        try:
            target.relative_to(self._workspace)
            return True
        except ValueError:
            return False
