"""Testes de sanidade do pacote assistant."""

import assistant


class TestPackage:
    """Verificar que o pacote assistant pode ser importado corretamente."""

    def test_package_importable(self) -> None:
        """O pacote assistant deve ser importável."""
        assert assistant is not None

    def test_version_defined(self) -> None:
        """O pacote deve expor __version__."""
        assert hasattr(assistant, "__version__")
        assert isinstance(assistant.__version__, str)
        assert len(assistant.__version__) > 0

    def test_version_format(self) -> None:
        """A versão deve seguir formato semântico (X.Y.Z)."""
        parts = assistant.__version__.split(".")
        assert len(parts) == 3
        for part in parts:
            assert part.isdigit()

    def test_subpackages_importable(self) -> None:
        """Todos os subpacotes devem ser importáveis."""
        import assistant.agent
        import assistant.api
        import assistant.api.metrics
        import assistant.config
        import assistant.database
        import assistant.harness
        import assistant.mcp
        import assistant.memory
        import assistant.models
        import assistant.observability
        import assistant.observability.events
        import assistant.observability.metrics
        import assistant.observability.repositories
        import assistant.observability.telemetry
        import assistant.policies
        import assistant.skills
        import assistant.tools
        import assistant.tools.filesystem
        import assistant.tools.git
        import assistant.tools.github
        import assistant.tools.terminal
        import assistant.tools.web

        # Verificar que todos foram importados sem erro
        assert assistant.agent is not None
        assert assistant.tools.filesystem is not None
        assert assistant.observability.telemetry is not None
