"""Testes para a ferramenta de leitura de arquivos."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from assistant.tools.filesystem.read_file import ReadFileTool


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Fixture que provê um workspace temporário."""
    return tmp_path


@pytest.fixture
def tool(workspace: Path) -> ReadFileTool:
    """Fixture que provê o ReadFileTool."""
    return ReadFileTool(workspace_path=str(workspace))


class TestReadFileTool:
    """Testes para ReadFileTool."""

    def test_read_existing_file_relative(self, tool: ReadFileTool, workspace: Path) -> None:
        """Lê arquivo com caminho relativo."""
        test_file = workspace / "test.txt"
        test_file.write_text("Hello World", encoding="utf-8")

        result = tool.execute(file_path="test.txt")
        assert result.success is True
        assert result.output == "Hello World"

    def test_read_existing_file_absolute(self, tool: ReadFileTool, workspace: Path) -> None:
        """Lê arquivo com caminho absoluto."""
        test_file = workspace / "test.txt"
        test_file.write_text("Hello World", encoding="utf-8")

        result = tool.execute(file_path=str(test_file))
        assert result.success is True
        assert result.output == "Hello World"

    def test_missing_argument(self, tool: ReadFileTool) -> None:
        """Requer file_path."""
        result = tool.execute()
        assert result.success is False
        assert result.error_code == "MISSING_ARGUMENT"

    def test_file_not_found(self, tool: ReadFileTool) -> None:
        """Erro para arquivo que não existe."""
        result = tool.execute(file_path="missing.txt")
        assert result.success is False
        assert result.error_code == "NOT_FOUND"

    def test_is_directory(self, tool: ReadFileTool, workspace: Path) -> None:
        """Erro ao tentar ler um diretório."""
        target_dir = workspace / "folder"
        target_dir.mkdir()

        result = tool.execute(file_path="folder")
        assert result.success is False
        assert result.error_code == "NOT_A_FILE"

    def test_path_traversal(self, tool: ReadFileTool, workspace: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
        """Impede path traversal para fora do workspace."""
        out_of_workspace = tmp_path_factory.mktemp("other")
        secret_file = out_of_workspace / "secret.txt"
        secret_file.write_text("secrets", encoding="utf-8")

        # Caminho absoluto
        result1 = tool.execute(file_path=str(secret_file))
        assert result1.success is False
        assert result1.error_code == "ACCESS_DENIED"

        # Caminho relativo com ../
        rel_path = os.path.relpath(secret_file, workspace)
        result2 = tool.execute(file_path=rel_path)
        assert result2.success is False
        assert result2.error_code == "ACCESS_DENIED"

    def test_decode_error(self, tool: ReadFileTool, workspace: Path) -> None:
        """Lida com arquivos não-texto (binários)."""
        bin_file = workspace / "image.bin"
        bin_file.write_bytes(b"\xff\xfe\xff")

        result = tool.execute(file_path="image.bin")
        assert result.success is False
        assert result.error_code == "DECODE_ERROR"

    def test_permission_error(self, tool: ReadFileTool, workspace: Path) -> None:
        """Lida com erro de permissão."""
        import stat

        test_file = workspace / "noperm.txt"
        test_file.write_text("secret", encoding="utf-8")

        # Remove all permissions for the user
        test_file.chmod(stat.S_IWRITE)

        try:
            # Em alguns sistemas de arquivo/Windows como root, read ainda pode funcionar,
            # então precisamos usar um patch para garantir que testamos o tratamento do erro
            from unittest import mock
            with mock.patch("pathlib.Path.read_text", side_effect=PermissionError("denied")):
                result = tool.execute(file_path="noperm.txt")

            assert result.success is False
            assert result.error_code == "PERMISSION_DENIED"
        finally:
            test_file.chmod(stat.S_IREAD | stat.S_IWRITE)
