"""Testes de integração end-to-end com o Ollama.

Requer que o Ollama esteja rodando localmente.
Execute com: pytest tests/integration/ -v
"""

from __future__ import annotations

import sys

import pytest

from assistant.config.settings import get_settings
from assistant.harness.loop import Harness, HarnessState
from assistant.memory.session import SessionState
from assistant.models.model_selector import ModelSelector, TaskType
from assistant.models.ollama_client import OllamaClient, OllamaError
from assistant.security.workspace import WorkspaceBoundary
from assistant.telemetry.context import ExecutionContext
from assistant.telemetry.tracker import TelemetryTracker
from assistant.tools.base import ToolResult


# ────────────────────────────────────────────────────────────────────
# Fixtures
# ────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def settings():
    return get_settings()


@pytest.fixture(scope="module")
def ollama(settings):
    client = OllamaClient(settings.ollama.base_url, settings.ollama.timeout_seconds)
    if not client.health_check():
        pytest.skip("Ollama não está rodando — pulando testes de integração.")
    return client


@pytest.fixture(scope="module")
def model_selector(settings):
    return ModelSelector(settings.models)


# ────────────────────────────────────────────────────────────────────
# 1. Ollama Health & Models
# ────────────────────────────────────────────────────────────────────

class TestOllamaConnection:
    """Valida conectividade com o Ollama."""

    def test_health_check(self, ollama: OllamaClient) -> None:
        assert ollama.health_check() is True

    def test_list_models(self, ollama: OllamaClient) -> None:
        models = ollama.list_models()
        assert isinstance(models, list)
        print(f"\n  Modelos disponíveis: {[m.get('name') for m in models]}")


# ────────────────────────────────────────────────────────────────────
# 2. Model Selection + Generate
# ────────────────────────────────────────────────────────────────────

class TestModelGeneration:
    """Valida que o Ollama consegue gerar texto com o modelo selecionado."""

    def test_generate_simple_prompt(self, ollama: OllamaClient, model_selector: ModelSelector) -> None:
        model = model_selector.lightweight
        print(f"\n  Usando modelo: {model}")

        response = ollama.generate(
            model=model,
            prompt="Responda apenas com 'OK'.",
            temperature=0.0,
        )

        assert response.done is True
        assert len(response.content) > 0
        assert response.model != ""
        print(f"  Resposta: {response.content[:100]}")
        print(f"  Tokens gerados: {response.eval_count}")
        if response.tokens_per_second:
            print(f"  Velocidade: {response.tokens_per_second:.1f} tok/s")

    def test_chat_conversation(self, ollama: OllamaClient, model_selector: ModelSelector) -> None:
        model = model_selector.lightweight
        messages = [
            {"role": "system", "content": "Responda de forma curta e direta."},
            {"role": "user", "content": "Quanto é 2 + 2?"},
        ]

        response = ollama.chat(model=model, messages=messages, temperature=0.0)

        assert response.done is True
        assert len(response.content) > 0
        print(f"\n  Chat response: {response.content[:100]}")


# ────────────────────────────────────────────────────────────────────
# 3. Harness Loop
# ────────────────────────────────────────────────────────────────────

class TestHarnessIntegration:
    """Valida o loop do Harness com handlers reais."""

    def test_harness_complete_flow(self, settings) -> None:
        harness = Harness(settings=settings.harness)
        result = harness.run()

        assert result["success"] is True
        assert result["final_state"] == "COMPLETE"
        assert result["iterations"] > 0
        print(f"\n  Harness: {result}")


# ────────────────────────────────────────────────────────────────────
# 4. Session State + Memory
# ────────────────────────────────────────────────────────────────────

