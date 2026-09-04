"""Testes para o Harness básico."""

from __future__ import annotations

from assistant.config.settings import HarnessSettings
from assistant.harness.loop import Harness, HarnessState


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
