"""Política de operações destrutivas."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class DestructiveOperationPolicy:
    """Controla e restringe operações que podem causar perda de dados.

    Define quais comandos e padrões são considerados destrutivos
    e devem ser bloqueados ou exigir confirmação antes da execução.
    """

    # Comandos/padrões sempre bloqueados
    ALWAYS_BLOCKED: ClassVar[list[str]] = [
        "rm -rf /",
        "rm -rf ~",
        "del /f /s /q C:\\",
        "format",
        "mkfs",
        "dd if=",
        "DROP DATABASE",
        "DROP TABLE",
        "TRUNCATE",
    ]

    # Padrões que exigem confirmação
    REQUIRE_CONFIRMATION: ClassVar[list[str]] = [
        "rm -rf",
        "rm -r",
        "del /s",
        "git push --force",
        "git reset --hard",
        "DELETE FROM",
    ]

    blocked_commands: list[str] = field(default_factory=list)
    allow_force_push: bool = False

    def evaluate(self, command: str) -> tuple[str, str]:
        """Avalia se um comando é seguro para execução.

        Args:
            command: Comando a ser avaliado.

        Returns:
            Tupla (ação, motivo) onde ação é 'allow', 'confirm' ou 'block'.
        """
        cmd_lower = command.lower().strip()

        # Verifica bloqueios absolutos
        for pattern in self.ALWAYS_BLOCKED:
            if pattern.lower() in cmd_lower:
                return "block", f"Operação destrutiva bloqueada: '{pattern}'."

        # Verifica bloqueios customizados
        for pattern in self.blocked_commands:
            if pattern.lower() in cmd_lower:
                return "block", f"Comando bloqueado pela política: '{pattern}'."

        # Verifica se exige confirmação
        for pattern in self.REQUIRE_CONFIRMATION:
            if pattern.lower() in cmd_lower:
                if pattern.lower() == "git push --force" and self.allow_force_push:
                    continue
                return "confirm", f"Operação requer confirmação: '{pattern}'."

        return "allow", "OK"
