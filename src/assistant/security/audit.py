"""Trilha de auditoria para operações de segurança."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path


class AuditTrail:
    """Registra todas as operações críticas para auditoria.

    Cada evento contém timestamp, tipo da operação, resultado
    e detalhes relevantes para análise posterior.
    """

    def __init__(self, log_file: str | Path) -> None:
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        event_type: str,
        action: str,
        result: str,
        details: str = "",
    ) -> None:
        """Registra um evento de auditoria.

        Args:
            event_type: Tipo do evento (ex: 'workspace_access', 'secret_detected').
            action: Ação tomada (ex: 'blocked', 'allowed', 'masked').
            result: Resultado da ação (ex: 'success', 'denied').
            details: Detalhes adicionais.
        """
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event_type": event_type,
            "action": action,
            "result": result,
            "details": details,
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def get_events(self, event_type: str | None = None) -> list[dict[str, str]]:
        """Recupera eventos da trilha de auditoria.

        Args:
            event_type: Filtro opcional por tipo de evento.

        Returns:
            Lista de eventos.
        """
        if not self.log_file.exists():
            return []

        events: list[dict[str, str]] = []
        with open(self.log_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                if event_type is None or record.get("event_type") == event_type:
                    events.append(record)

        return events
