"""Testes para o Agent mínimo."""

from __future__ import annotations

from unittest import mock

import pytest

from assistant.agent.agent import Agent, AgentModelError
from assistant.config.settings import ModelSettings
from assistant.models.model_selector import ModelSelector, TaskType
from assistant.models.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaResponse,
    OllamaTimeoutError,
)


@pytest.fixture
def model_selector() -> ModelSelector:
    """Fixture para ModelSelector."""
    settings = ModelSettings(general="qwen3:4b", coding="qwen2.5-coder:3b")
    return ModelSelector(settings)


@pytest.fixture
def mock_client() -> mock.MagicMock:
    """Fixture para mock do OllamaClient."""
    return mock.MagicMock(spec=OllamaClient)


class TestAgentProcess:
    """Testes para o método process do Agent."""

    def test_process_success(
        self, mock_client: mock.MagicMock, model_selector: ModelSelector
    ) -> None:
        """Deve processar entrada e retornar resposta do modelo."""
        mock_response = OllamaResponse(content="Olá, mundo!", model="qwen3:4b", done=True)
        mock_client.generate.return_value = mock_response

        agent = Agent(mock_client, model_selector)
        result = agent.process("Diga olá")

        assert result == "Olá, mundo!"
        mock_client.generate.assert_called_once_with(model="qwen3:4b", prompt="Diga olá")

    def test_process_with_custom_task_type(
        self, mock_client: mock.MagicMock, model_selector: ModelSelector
    ) -> None:
        """Deve usar o modelo correto para o tipo de tarefa."""
        mock_response = OllamaResponse(content="def ola(): pass", model="qwen2.5-coder:3b", done=True)
        mock_client.generate.return_value = mock_response

        agent = Agent(mock_client, model_selector)
        result = agent.process("Crie função ola", task_type=TaskType.CODING)

        assert "def ola" in result
        mock_client.generate.assert_called_once_with(
            model="qwen2.5-coder:3b", prompt="Crie função ola"
        )

    def test_process_handles_timeout(
        self, mock_client: mock.MagicMock, model_selector: ModelSelector
    ) -> None:
        """Deve lançar AgentModelError quando ocorre timeout no Ollama."""
        mock_client.generate.side_effect = OllamaTimeoutError("Timeout")

        agent = Agent(mock_client, model_selector)
        with pytest.raises(AgentModelError, match=r"Falha ao consultar modelo.*Timeout"):
            agent.process("Diga olá")

    def test_process_handles_connection_error(
        self, mock_client: mock.MagicMock, model_selector: ModelSelector
    ) -> None:
        """Deve lançar AgentModelError quando ocorre erro de conexão no Ollama."""
        mock_client.generate.side_effect = OllamaConnectionError("Connection refused")

        agent = Agent(mock_client, model_selector)
        with pytest.raises(AgentModelError, match=r"Falha ao consultar modelo.*Connection"):
            agent.process("Diga olá")
