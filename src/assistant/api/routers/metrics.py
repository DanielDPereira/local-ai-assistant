"""Rotas de métricas da API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

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


@router.get("/executions")
async def list_executions(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: DatabaseConnection = Depends(get_db)  # noqa: B008
) -> dict[str, Any]:
    """Lista execuções com paginação e filtros."""
    query = "SELECT * FROM executions"
    params: list[Any] = []

    if status:
        query += " WHERE status = ?"
        params.append(status)

    query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with db.get_connection() as conn:
        cursor = conn.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]

        # Count total
        count_query = "SELECT COUNT(*) as count FROM executions"
        count_params: list[Any] = []
        if status:
            count_query += " WHERE status = ?"
            count_params.append(status)

        count_cursor = conn.execute(count_query, count_params)
        total = count_cursor.fetchone()["count"]

    return {
        "items": rows,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/executions/{execution_id}")
async def get_execution(
    execution_id: str,
    db: DatabaseConnection = Depends(get_db)  # noqa: B008
) -> dict[str, Any]:
    """Retorna detalhes de uma execução."""
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT * FROM executions WHERE id = ?", (execution_id,))
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Execution not found")

    return dict(row)


@router.get("/models")
async def get_models_metrics(
    db: DatabaseConnection = Depends(get_db)  # noqa: B008
) -> dict[str, Any]:
    """Retorna métricas agregadas por modelo."""
    query = """
    SELECT
        model,
        COUNT(*) as total_runs,
        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_runs,
        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_runs,
        AVG(duration_ms) as avg_duration_ms,
        AVG(tokens_per_second) as avg_tokens_per_second,
        SUM(total_tokens) as total_tokens
    FROM model_runs
    GROUP BY model
    ORDER BY total_runs DESC
    """

    with db.get_connection() as conn:
        cursor = conn.execute(query)
        rows = [dict(row) for row in cursor.fetchall()]

    # Process rows
    for row in rows:
        total = row["total_runs"]
        success = row["successful_runs"] or 0
        row["success_rate"] = (success / total) * 100.0 if total > 0 else 0.0
        row["avg_duration_ms"] = row["avg_duration_ms"] or 0.0
        row["avg_tokens_per_second"] = row["avg_tokens_per_second"] or 0.0
        row["total_tokens"] = row["total_tokens"] or 0
        row["successful_runs"] = success
        row["failed_runs"] = row["failed_runs"] or 0

    return {"items": rows}
