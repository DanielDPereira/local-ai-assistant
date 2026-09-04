"""Testes para o Harness básico."""

from __future__ import annotations

from unittest import mock

from assistant.config.settings import HarnessSettings
from assistant.harness.loop import Harness, HarnessState
from assistant.validation.runner import ValidationResult, ValidationRunner


class TestHarness:
    """Testes para a classe Harness."""

    def test_default_loop_execution(self) -> None:
        """Testa se o fluxo padrão passa pelos estados corretos e conclui."""
        harness = Harness()
        result = harness.run()

        assert result["success"] is True
        assert result["final_state"] == "COMPLETE"
        # PLAN -> ACT -> OBSERVE -> VERIFY -> COMPLETE = 4 transições
        assert result["iterations"] == 4

    def test_iteration_limit(self) -> None:
        """Testa se o limite de iterações impede loops infinitos."""
        settings = HarnessSettings(max_iterations=3)
        harness = Harness(settings=settings)

        # Cria um loop infinito ACT -> OBSERVE -> ACT
        harness.set_handler(HarnessState.PLAN, lambda: HarnessState.ACT)
        harness.set_handler(HarnessState.ACT, lambda: HarnessState.OBSERVE)
        harness.set_handler(HarnessState.OBSERVE, lambda: HarnessState.ACT)

        result = harness.run()

        assert result["success"] is False
        assert result["final_state"] == "ERROR"
        assert result["iterations"] == 3
        assert result["timeout"] is False

    @mock.patch("time.monotonic")
    def test_global_timeout(self, mock_time: mock.MagicMock) -> None:
        """Testa se o timeout global encerra a execução."""
        settings = HarnessSettings(timeout_seconds=5)
        harness = Harness(settings=settings)

        # Cria um loop simulando demoras
        # time.monotonic é chamado no início, e depois em cada iteração, e por fim no retorno
        mock_time.side_effect = [0.0, 1.0, 3.0, 6.0, 6.0]  # Passou 6 segundos na 3ª iteração

        harness.set_handler(HarnessState.PLAN, lambda: HarnessState.ACT)
        harness.set_handler(HarnessState.ACT, lambda: HarnessState.OBSERVE)
        harness.set_handler(HarnessState.OBSERVE, lambda: HarnessState.ACT)

        result = harness.run()

        assert result["success"] is False
        assert result["final_state"] == "ERROR"
        assert result["timeout"] is True
        assert result["elapsed_time"] == 6.0

    def test_fix_loop_execution(self) -> None:
        """Testa se o fluxo consegue voltar para FIX e concluir depois."""
        harness = Harness()

        # Variável para simular uma falha temporária
        attempts = {"count": 0}

        def mock_verify() -> HarnessState:
            if attempts["count"] == 0:
                attempts["count"] += 1
                return HarnessState.FIX
            return HarnessState.COMPLETE

        harness.set_handler(HarnessState.VERIFY, mock_verify)

        result = harness.run()

        assert result["success"] is True
        assert result["final_state"] == "COMPLETE"
        # PLAN -> ACT -> OBSERVE -> VERIFY -> FIX -> ACT -> OBSERVE -> VERIFY -> COMPLETE
        assert result["iterations"] > 4

    def test_missing_handler_causes_error(self) -> None:
        """Testa erro por falta de handler para um estado."""
        harness = Harness()
        # Remove temporariamente o acesso aos handlers modificando o dunder ou removendo do dict,
        # Mas podemos simular criando um estado custom ou removendo do dict (que é interno, então faremos clear para testar erro)
        harness._handlers.clear()

        result = harness.run()

        assert result["success"] is False
        assert result["final_state"] == "ERROR"

    def test_exception_in_handler_causes_error(self) -> None:
        """Testa que exceções em handlers abortam o fluxo com ERROR."""
        harness = Harness()

        def crashing_handler() -> HarnessState:
            raise ValueError("Something bad happened")

        harness.set_handler(HarnessState.PLAN, crashing_handler)

        result = harness.run()

        assert result["success"] is False
        assert result["final_state"] == "ERROR"

    def test_loop_detection(self) -> None:
        """Testa se ações idênticas repetidas acionam a detecção de loop."""
        harness = Harness()

        def loop_handler() -> HarnessState:
            harness.record_action("read_file(test.py)")
            return HarnessState.OBSERVE

        harness.set_handler(HarnessState.PLAN, lambda: HarnessState.ACT)
        harness.set_handler(HarnessState.ACT, loop_handler)
        harness.set_handler(HarnessState.OBSERVE, lambda: HarnessState.ACT)

        result = harness.run()

        assert result["success"] is False
        assert result["final_state"] == "ERROR"
        assert result["loop_detected"] is True
        assert result["iterations"] < 10

    def test_verify_handler_success(self) -> None:
        """Testa se o estado VERIFY vai para COMPLETE quando as validações passam."""
        mock_runner = mock.MagicMock(spec=ValidationRunner)
        mock_runner.run_all.return_value = {
            "Ruff": ValidationResult(tool="Ruff", success=True, output="", duration=0.1)
        }

        harness = Harness(validation_runner=mock_runner)
        # Ao rodar, PLAN -> ACT -> OBSERVE -> VERIFY (passa) -> COMPLETE
        result = harness.run()

        assert result["success"] is True
        assert result["final_state"] == "COMPLETE"
        mock_runner.run_all.assert_called_once()

    def test_verify_handler_failure(self) -> None:
        """Testa se o estado VERIFY vai para FIX quando uma validação falha."""
        mock_runner = mock.MagicMock(spec=ValidationRunner)

        # 1ª vez falha, 2ª vez sucesso
        mock_runner.run_all.side_effect = [
            {"Ruff": ValidationResult(tool="Ruff", success=False, output="Erro", duration=0.1)},
            {"Ruff": ValidationResult(tool="Ruff", success=True, output="Ok", duration=0.1)}
        ]

        harness = Harness(validation_runner=mock_runner)
        result = harness.run()

        assert result["success"] is True
        assert result["final_state"] == "COMPLETE"
        assert mock_runner.run_all.call_count == 2
