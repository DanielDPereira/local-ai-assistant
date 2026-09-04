"""Módulo de banco de dados para telemetria e persistência."""

from assistant.db.connection import DatabaseConnection
from assistant.db.migrations_runner import MigrationError, MigrationRunner

__all__ = ["DatabaseConnection", "MigrationError", "MigrationRunner"]
