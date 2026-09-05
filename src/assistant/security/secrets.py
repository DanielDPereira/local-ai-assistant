"""Proteção contra vazamento de secrets em código e logs."""

from __future__ import annotations

import re
from typing import ClassVar


class SecretProtection:
    """Detecta e mascara secrets em textos para prevenir vazamento.

    Usado para sanitizar outputs de ferramentas, logs e conteúdo
    antes de ser exibido ou persistido.
    """

    # Padrões comuns de secrets
    PATTERNS: ClassVar[list[tuple[str, str]]] = [
        (r"(?i)(api[_-]?key|apikey)\s*[:=]\s*\S+", "API Key"),
        (r"(?i)(secret|password|passwd|pwd)\s*[:=]\s*\S+", "Password/Secret"),
        (r"(?i)(token|bearer)\s*[:=]\s*\S+", "Token"),
        (r"(?i)(private[_-]?key)\s*[:=]\s*\S+", "Private Key"),
        (r"ghp_[A-Za-z0-9_]{36,}", "GitHub PAT"),
        (r"sk-[A-Za-z0-9]{20,}", "API Secret Key"),
        (r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----", "Private Key Block"),
    ]

    @classmethod
    def contains_secrets(cls, text: str) -> list[str]:
        """Verifica se o texto contém padrões de secrets.

        Args:
            text: Texto a ser analisado.

        Returns:
            Lista de tipos de secrets encontrados (vazia se nenhum).
        """
        found: list[str] = []
        for pattern, label in cls.PATTERNS:
            if re.search(pattern, text) and label not in found:
                found.append(label)
        return found

    @classmethod
    def mask(cls, text: str) -> str:
        """Mascara todos os secrets encontrados no texto.

        Args:
            text: Texto com possíveis secrets.

        Returns:
            Texto com secrets substituídos por '[REDACTED]'.
        """
        masked = text
        for pattern, _ in cls.PATTERNS:
            masked = re.sub(pattern, "[REDACTED]", masked)
        return masked
