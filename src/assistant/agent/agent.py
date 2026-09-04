"""Agent mínimo.

Implementação básica do Agent que recebe uma solicitação e consulta o modelo.
"""

from __future__ import annotations

import logging
import time

from assistant.models.model_selector import ModelSelector, TaskType
from assistant.models.ollama_client import OllamaClient, OllamaError
from assistant.telemetry.context import ExecutionContext
from assistant.telemetry.tracker import TelemetryTracker

logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Erro base para operações do Agent."""


class AgentModelError(AgentError):
    """Erro originado da comunicação com o modelo."""


class Agent:
    """Agent mínimo para processamento de entrada."""

    def __init__(
        self,
        ollama_client: OllamaClient,
        model_selector: ModelSelector,
        telemetry_tracker: TelemetryTracker | None = None,
        execution_context: ExecutionContext | None = None,
    ) -> None:
        """Inicializa o Agent.

        Args:
            ollama_client: Cliente para comunicação com Ollama.
            model_selector: Seletor de modelos.
            telemetry_tracker: Rastreador de telemetria opcional.
            execution_context: Contexto de execução opcional.
        """
        self._client = ollama_client
        self._selector = model_selector
        self._tracker = telemetry_tracker
        self._context = execution_context

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
        start_time = time.monotonic()

        if self._tracker and self._context:
            self._tracker.track_model_request(self._context, model_name, start_time)

        try:
            logger.debug("Enviando requisição ao modelo %s", model_name)
            response = self._client.generate(model=model_name, prompt=input_text)

            if self._tracker and self._context:
                self._tracker.track_model_response(self._context, model_name, start_time, response)

            return response.content
        except OllamaError as e:
            if self._tracker and self._context:
                self._tracker.track_model_response(self._context, model_name, start_time, None, error=str(e))

            logger.error("Erro de comunicação com o modelo: %s", e)
            raise AgentModelError(f"Falha ao consultar modelo {model_name}: {e}") from e
