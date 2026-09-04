"""Testes para a ferramenta de escrita de arquivos."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from assistant.tools.filesystem.write_file import WriteFileTool


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Fixture que provê um workspace temporário."""
    return tmp_path


@pytest.fixture
def tool(workspace: Path) -> WriteFileTool:
    """Fixture que provê o WriteFileTool."""
    return WriteFileTool(workspace_path=str(workspace))


class TestWriteFileTool:
    """Testes para WriteFileTool."""

    def test_write_new_file_relative(self, tool: WriteFileTool, workspace: Path) -> None:
        """Escreve um novo arquivo usando caminho relativo."""
        result = tool.execute(file_path="new_file.txt", content="Hello!")

        assert result.success is True
        assert (workspace / "new_file.txt").exists()
        assert (workspace / "new_file.txt").read_text(encoding="utf-8") == "Hello!"

    def test_write_overwrite_file(self, tool: WriteFileTool, workspace: Path) -> None:
        """Sobrescreve arquivo existente."""
        test_file = workspace / "test.txt"
        test_file.write_text("Old content", encoding="utf-8")

        result = tool.execute(file_path="test.txt", content="New content")

        assert result.success is True
        assert test_file.read_text(encoding="utf-8") == "New content"

    def test_write_creates_directories(self, tool: WriteFileTool, workspace: Path) -> None:
        """Cria diretórios pais caso não existam."""
        result = tool.execute(file_path="deep/folder/file.txt", content="Deep")

        assert result.success is True
        assert (workspace / "deep" / "folder" / "file.txt").exists()
        assert (workspace / "deep" / "folder" / "file.txt").read_text(encoding="utf-8") == "Deep"

    def test_missing_arguments(self, tool: WriteFileTool) -> None:
        """Erro se argumentos estiverem ausentes."""
        result1 = tool.execute(content="Hello")
        assert result1.success is False
        assert result1.error_code == "MISSING_ARGUMENT"

        result2 = tool.execute(file_path="test.txt")
        assert result2.success is False
        assert result2.error_code == "MISSING_ARGUMENT"

    def test_is_directory(self, tool: WriteFileTool, workspace: Path) -> None:
        """Erro ao tentar escrever onde já existe um diretório com mesmo nome."""
        target_dir = workspace / "folder"
        target_dir.mkdir()

        result = tool.execute(file_path="folder", content="Content")
        assert result.success is False
        assert result.error_code == "IS_A_DIRECTORY"

    def test_path_traversal(self, tool: WriteFileTool, workspace: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
        """Impede path traversal para fora do workspace."""
        out_of_workspace = tmp_path_factory.mktemp("other")
        secret_file = out_of_workspace / "hacked.txt"

        # Caminho absoluto
        result1 = tool.execute(file_path=str(secret_file), content="Hacked")
        assert result1.success is False
        assert result1.error_code == "ACCESS_DENIED"
        assert not secret_file.exists()

        # Caminho relativo com ../
        rel_path = os.path.relpath(secret_file, workspace)
        result2 = tool.execute(file_path=rel_path, content="Hacked")
        assert result2.success is False
        assert result2.error_code == "ACCESS_DENIED"
        assert not secret_file.exists()

    def test_permission_error(self, tool: WriteFileTool, workspace: Path) -> None:
        """Lida com erro de permissão."""
        import stat

        test_file = workspace / "readonly.txt"
        test_file.write_text("content", encoding="utf-8")
        test_file.chmod(stat.S_IREAD)  # Apenas leitura

        try:
            # Em alguns sistemas (Windows/root) isso pode não gerar PermissionError nativamente,
            # forçamos via mock para garantir o tratamento correto do bloco except.
            from unittest import mock
            with mock.patch("pathlib.Path.write_text", side_effect=PermissionError("denied")):
                result = tool.execute(file_path="readonly.txt", content="New")

            assert result.success is False
            assert result.error_code == "PERMISSION_DENIED"
        finally:
            test_file.chmod(stat.S_IREAD | stat.S_IWRITE)