class TestMemoryIntegration:
    """Valida estado de sessão em fluxo real."""

    def test_session_workflow(self, model_selector: ModelSelector) -> None:
        state = SessionState()

        # Simula uma sessão: guardar modelo, registrar mensagens
        state.set("active_model", model_selector.general)
        state.add_message("user", "Hello!")
        state.add_message("assistant", "Hi there!")

        assert state.get("active_model") == model_selector.general
        assert len(state.get_history()) == 2
        print(f"\n  Modelo ativo na sessão: {state.get('active_model')}")


# ────────────────────────────────────────────────────────────────────
# 5. Security
# ────────────────────────────────────────────────────────────────────

class TestSecurityIntegration:
    """Valida segurança em contexto real de workspace."""

    def test_workspace_boundary_real(self, settings) -> None:
        boundary = WorkspaceBoundary(settings.workspace.path)

        # O próprio workspace deve ser válido
        assert boundary.is_within(settings.workspace.path) is True

        # Caminhos externos devem ser bloqueados
        if sys.platform == "win32":
            assert boundary.is_within("C:\\Windows\\System32") is False
        else:
            assert boundary.is_within("/etc/passwd") is False

        print(f"\n  Workspace: {settings.workspace.path}")


# ────────────────────────────────────────────────────────────────────
# 6. API Server
# ────────────────────────────────────────────────────────────────────

class TestAPIIntegration:
    """Valida endpoints da API."""

    def test_health_endpoint(self) -> None:
        from fastapi.testclient import TestClient
        from assistant.api.main import app

        client = TestClient(app)
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print(f"\n  API Health: {data}")

    def test_dashboard_serves(self) -> None:
        from fastapi.testclient import TestClient
        from assistant.api.main import app

        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert "html" in response.headers.get("content-type", "").lower()
        print("\n  Dashboard: served OK")


# ────────────────────────────────────────────────────────────────────
# 7. Full E2E: Ollama + Harness + Tools
# ────────────────────────────────────────────────────────────────────

class TestEndToEnd:
    """Teste end-to-end: Ollama gera resposta, harness controla o fluxo."""

    def test_agent_simulation(
        self, ollama: OllamaClient, model_selector: ModelSelector, settings
    ) -> None:
        """Simula um fluxo completo do agente."""
        model = model_selector.lightweight

        # 1. Estado da sessão
        session = SessionState()
        session.set("task", "Resolver 2+2")

        # 2. O harness controla o loop
        harness = Harness(settings=settings.harness)

        # Handler PLAN: gera prompt
        def plan_handler():
            task = session.get("task")
            session.set("prompt", f"Resolva: {task}. Responda apenas o resultado numerico.")
            return HarnessState.ACT

        # Handler ACT: chama o Ollama
        def act_handler():
            prompt = session.get("prompt")
            response = ollama.generate(model=model, prompt=prompt, temperature=0.0)
            session.set("response", response.content)
            session.add_message("user", prompt)
            session.add_message("assistant", response.content)
            return HarnessState.OBSERVE

        # Handler OBSERVE: verifica resposta
        def observe_handler():
            response = session.get("response", "")
            session.set("has_answer", len(response) > 0)
            return HarnessState.VERIFY

        # Handler VERIFY: valida
        def verify_handler():
            if session.get("has_answer"):
                return HarnessState.COMPLETE
            return HarnessState.FIX

        harness.set_handler(HarnessState.PLAN, plan_handler)
        harness.set_handler(HarnessState.ACT, act_handler)
        harness.set_handler(HarnessState.OBSERVE, observe_handler)
        harness.set_handler(HarnessState.VERIFY, verify_handler)

        result = harness.run()

        assert result["success"] is True
        assert result["final_state"] == "COMPLETE"

        response_text = session.get("response", "")
        history = session.get_history()

        print(f"\n  Tarefa: {session.get('task')}")
        print(f"  Resposta do LLM: {response_text[:200]}")
        print(f"  Mensagens na sessão: {len(history)}")
        print(f"  Harness iterations: {result['iterations']}")
        print(f"  Tempo total: {result['elapsed_time']:.2f}s")
