"""Memória persistente do agente."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class PersistentMemory:
    """Armazena memórias explicitamente aprovadas para persistência.

    Cada memória contém origem, timestamp, escopo e conteúdo.
    Os dados são armazenados em um arquivo JSONL para durabilidade.
    """

    def __init__(self, storage_file: str | Path) -> None:
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)

    def save(self, content: str, scope: str = "global", origin: str = "user") -> dict[str, Any]:
        """Salva uma nova memória.

        Args:
            content: Conteúdo da memória.
            scope: Escopo da memória (ex: 'global', 'project', 'session').
            origin: Origem da memória (ex: 'user', 'agent').

        Returns:
            Dicionário com a memória salva (incluindo timestamp).
        """
        record: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "origin": origin,
            "scope": scope,
            "content": content,
        }

        with open(self.storage_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        return record

    def load_all(self, scope: str | None = None) -> list[dict[str, Any]]:
        """Carrega todas as memórias, opcionalmente filtradas por escopo.

        Args:
            scope: Se fornecido, filtra apenas memórias deste escopo.

        Returns:
            Lista de memórias ordenadas por timestamp.
        """
        if not self.storage_file.exists():
            return []

        memories: list[dict[str, Any]] = []
        with open(self.storage_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                if scope is None or record.get("scope") == scope:
                    memories.append(record)

        return memories

    def remove(self, content: str) -> bool:
        """Remove uma memória pelo conteúdo exato.

        Reescreve o arquivo sem a memória removida.

        Returns:
            True se alguma memória foi removida.
        """
        if not self.storage_file.exists():
            return False

        memories = self.load_all()
        filtered = [m for m in memories if m.get("content") != content]

        if len(filtered) == len(memories):
            return False

        with open(self.storage_file, "w", encoding="utf-8") as f:
            for record in filtered:
                f.write(json.dumps(record) + "\n")

        return True
