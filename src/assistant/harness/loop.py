"""Harness — controla o ciclo de vida e execução do agente."""

from __future__ import annotations

import logging
import time
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
        self._timeout_seconds = self._settings.timeout_seconds
        self._action_history: list[str] = []
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

    def record_action(self, action_signature: str) -> None:
        """Registra uma ação executada pelo agente para detecção de loops.

        Args:
            action_signature: Representação em string da ação (ex: 'read_file({"path": "x"})').
        """
        self._action_history.append(action_signature)

    def _detect_loop(self) -> bool:
        """Verifica se há um loop baseado nas últimas ações.

        Retorna True se as últimas 3 ações forem idênticas.
        """
        if len(self._action_history) >= 3:
            last_3 = self._action_history[-3:]
            if last_3[0] == last_3[1] == last_3[2]:
                return True
        return False

    def run(self) -> dict[str, Any]:
        """Executa o loop até atingir COMPLETE, ERROR ou o limite de iterações.

        Returns:
            Dicionário com o resultado da execução.
        """
        self._state = HarnessState.PLAN
        self._iterations = 0
        self._action_history.clear()

        start_time = time.monotonic()
        timeout_reached = False
        loop_detected = False

        while self._state not in (HarnessState.COMPLETE, HarnessState.ERROR):
            elapsed_time = time.monotonic() - start_time
            if elapsed_time > self._timeout_seconds:
                logger.warning("Timeout global atingido (%.2fs > %ds).", elapsed_time, self._timeout_seconds)
                self._state = HarnessState.ERROR
                timeout_reached = True
                break

            if self._iterations >= self._max_iterations:
                logger.warning("Limite de iterações atingido (%d).", self._max_iterations)
                self._state = HarnessState.ERROR
                break

            if self._detect_loop():
                logger.warning("Loop detectado: ações repetidas sem progresso.")
                self._state = HarnessState.ERROR
                loop_detected = True
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
            "timeout": timeout_reached,
            "loop_detected": loop_detected,
            "elapsed_time": time.monotonic() - start_time,
        }
