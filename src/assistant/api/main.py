"""Ponto de entrada da API HTTP do assistente."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from assistant.api.routers import metrics

app = FastAPI(
    title="Local AI Assistant",
    description="Assistente pessoal de IA executado localmente",
    version="0.1.0",
)

app.include_router(metrics.router)

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def serve_dashboard() -> FileResponse:
    """Serve o dashboard web."""
    return FileResponse(static_dir / "index.html")

@app.get("/api/health")
async def health_check() -> dict[str, Any]:
    """Retorna o status da aplicação."""
    return {"status": "ok"}
