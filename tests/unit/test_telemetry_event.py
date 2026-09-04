"""Testes para o modelo de eventos de telemetria."""

from __future__ import annotations

import time

from assistant.telemetry.event import EventStatus, EventType, TelemetryEvent


class TestTelemetryEvent:
    """Testes para a classe TelemetryEvent."""

    def test_event_creation(self) -> None:
        """Testa se um evento é criado com defaults corretos."""
        event = TelemetryEvent(
            execution_id="exec-123",
            event_type=EventType.SYSTEM_START,
            status=EventStatus.OK
        )

        assert event.execution_id == "exec-123"
        assert event.event_type == EventType.SYSTEM_START
        assert event.status == EventStatus.OK

        # Defaults
        assert event.event_id is not None
        assert isinstance(event.event_id, str)
        assert len(event.event_id) > 10
        assert event.timestamp > 0
        assert isinstance(event.timestamp, float)
        assert event.metadata == {}

    def test_event_to_dict(self) -> None:
        """Verifica serialização para dicionário."""
        custom_time = time.time()
        event = TelemetryEvent(
            event_id="evt-456",
            execution_id="exec-123",
            timestamp=custom_time,
            event_type=EventType.ERROR,
            status=EventStatus.ERROR,
            metadata={"reason": "timeout"}
        )

        data = event.to_dict()

        assert data["event_id"] == "evt-456"
        assert data["execution_id"] == "exec-123"
        assert data["timestamp"] == custom_time
        assert data["event_type"] == "error"
        assert data["status"] == "error"
        assert data["metadata"] == {"reason": "timeout"}
