"""Testes para o TelemetryTracker."""

from __future__ import annotations

import time

from assistant.models.ollama_client import OllamaResponse
from assistant.telemetry.context import ExecutionContext
from assistant.telemetry.event import EventStatus, EventType, TelemetryEvent
from assistant.telemetry.tracker import TelemetryTracker


class TestTelemetryTracker:
    """Testes para TelemetryTracker."""

    def test_record_event(self) -> None:
        """Verifica o registro de um evento genérico."""
        tracker = TelemetryTracker()
        event = TelemetryEvent(execution_id="123", event_type=EventType.SYSTEM_START, status=EventStatus.OK)

        tracker.record_event(event)

        events = tracker.get_events()
        assert len(events) == 1
        assert events[0] == event

    def test_track_execution_lifecycle(self) -> None:
        """Verifica registro do início e fim de execução."""
        tracker = TelemetryTracker()
        context = ExecutionContext(task_type="coding", model="qwen")

        # Start
        tracker.track_execution_started(context, metadata={"trigger": "manual"})

        events = tracker.get_events()
        assert len(events) == 1
        start_evt = events[0]
        assert start_evt.execution_id == context.execution_id
        assert start_evt.event_type == EventType.EXECUTION_START
        assert start_evt.status == EventStatus.OK
        assert start_evt.metadata["task_type"] == "coding"
        assert start_evt.metadata["trigger"] == "manual"

        # End
        context.mark_completed()
        tracker.track_execution_ended(context)

        events = tracker.get_events()
        assert len(events) == 2
        end_evt = events[1]
        assert end_evt.execution_id == context.execution_id
        assert end_evt.event_type == EventType.EXECUTION_END
        assert end_evt.status == EventStatus.OK
        assert end_evt.metadata["final_status"] == "completed"

    def test_track_execution_failed(self) -> None:
        """Verifica registro de término com falha."""
        tracker = TelemetryTracker()
        context = ExecutionContext(task_type="coding", model="qwen")

        context.mark_failed()
        tracker.track_execution_ended(context, metadata={"error": "timeout"})

        events = tracker.get_events()
        assert len(events) == 1
        end_evt = events[0]
        assert end_evt.event_type == EventType.EXECUTION_END
        assert end_evt.status == EventStatus.ERROR
        assert end_evt.metadata["error"] == "timeout"
        assert end_evt.metadata["final_status"] == "failed"

    def test_track_model(self) -> None:
        """Verifica o registro de request e response de modelo."""
        tracker = TelemetryTracker()
        context = ExecutionContext(task_type="coding", model="qwen")
        start = time.monotonic()

        # Request
        tracker.track_model_request(context, model="qwen", start_time=start)

        events = tracker.get_events()
        assert len(events) == 1
        req_evt = events[0]
        assert req_evt.event_type == EventType.MODEL_REQUEST
        assert req_evt.metadata["model"] == "qwen"

        # Response (Sucesso)
        response = OllamaResponse(
            content="ok", model="qwen", done=True, eval_count=100, tokens_per_second=25.0
        )
        tracker.track_model_response(context, model="qwen", start_time=start, response=response)

        events = tracker.get_events()
        assert len(events) == 2
        res_evt = events[1]
        assert res_evt.event_type == EventType.MODEL_RESPONSE
        assert res_evt.status == EventStatus.OK
        assert res_evt.metadata["tokens"] == 100
        assert res_evt.metadata["tokens_per_second"] == 25.0
        assert res_evt.metadata["duration"] >= 0

        # Response (Erro)
        tracker.track_model_response(context, model="qwen", start_time=start, response=None, error="Timeout")
        events = tracker.get_events()
        err_evt = events[2]
        assert err_evt.event_type == EventType.MODEL_RESPONSE
        assert err_evt.status == EventStatus.ERROR
        assert err_evt.metadata["error"] == "Timeout"
