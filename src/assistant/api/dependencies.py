"""Injeção de dependências para a API FastAPI."""

from __future__ import annotations

from collections.abc import Generator

from assistant.config import get_settings
from assistant.db.connection import DatabaseConnection

_db_instance: DatabaseConnection | None = None


def get_db() -> Generator[DatabaseConnection, None, None]:
    """Fornece uma instância do DatabaseConnection."""
    global _db_instance
    if _db_instance is None:
        settings = get_settings()
        _db_instance = DatabaseConnection(db_path=settings.database.path)

    yield _db_instance
