"""Modelos de dados para Skills."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Skill:
    """Representa uma Skill (instrução/capacidade especializada)."""
    name: str
    description: str
    instructions: str
    version: str = "1.0"
    metadata: dict[str, Any] = field(default_factory=dict)
