"""Ponto de entrada da API HTTP do assistente."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

app = FastAPI(
    title="Local AI Assistant",
    description="Assistente pessoal de IA executado localmente",
    version="0.1.0",
)


@app.get("/api/health")
async def health_check() -> dict[str, Any]:
    """Retorna o status da aplicação."""
    return {"status": "ok"}
