"""Telemetria para operações MCP."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path


class McpTelemetry:
    """Registra operações MCP para auditoria e monitoramento."""

    def __init__(self, log_file: str | Path) -> None:
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        server_name: str,
        method: str,
        tool_name: str = "",
        success: bool = True,
        duration_ms: float = 0.0,
        error: str = "",
    ) -> None:
        """Registra uma operação MCP.

        Args:
            server_name: Nome do servidor MCP.
            method: Método JSON-RPC chamado.
            tool_name: Nome da ferramenta (se aplicável).
            success: Se a operação teve sucesso.
            duration_ms: Duração em milissegundos.
            error: Mensagem de erro (se aplicável).
        """
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "mcp_operation",
            "server": server_name,
            "method": method,
            "tool": tool_name,
            "success": success,
            "duration_ms": duration_ms,
            "error": error,
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
