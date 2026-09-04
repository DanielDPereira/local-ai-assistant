"""Testes para o router de métricas."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from assistant.api.dependencies import get_db
from assistant.api.main import app
from assistant.db.connection import DatabaseConnection
from assistant.db.migrations_runner import MigrationRunner


@pytest.fixture
def memory_db(tmp_path: Path) -> DatabaseConnection:
    """Cria um banco de dados temporário com dados."""
    db_file = tmp_path / "test_api_metrics.db"
    db = DatabaseConnection(db_path=str(db_file))

    runner = MigrationRunner(db=db)
    runner.run_migrations()

    with db.get_connection() as conn:
        conn.execute(
            """INSERT INTO executions
               (id, started_at, task_type, status, model, success, duration_ms, total_tokens, tool_calls, error_count, estimated_cost, estimated_energy_kwh)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("exec1", "2026-09-04 10:00:00", "coding", "DONE", "qwen3:4b", 1, 1000, 50, 2, 0, 0.5, 0.1)
        )
        conn.execute(
            """INSERT INTO executions
               (id, started_at, task_type, status, model, success, duration_ms, total_tokens, tool_calls, error_count, estimated_cost, estimated_energy_kwh)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("exec2", "2026-09-04 11:00:00", "coding", "ERROR", "qwen3:4b", 0, 500, 10, 0, 1, 0.1, 0.02)
        )

    return db


@pytest.fixture
def client(memory_db: DatabaseConnection) -> Generator[TestClient, None, None]:
    """TestClient configurado com o banco de dados temporário."""
    def override_get_db() -> Generator[DatabaseConnection, None, None]:
        yield memory_db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_overview(client: TestClient) -> None:
    """Verifica o endpoint de overview."""
    response = client.get("/api/metrics/overview")
    assert response.status_code == 200

    data = response.json()
    assert data["total_executions"] == 2
    assert data["success_rate"] == 50.0
    assert data["successful_executions"] == 1
    assert data["failed_executions"] == 1
    assert data["avg_duration_ms"] == 750.0
    assert data["total_tokens"] == 60
    assert data["total_tool_calls"] == 2
    assert data["total_errors"] == 1
    assert data["total_cost"] == pytest.approx(0.6)
    assert data["total_energy_kwh"] == pytest.approx(0.12)
