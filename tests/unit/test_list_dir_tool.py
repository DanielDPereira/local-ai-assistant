"""Testes para a ferramenta de listagem de diretórios."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from assistant.tools.filesystem.list_dir import ListDirTool


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Fixture que provê um workspace temporário."""
    return tmp_path


@pytest.fixture
def tool(workspace: Path) -> ListDirTool:
    """Fixture que provê o ListDirTool."""
    return ListDirTool(workspace_path=str(workspace))


class TestListDirTool:
    """Testes para ListDirTool."""

    def test_list_root_directory(self, tool: ListDirTool, workspace: Path) -> None:
        """Lista a raiz do workspace (padrão se nenhum argumento)."""
        (workspace / "file.txt").write_text("Hello", encoding="utf-8")
        (workspace / "folder").mkdir()

        result = tool.execute()

        assert result.success is True
        assert "[DIR] folder" in result.output
        assert "[FILE] file.txt" in result.output

    def test_list_sub_directory(self, tool: ListDirTool, workspace: Path) -> None:
        """Lista um subdiretório do workspace."""
        sub_dir = workspace / "sub"
        sub_dir.mkdir()
        (sub_dir / "child.txt").write_text("Child", encoding="utf-8")

        result = tool.execute(dir_path="sub")

        assert result.success is True
        assert "[FILE] child.txt" in result.output

    def test_list_empty_directory(self, tool: ListDirTool, workspace: Path) -> None:
        """Lista um diretório vazio."""
        result = tool.execute()

        assert result.success is True
        assert result.output == "(diretório vazio)"

    def test_not_found(self, tool: ListDirTool) -> None:
        """Erro se o diretório não existir."""
        result = tool.execute(dir_path="missing")

        assert result.success is False
        assert result.error_code == "NOT_FOUND"

    def test_is_file(self, tool: ListDirTool, workspace: Path) -> None:
        """Erro ao tentar listar um arquivo em vez de diretório."""
        test_file = workspace / "test.txt"
        test_file.write_text("Hello", encoding="utf-8")

        result = tool.execute(dir_path="test.txt")
        assert result.success is False
        assert result.error_code == "NOT_A_DIRECTORY"

    def test_path_traversal(self, tool: ListDirTool, workspace: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
        """Impede path traversal para fora do workspace."""
        out_of_workspace = tmp_path_factory.mktemp("other")

        # Caminho absoluto
        result1 = tool.execute(dir_path=str(out_of_workspace))
        assert result1.success is False
        assert result1.error_code == "ACCESS_DENIED"

        # Caminho relativo com ../
        rel_path = os.path.relpath(out_of_workspace, workspace)
        result2 = tool.execute(dir_path=rel_path)
        assert result2.success is False
        assert result2.error_code == "ACCESS_DENIED"

    def test_permission_error(self, tool: ListDirTool, workspace: Path) -> None:
        """Lida com erro de permissão."""
        import stat

        test_dir = workspace / "noperm"
        test_dir.mkdir()

        try:
            # Em alguns sistemas (Windows/root) read_text gera permissão negada
            # de formas diferentes. Para iterdir também forçamos o erro com mock
            from unittest import mock
            with mock.patch("pathlib.Path.iterdir", side_effect=PermissionError("denied")):
                result = tool.execute(dir_path="noperm")

            assert result.success is False
            assert result.error_code == "PERMISSION_DENIED"
        finally:
            test_dir.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
