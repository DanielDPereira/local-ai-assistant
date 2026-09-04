"""Agregação de custos computacionais usando SQLite."""

from __future__ import annotations

from typing import Any

from assistant.db.connection import DatabaseConnection


class CostAggregator:
    """Calcula métricas agregadas de custo usando o banco de dados."""

    def __init__(self, db: DatabaseConnection) -> None:
        """Inicializa o agregador."""
        self._db = db

    def aggregate_by_model(self) -> list[dict[str, Any]]:
        """Agrega custos e energia por modelo.

        Returns:
            Lista de dicionários contendo modelo, total de energia e custo.
        """
        query = """
        SELECT
            model,
            SUM(estimated_energy_kwh) as total_energy_kwh,
            SUM(estimated_cost) as total_cost,
            COUNT(*) as executions_count
        FROM executions
        GROUP BY model
        ORDER BY total_cost DESC
        """
        return self._fetch_all(query)

    def aggregate_by_task_type(self) -> list[dict[str, Any]]:
        """Agrega custos e energia por tipo de tarefa."""
        query = """
        SELECT
            task_type,
            SUM(estimated_energy_kwh) as total_energy_kwh,
            SUM(estimated_cost) as total_cost,
            COUNT(*) as executions_count
        FROM executions
        GROUP BY task_type
        ORDER BY total_cost DESC
        """
        return self._fetch_all(query)

    def get_total_cost(self) -> dict[str, float]:
        """Retorna o custo e energia totais registrados."""
        query = """
        SELECT
            SUM(estimated_energy_kwh) as total_energy_kwh,
            SUM(estimated_cost) as total_cost
        FROM executions
        """
        result = self._fetch_one(query)
        return {
            "total_energy_kwh": result["total_energy_kwh"] or 0.0,
            "total_cost": result["total_cost"] or 0.0,
        }

    def _fetch_all(self, query: str) -> list[dict[str, Any]]:
        """Auxiliar para buscar múltiplos registros."""
        with self._db.get_connection() as conn:
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def _fetch_one(self, query: str) -> dict[str, Any]:
        """Auxiliar para buscar um único registro."""
        with self._db.get_connection() as conn:
            cursor = conn.execute(query)
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {}
