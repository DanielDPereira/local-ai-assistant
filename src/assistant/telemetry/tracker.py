"""Rastreador de telemetria responsável por registrar eventos."""

from __future__ import annotations

import logging
import time
from typing import Any

from assistant.models.ollama_client import OllamaResponse
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

    def track_model_request(self, context: ExecutionContext, model: str, start_time: float) -> None:
        """Registra o início de uma requisição ao modelo."""
        meta = {
            "model": model,
            "request_start": start_time,
        }
        event = TelemetryEvent(
            execution_id=context.execution_id,
            event_type=EventType.MODEL_REQUEST,
            status=EventStatus.OK,
            metadata=meta,
        )
        self.record_event(event)

    def track_model_response(self, context: ExecutionContext, model: str, start_time: float, response: OllamaResponse | None, error: str | None = None) -> None:
        """Registra a resposta do modelo."""
        end_time = time.monotonic()
        duration = end_time - start_time

        meta: dict[str, Any] = {
            "model": model,
            "duration": duration,
        }

        if response:
            meta["tokens"] = response.eval_count
            meta["tokens_per_second"] = response.tokens_per_second
            status = EventStatus.OK
        else:
            meta["error"] = error
            status = EventStatus.ERROR

        event = TelemetryEvent(
            execution_id=context.execution_id,
            event_type=EventType.MODEL_RESPONSE,
            status=status,
            metadata=meta,
        )
        self.record_event(event)
