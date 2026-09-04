"""Contexto de execução que acompanha a execução inteira do agente."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum


class ExecutionStatus(StrEnum):
    """Status geral de uma execução."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionContext:
    """Acompanha os metadados de uma execução específica do agente."""

    task_type: str
    model: str

    # Gerados automaticamente se não fornecidos
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: float = field(default_factory=time.time)
    status: ExecutionStatus = field(default=ExecutionStatus.RUNNING)

    def mark_completed(self) -> None:
        """Marca a execução como concluída com sucesso."""
        self.status = ExecutionStatus.COMPLETED

    def mark_failed(self) -> None:
        """Marca a execução como falha."""
        self.status = ExecutionStatus.FAILED

    def mark_cancelled(self) -> None:
        """Marca a execução como cancelada."""
        self.status = ExecutionStatus.CANCELLED
