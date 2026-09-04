"""Testes para o agregador de custos."""

from __future__ import annotations

from pathlib import Path

import pytest

from assistant.db.connection import DatabaseConnection
from assistant.db.migrations_runner import MigrationRunner
from assistant.telemetry.cost_aggregator import CostAggregator


@pytest.fixture
def memory_db(tmp_path: Path) -> DatabaseConnection:
    """Cria um banco de dados temporário com o schema completo e alguns dados."""
    db_file = tmp_path / "test_costs.db"
    db = DatabaseConnection(db_path=str(db_file))

    # Aplica o schema
    runner = MigrationRunner(db=db)
    runner.run_migrations()

    # Insere dados dummy
    with db.get_connection() as conn:
        conn.execute(
            """INSERT INTO executions
               (id, started_at, task_type, status, model, estimated_energy_kwh, estimated_cost)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("exec1", "2026-09-04 10:00:00", "coding", "DONE", "qwen3:4b", 0.5, 0.40)
        )
        conn.execute(
            """INSERT INTO executions
               (id, started_at, task_type, status, model, estimated_energy_kwh, estimated_cost)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("exec2", "2026-09-04 11:00:00", "coding", "DONE", "qwen2.5-coder:3b", 0.2, 0.16)
        )
        conn.execute(
            """INSERT INTO executions
               (id, started_at, task_type, status, model, estimated_energy_kwh, estimated_cost)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("exec3", "2026-09-04 12:00:00", "general", "DONE", "qwen3:4b", 0.3, 0.24)
        )

    return db

class TestCostAggregator:
    """Testes para CostAggregator."""

    def test_aggregate_by_model(self, memory_db: DatabaseConnection) -> None:
        """Verifica a agregação de custos por modelo."""
        aggregator = CostAggregator(memory_db)
        results = aggregator.aggregate_by_model()

        assert len(results) == 2
        # qwen3:4b (exec1 + exec3 = 0.8 kWh, 0.64 cost)
        assert results[0]["model"] == "qwen3:4b"
        assert pytest.approx(results[0]["total_energy_kwh"]) == 0.8
        assert pytest.approx(results[0]["total_cost"]) == 0.64
        assert results[0]["executions_count"] == 2

        # qwen2.5-coder:3b (exec2 = 0.2 kWh, 0.16 cost)
        assert results[1]["model"] == "qwen2.5-coder:3b"
        assert pytest.approx(results[1]["total_energy_kwh"]) == 0.2
        assert pytest.approx(results[1]["total_cost"]) == 0.16

    def test_aggregate_by_task_type(self, memory_db: DatabaseConnection) -> None:
        """Verifica a agregação de custos por task_type."""
        aggregator = CostAggregator(memory_db)
        results = aggregator.aggregate_by_task_type()

        assert len(results) == 2
        # coding (exec1 + exec2 = 0.7 kWh, 0.56 cost)
        assert results[0]["task_type"] == "coding"
        assert pytest.approx(results[0]["total_cost"]) == 0.56

    def test_get_total_cost(self, memory_db: DatabaseConnection) -> None:
        """Verifica custo total."""
        aggregator = CostAggregator(memory_db)
        totals = aggregator.get_total_cost()

        assert pytest.approx(totals["total_energy_kwh"]) == 1.0
        assert pytest.approx(totals["total_cost"]) == 0.80
