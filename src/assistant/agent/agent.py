"""Agent mínimo.

Implementação básica do Agent que recebe uma solicitação e consulta o modelo.
"""

from __future__ import annotations

import logging

from assistant.models.model_selector import ModelSelector, TaskType
from assistant.models.ollama_client import OllamaClient, OllamaError

logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Erro base para operações do Agent."""


class AgentModelError(AgentError):
    """Erro originado da comunicação com o modelo."""


class Agent:
    """Agent mínimo para processamento de entrada."""

    def __init__(self, ollama_client: OllamaClient, model_selector: ModelSelector) -> None:
        """Inicializa o Agent.

        Args:
            ollama_client: Cliente para comunicação com Ollama.
            model_selector: Seletor de modelos.
        """
        self._client = ollama_client
        self._selector = model_selector

    def process(self, input_text: str, task_type: TaskType = TaskType.GENERAL) -> str:
        """Processa a entrada enviando ao modelo e retornando a resposta.

        Args:
            input_text: O texto da solicitação do usuário.
            task_type: Tipo de tarefa para seleção de modelo (padrão: general).

        Returns:
            Resposta gerada pelo modelo.

        Raises:
            AgentModelError: Se ocorrer um erro de comunicação com o modelo.
        """
        model_name = self._selector.select(task_type)
        try:
            logger.debug("Enviando requisição ao modelo %s", model_name)
            response = self._client.generate(model=model_name, prompt=input_text)
            return response.content
        except OllamaError as e:
            logger.error("Erro de comunicação com o modelo: %s", e)
            raise AgentModelError(f"Falha ao consultar modelo {model_name}: {e}") from e
