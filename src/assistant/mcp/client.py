"""Cliente MCP (Model Context Protocol) para integração com servidores externos."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from typing import Any


@dataclass
class McpToolSchema:
    """Schema de uma ferramenta descoberta via MCP."""

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class McpServerConfig:
    """Configuração de um servidor MCP."""

    name: str
    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)


class McpClient:
    """Cliente para comunicação com servidores MCP via stdio (JSON-RPC 2.0).

    Cada instância gerencia a conexão com um único servidor MCP,
    seguindo o protocolo JSON-RPC 2.0 sobre stdin/stdout.
    """

    def __init__(self, config: McpServerConfig) -> None:
        self.config = config
        self._process: subprocess.Popen[str] | None = None
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def start(self) -> None:
        """Inicia o processo do servidor MCP."""
        if self._process is not None:
            return

        self._process = subprocess.Popen(
            [self.config.command, *self.config.args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**self.config.env} if self.config.env else None,
        )

    def stop(self) -> None:
        """Encerra o processo do servidor MCP."""
        if self._process is None:
            return
        self._process.terminate()
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._process.kill()
        self._process = None

    def _send_request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Envia uma requisição JSON-RPC 2.0 e aguarda a resposta.

        Args:
            method: Nome do método JSON-RPC.
            params: Parâmetros opcionais.

        Returns:
            Dicionário com o campo 'result' da resposta.

        Raises:
            RuntimeError: Se o servidor não estiver iniciado.
            Exception: Se a resposta contiver um erro JSON-RPC.
        """
        if self._process is None or self._process.stdin is None or self._process.stdout is None:
            raise RuntimeError("Servidor MCP não está iniciado. Chame start() primeiro.")

        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
        }
        if params is not None:
            request["params"] = params

        self._process.stdin.write(json.dumps(request) + "\n")
        self._process.stdin.flush()

        raw_response = self._process.stdout.readline()
        if not raw_response:
            raise RuntimeError("Servidor MCP não retornou resposta.")

        response = json.loads(raw_response)

        if "error" in response:
            error = response["error"]
            raise Exception(f"MCP Error ({error.get('code')}): {error.get('message')}")

        return dict(response.get("result", {}))

    def initialize(self) -> dict[str, Any]:
        """Inicializa a conexão com o servidor MCP (handshake)."""
        return self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "local-ai-assistant", "version": "0.1.0"},
        })

    def list_tools(self) -> list[McpToolSchema]:
        """Descobre as ferramentas disponíveis no servidor MCP.

        Returns:
            Lista de McpToolSchema com as ferramentas descobertas.
        """
        result = self._send_request("tools/list")
        tools: list[McpToolSchema] = []
        for tool_data in result.get("tools", []):
            tools.append(McpToolSchema(
                name=tool_data.get("name", ""),
                description=tool_data.get("description", ""),
                input_schema=tool_data.get("inputSchema", {}),
            ))
        return tools

    def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Executa uma ferramenta no servidor MCP.

        Args:
            tool_name: Nome da ferramenta a executar.
            arguments: Argumentos para a ferramenta.

        Returns:
            Resultado da execução.
        """
        return self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments or {},
        })
