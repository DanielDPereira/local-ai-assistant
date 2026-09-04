"""Interface base para todas as ferramentas (tools).

Define o contrato que todas as ferramentas devem implementar para
serem utilizadas pelo Agent. Garante que o Agent não dependa de
implementações concretas.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolResult:
    """Resultado da execução de uma ferramenta.

    Attributes:
        success: Indica se a execução foi bem-sucedida.
        output: Saída textual da ferramenta (pode ser o erro em caso de falha).
        data: Dados estruturados adicionais (opcional).
        error_code: Código de erro específico da ferramenta (opcional).
    """

    success: bool
    output: str
    data: dict[str, Any] | None = None
    error_code: str | None = None


class BaseTool(ABC):
    """Classe base abstrata para todas as ferramentas."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome identificador da ferramenta (ex: 'read_file')."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Descrição de uso da ferramenta para o modelo entender o que ela faz."""

    @property
    @abstractmethod
    def schema(self) -> dict[str, Any]:
        """Esquema JSON Schema dos parâmetros aceitos pela ferramenta."""

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """Executa a ferramenta com os parâmetros fornecidos.

        Args:
            **kwargs: Parâmetros fornecidos pelo modelo (validados contra o schema).

        Returns:
            O resultado da execução encapsulado em ToolResult.
        """
