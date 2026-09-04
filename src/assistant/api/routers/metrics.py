"""Rotas de métricas da API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from assistant.api.dependencies import get_db
from assistant.db.connection import DatabaseConnection

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/overview")
async def get_overview(db: DatabaseConnection = Depends(get_db)) -> dict[str, Any]:  # noqa: B008
    """Retorna métricas gerais do sistema."""
    query = """
    SELECT
        COUNT(*) as total_executions,
        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_executions,
        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_executions,
        AVG(duration_ms) as avg_duration_ms,
        SUM(total_tokens) as total_tokens,
        SUM(tool_calls) as total_tool_calls,
        SUM(error_count) as total_errors,
        SUM(estimated_cost) as total_cost,
        SUM(estimated_energy_kwh) as total_energy_kwh
    FROM executions
    """
    with db.get_connection() as conn:
        cursor = conn.execute(query)
        row = cursor.fetchone()

    if not row or row["total_executions"] == 0:
        return {
            "total_executions": 0,
            "success_rate": 0.0,
            "successful_executions": 0,
            "failed_executions": 0,
            "avg_duration_ms": 0.0,
            "total_tokens": 0,
            "total_tool_calls": 0,
            "total_errors": 0,
            "total_cost": 0.0,
            "total_energy_kwh": 0.0,
        }

    total = row["total_executions"]
    success = row["successful_executions"] or 0

    return {
        "total_executions": total,
        "success_rate": (success / total) * 100.0 if total > 0 else 0.0,
        "successful_executions": success,
        "failed_executions": row["failed_executions"] or 0,
        "avg_duration_ms": row["avg_duration_ms"] or 0.0,
        "total_tokens": row["total_tokens"] or 0,
        "total_tool_calls": row["total_tool_calls"] or 0,
        "total_errors": row["total_errors"] or 0,
        "total_cost": row["total_cost"] or 0.0,
        "total_energy_kwh": row["total_energy_kwh"] or 0.0,
    }
