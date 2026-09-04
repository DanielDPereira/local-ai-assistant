"""Testes para o ExecutionContext."""

from __future__ import annotations

from assistant.telemetry.context import ExecutionContext, ExecutionStatus


class TestExecutionContext:
    """Testes para a classe ExecutionContext."""

    def test_context_creation(self) -> None:
        """Testa a inicialização do contexto com os padrões corretos."""
        ctx = ExecutionContext(task_type="coding", model="qwen2.5-coder:3b")

        assert ctx.task_type == "coding"
        assert ctx.model == "qwen2.5-coder:3b"
        assert ctx.status == ExecutionStatus.RUNNING
        assert ctx.execution_id is not None
        assert isinstance(ctx.execution_id, str)
        assert ctx.started_at > 0

    def test_status_transitions(self) -> None:
        """Verifica a mudança de status."""
        ctx = ExecutionContext(task_type="general", model="qwen")

        ctx.mark_completed()
        assert ctx.status == ExecutionStatus.COMPLETED

        ctx.mark_failed()
        assert ctx.status == ExecutionStatus.FAILED

        ctx.mark_cancelled()
        assert ctx.status == ExecutionStatus.CANCELLED
