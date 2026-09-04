"""Testes para o endpoint principal da API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from assistant.api.main import app

client = TestClient(app)


def test_health_check() -> None:
    """Verifica se o endpoint /api/health retorna status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
