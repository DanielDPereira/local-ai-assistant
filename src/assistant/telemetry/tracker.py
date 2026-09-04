"""Rastreador de telemetria responsável por registrar eventos."""

from __future__ import annotations

import logging
from typing import Any

from assistant.telemetry.context import ExecutionContext, ExecutionStatus
from assistant.telemetry.event import EventStatus, EventType, TelemetryEvent

logger = logging.getLogger(__name__)


class TelemetryTracker:
    """Gerencia a gravação e ciclo de vida dos eventos de telemetria."""

    def __init__(self) -> None:
        """Inicializa o rastreador. Por enquanto, mantém eventos em memória."""
        self._events: list[TelemetryEvent] = []

    def get_events(self) -> list[TelemetryEvent]:
        """Retorna todos os eventos registrados (apenas para debug/teste)."""
        return self._events.copy()

    def record_event(self, event: TelemetryEvent) -> None:
        """Registra um evento na coleção."""
        self._events.append(event)
        logger.debug("Evento registrado: %s (%s)", event.event_type, event.execution_id)

    def track_execution_started(self, context: ExecutionContext, metadata: dict[str, Any] | None = None) -> None:
        """Registra o início de uma execução."""
        meta = metadata or {}
        meta.update({"task_type": context.task_type, "model": context.model})
        event = TelemetryEvent(
            execution_id=context.execution_id,
            event_type=EventType.EXECUTION_START,
            status=EventStatus.OK,
            metadata=meta,
        )
        self.record_event(event)

    def track_execution_ended(self, context: ExecutionContext, metadata: dict[str, Any] | None = None) -> None:
        """Registra o fim de uma execução baseando-se no status do contexto."""
        event_type = EventType.EXECUTION_END

        status_map = {
            ExecutionStatus.COMPLETED: EventStatus.OK,
            ExecutionStatus.FAILED: EventStatus.ERROR,
            ExecutionStatus.CANCELLED: EventStatus.WARNING,
            ExecutionStatus.RUNNING: EventStatus.WARNING,  # Se terminar sem mudar o status
        }

        event_status = status_map.get(context.status, EventStatus.WARNING)
        meta = metadata or {}
        meta["final_status"] = context.status.value

        event = TelemetryEvent(
            execution_id=context.execution_id,
            event_type=event_type,
            status=event_status,
            metadata=meta,
        )
        self.record_event(event)
