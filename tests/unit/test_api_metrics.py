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
        # Executions
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
        # Model runs
        conn.execute(
            """INSERT INTO model_runs
               (id, execution_id, model, started_at, duration_ms, success, total_tokens, tokens_per_second)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ("mr1", "exec1", "qwen3:4b", "2026-09-04 10:00:01", 500, 1, 50, 100.0)
        )
        conn.execute(
            """INSERT INTO model_runs
               (id, execution_id, model, started_at, duration_ms, success, total_tokens, tokens_per_second)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ("mr2", "exec2", "qwen3:4b", "2026-09-04 11:00:01", 200, 0, 10, 50.0)
        )
        # Hardware samples
        conn.execute(
            """INSERT INTO hardware_samples
               (id, execution_id, timestamp, cpu_percent, ram_percent, ram_used_mb)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("hw1", "exec1", "2026-09-04 10:00:00.500", 10.0, 50.0, 1024.0)
        )
        conn.execute(
            """INSERT INTO hardware_samples
               (id, execution_id, timestamp, cpu_percent, ram_percent, ram_used_mb)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("hw2", "exec1", "2026-09-04 10:00:01.000", 20.0, 51.0, 1050.0)
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


def test_list_executions(client: TestClient) -> None:
    """Verifica listagem de execuções."""
    # List all
    response = client.get("/api/metrics/executions")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

    # Filter by status
    response = client.get("/api/metrics/executions?status=ERROR")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == "exec2"

    # Pagination
    response = client.get("/api/metrics/executions?limit=1&offset=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_execution(client: TestClient) -> None:
    """Verifica busca de execução única."""
    response = client.get("/api/metrics/executions/exec1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "exec1"
    assert data["status"] == "DONE"

    response = client.get("/api/metrics/executions/invalid_id")
    assert response.status_code == 404


def test_get_models_metrics(client: TestClient) -> None:
    """Verifica agregação de métricas por modelo."""
    response = client.get("/api/metrics/models")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    model_data = data["items"][0]

    assert model_data["model"] == "qwen3:4b"
    assert model_data["total_runs"] == 2
    assert model_data["successful_runs"] == 1
    assert model_data["failed_runs"] == 1
    assert model_data["success_rate"] == 50.0
    assert model_data["avg_duration_ms"] == 350.0
    assert model_data["avg_tokens_per_second"] == 75.0
    assert model_data["total_tokens"] == 60


def test_get_hardware_metrics(client: TestClient) -> None:
    """Verifica endpoint de métricas de hardware."""
    response = client.get("/api/metrics/hardware")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

    # Filter by execution
    response = client.get("/api/metrics/hardware?execution_id=exec1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2

    response = client.get("/api/metrics/hardware?execution_id=exec2")
    assert response.status_code == 200
    data2 = response.json()
    assert data2["total"] == 0


def test_get_costs_metrics(client: TestClient) -> None:
    """Verifica endpoint de custos."""
    response = client.get("/api/metrics/costs")
    assert response.status_code == 200
    data = response.json()

    assert "total" in data
    assert "by_model" in data
    assert "by_task_type" in data

    assert data["total"]["total_cost"] == pytest.approx(0.6)
    assert data["total"]["total_energy_kwh"] == pytest.approx(0.12)

    assert len(data["by_model"]) == 1
    assert data["by_model"][0]["model"] == "qwen3:4b"
    assert data["by_model"][0]["total_cost"] == pytest.approx(0.6)

    assert len(data["by_task_type"]) == 1
    assert data["by_task_type"][0]["task_type"] == "coding"
    assert data["by_task_type"][0]["total_cost"] == pytest.approx(0.6)


def test_get_errors_metrics(client: TestClient) -> None:
    """Verifica endpoint de erros."""
    response = client.get("/api/metrics/errors")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == "exec2"
