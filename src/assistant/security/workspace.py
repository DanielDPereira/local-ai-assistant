"""Garantias de limites de workspace para ferramentas."""

from __future__ import annotations

from pathlib import Path


class WorkspaceBoundaryError(Exception):
    """Erro lançado quando uma operação viola os limites do workspace."""


class WorkspaceBoundary:
    """Garante que operações de arquivo fiquem dentro do workspace permitido.

    Todas as ferramentas de I/O devem validar caminhos através desta classe
    antes de executar qualquer operação no sistema de arquivos.
    """

    def __init__(self, workspace_root: str | Path) -> None:
        self.workspace_root = Path(workspace_root).resolve()

    def validate(self, target_path: str | Path) -> Path:
        """Valida se um caminho está dentro do workspace.

        Args:
            target_path: Caminho a ser validado.

        Returns:
            Caminho resolvido (absoluto) e validado.

        Raises:
            WorkspaceBoundaryError: Se o caminho estiver fora do workspace.
        """
        resolved = Path(target_path).resolve()

        try:
            resolved.relative_to(self.workspace_root)
        except ValueError:
            raise WorkspaceBoundaryError(
                f"Acesso negado: '{resolved}' está fora do workspace '{self.workspace_root}'."
            ) from None

        return resolved

    def is_within(self, target_path: str | Path) -> bool:
        """Verifica se um caminho está dentro do workspace sem lançar erro."""
        try:
            self.validate(target_path)
            return True
        except WorkspaceBoundaryError:
            return False
