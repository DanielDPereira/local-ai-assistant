"""Políticas de memória — controla o que pode ser persistido."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass
class MemoryPolicy:
    """Define o que pode ser persistido na memória do agente.

    Attributes:
        allow_agent_memories: Se o agente pode salvar memórias automaticamente.
        max_memory_size: Tamanho máximo em caracteres para uma memória individual.
        allowed_scopes: Escopos permitidos para persistência.
        blocked_patterns: Padrões de conteúdo que não devem ser persistidos.
    """

    allow_agent_memories: bool = True
    max_memory_size: int = 5000
    allowed_scopes: list[str] | None = None
    blocked_patterns: list[str] | None = None

    # Padrões sempre bloqueados por segurança
    ALWAYS_BLOCKED: ClassVar[list[str]] = [
        "password",
        "secret",
        "api_key",
        "token",
        "private_key",
        "credit_card",
    ]

    def can_persist(self, content: str, scope: str = "global", origin: str = "user") -> tuple[bool, str]:
        """Verifica se um conteúdo pode ser persistido.

        Args:
            content: Conteúdo a ser persistido.
            scope: Escopo da memória.
            origin: Origem da memória.

        Returns:
            Tupla (permitido, motivo).
        """
        if origin == "agent" and not self.allow_agent_memories:
            return False, "Memórias automáticas do agente estão desabilitadas."

        if len(content) > self.max_memory_size:
            return False, f"Conteúdo excede o tamanho máximo ({self.max_memory_size} caracteres)."

        if self.allowed_scopes and scope not in self.allowed_scopes:
            return False, f"Escopo '{scope}' não é permitido."

        content_lower = content.lower()

        for pattern in self.ALWAYS_BLOCKED:
            if pattern in content_lower:
                return False, f"Conteúdo contém padrão bloqueado por segurança: '{pattern}'."

        if self.blocked_patterns:
            for pattern in self.blocked_patterns:
                if pattern.lower() in content_lower:
                    return False, f"Conteúdo contém padrão bloqueado: '{pattern}'."

        return True, "OK"
