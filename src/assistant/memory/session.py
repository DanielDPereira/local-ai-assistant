"""Estado de sessão (memória temporária) do agente."""

from __future__ import annotations

from typing import Any


class SessionState:
    """Armazena o estado temporário durante uma sessão do agente.

    Todos os dados são mantidos apenas em memória e descartados
    quando a sessão é encerrada. Usado para contexto da conversa
    atual, variáveis intermediárias e preferências de sessão.
    """

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._history: list[dict[str, str]] = []

    def set(self, key: str, value: Any) -> None:
        """Define um valor no estado da sessão."""
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor do estado da sessão."""
        return self._data.get(key, default)

    def delete(self, key: str) -> bool:
        """Remove um valor do estado da sessão.

        Returns:
            True se a chave existia e foi removida.
        """
        if key in self._data:
            del self._data[key]
            return True
        return False

    def clear(self) -> None:
        """Limpa todo o estado da sessão."""
        self._data.clear()
        self._history.clear()

    def add_message(self, role: str, content: str) -> None:
        """Adiciona uma mensagem ao histórico da sessão."""
        self._history.append({"role": role, "content": content})

    def get_history(self) -> list[dict[str, str]]:
        """Retorna o histórico de mensagens da sessão."""
        return list(self._history)

    @property
    def keys(self) -> list[str]:
        """Retorna as chaves armazenadas no estado."""
        return list(self._data.keys())
