"""Modelo base para os eventos de telemetria e observabilidade."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EventType(StrEnum):
    """Tipos de evento no ciclo de vida."""
    SYSTEM_START = "system_start"
    EXECUTION_START = "execution_start"
    EXECUTION_END = "execution_end"
    STATE_TRANSITION = "state_transition"
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    MODEL_REQUEST = "model_request"
    MODEL_RESPONSE = "model_response"
    ERROR = "error"


class EventStatus(StrEnum):
    """Status do evento."""
    OK = "ok"
    ERROR = "error"
    WARNING = "warning"
    IN_PROGRESS = "in_progress"


@dataclass(frozen=True)
class TelemetryEvent:
    """Representa um evento único na telemetria do assistente."""

    execution_id: str
    event_type: EventType
    status: EventStatus
    metadata: dict[str, Any] = field(default_factory=dict)

    # Gerados automaticamente se não fornecidos
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Converte o evento para dicionário."""
        return {
            "event_id": self.event_id,
            "execution_id": self.execution_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "status": self.status.value,
            "metadata": self.metadata,
        }
