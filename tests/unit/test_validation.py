"""Testes para o ValidationRunner."""

from __future__ import annotations

from unittest import mock

from assistant.validation.runner import ValidationResult, ValidationRunner


class TestValidationRunner:
    """Testes para o ValidationRunner."""

    def test_run_tool_success(self) -> None:
        """Testa sucesso em rodar uma ferramenta."""
        runner = ValidationRunner(workspace_path=".")

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.MagicMock(returncode=0, stdout="Success", stderr="")
            result = runner._run_tool("Teste", "echo Success")

            assert result.success is True
            assert result.tool == "Teste"
            assert "Success" in result.output
            assert result.duration >= 0

    def test_run_tool_failure(self) -> None:
        """Testa falha ao rodar uma ferramenta (retorno != 0)."""
        runner = ValidationRunner(workspace_path=".")

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.MagicMock(returncode=1, stdout="", stderr="Error msg")
            result = runner._run_tool("Teste", "false")

            assert result.success is False
            assert result.tool == "Teste"
            assert "[STDERR]\nError msg" in result.output

    def test_run_tool_exception(self) -> None:
        """Testa exceção durante execução do subprocess."""
        runner = ValidationRunner(workspace_path=".")

        with mock.patch("subprocess.run", side_effect=OSError("OS Error")):
            result = runner._run_tool("Teste", "cmd")

            assert result.success is False
            assert "Erro fatal executando Teste: OS Error" in result.output

    def test_run_all_tools(self) -> None:
        """Verifica se run_all aciona todas as ferramentas mapeadas."""
        runner = ValidationRunner(workspace_path=".")

        mock_result = ValidationResult(tool="mock", success=True, output="", duration=1.0)

        with mock.patch.object(runner, "run_ruff", return_value=mock_result) as m_ruff, \
             mock.patch.object(runner, "run_mypy", return_value=mock_result) as m_mypy, \
             mock.patch.object(runner, "run_pytest", return_value=mock_result) as m_pytest, \
             mock.patch.object(runner, "run_build", return_value=mock_result) as m_build:

            results = runner.run_all()

            assert "Ruff" in results
            assert "Mypy" in results
            assert "Pytest" in results
            assert "Build" in results
            m_ruff.assert_called_once()
            m_mypy.assert_called_once()
            m_pytest.assert_called_once()
            m_build.assert_called_once()
