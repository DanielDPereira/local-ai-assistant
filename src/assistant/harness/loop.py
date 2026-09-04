"""Harness — controla o ciclo de vida e execução do agente."""

from __future__ import annotations

import logging
from collections.abc import Callable
from enum import Enum, auto
from typing import Any

from assistant.config.settings import HarnessSettings

logger = logging.getLogger(__name__)


class HarnessState(Enum):
    """Estados do ciclo de vida da execução."""
    PLAN = auto()
    ACT = auto()
    OBSERVE = auto()
    VERIFY = auto()
    COMPLETE = auto()
    FIX = auto()
    ERROR = auto()


class Harness:
    """Controla o loop de execução garantindo que as regras sejam seguidas."""

    def __init__(self, settings: HarnessSettings | None = None) -> None:
        """Inicializa o Harness.

        Args:
            settings: Configurações do Harness. Se omitido, usa padrões.
        """
        self._settings = settings or HarnessSettings()
        self._state = HarnessState.PLAN
        self._iterations = 0
        self._max_iterations = self._settings.max_iterations
        # Handlers mockáveis temporariamente
        self._handlers: dict[HarnessState, Callable[[], HarnessState]] = {
            HarnessState.PLAN: lambda: HarnessState.ACT,
            HarnessState.ACT: lambda: HarnessState.OBSERVE,
            HarnessState.OBSERVE: lambda: HarnessState.VERIFY,
            HarnessState.VERIFY: lambda: HarnessState.COMPLETE,
            HarnessState.FIX: lambda: HarnessState.ACT,
        }

    @property
    def state(self) -> HarnessState:
        """Estado atual."""
        return self._state

    def set_handler(self, state: HarnessState, handler: Callable[[], HarnessState]) -> None:
        """Define o tratador para um estado específico."""
        self._handlers[state] = handler

    def run(self) -> dict[str, Any]:
        """Executa o loop até atingir COMPLETE, ERROR ou o limite de iterações.

        Returns:
            Dicionário com o resultado da execução.
        """
        self._state = HarnessState.PLAN
        self._iterations = 0

        while self._state not in (HarnessState.COMPLETE, HarnessState.ERROR):
            if self._iterations >= self._max_iterations:
                logger.warning("Limite de iterações atingido (%d).", self._max_iterations)
                self._state = HarnessState.ERROR
                break

            self._iterations += 1
            handler = self._handlers.get(self._state)

            if not handler:
                logger.error("Nenhum handler para o estado %s", self._state)
                self._state = HarnessState.ERROR
                break

            try:
                # Executa a ação do estado atual e obtém o próximo estado
                next_state = handler()
                self._state = next_state
            except Exception as e:
                logger.exception("Erro durante o estado %s: %s", self._state, e)
                self._state = HarnessState.ERROR

        return {
            "final_state": self._state.name,
            "iterations": self._iterations,
            "success": self._state == HarnessState.COMPLETE,
        }
