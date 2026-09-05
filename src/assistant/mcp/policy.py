"""Políticas de segurança para ferramentas MCP."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class McpPolicy:
    """Define as permissões e restrições para chamadas MCP.

    Cada servidor MCP pode ter uma política associada que define
    quais ferramentas são permitidas/bloqueadas e limites de execução.
    """

    server_name: str
    allowed_tools: list[str] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)
    max_calls_per_session: int = 100
    timeout_seconds: int = 30
    require_confirmation: bool = False

    # Lista global de operações sempre bloqueadas
    GLOBAL_BLOCKED_PATTERNS: ClassVar[list[str]] = [
        "delete_all",
        "drop_database",
        "rm_rf",
        "format_disk",
    ]

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Verifica se uma ferramenta é permitida pela política.

        Args:
            tool_name: Nome da ferramenta MCP.

        Returns:
            True se a ferramenta for permitida.
        """
        # Verifica lista global de bloqueio
        for pattern in self.GLOBAL_BLOCKED_PATTERNS:
            if pattern in tool_name.lower():
                return False

        # Verifica lista explícita de bloqueio do servidor
        if tool_name in self.blocked_tools:
            return False

        # Se há lista de permitidos, só permite o que está nela
        if self.allowed_tools:
            return tool_name in self.allowed_tools

        return True
