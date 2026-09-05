"""Telemetria para registrar uso das Skills."""

import json
from datetime import UTC, datetime
from pathlib import Path


class SkillTelemetry:
    """Registra estatísticas de uso das Skills."""

    def __init__(self, log_file: str | Path) -> None:
        """Inicializa o sistema de telemetria.

        Args:
            log_file: Caminho para o arquivo JSONL de logs.
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def record_usage(self, skill_name: str, context: str = "") -> None:
        """Registra a utilização de uma skill.

        Args:
            skill_name: Nome da skill utilizada.
            context: Contexto opcional ou motivo do uso.
        """
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "skill_usage",
            "skill": skill_name,
            "context": context
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
