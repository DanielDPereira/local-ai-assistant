"""Testes para o cliente MCP."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from assistant.mcp.client import McpClient, McpServerConfig, McpToolSchema


def _make_client() -> McpClient:
    config = McpServerConfig(name="test-server", command="echo")
    return McpClient(config)


def test_mcp_client_init() -> None:
    """Verifica inicialização do cliente."""
    client = _make_client()
    assert client.config.name == "test-server"
    assert client._process is None


def test_mcp_client_send_request_not_started() -> None:
    """Verifica erro quando o servidor não foi iniciado."""
    client = _make_client()
    with pytest.raises(RuntimeError, match="não está iniciado"):
        client._send_request("test")


def test_mcp_client_send_request_success() -> None:
    """Verifica envio e recebimento de JSON-RPC."""
    client = _make_client()

    mock_stdin = MagicMock()
    mock_stdout = MagicMock()
    response = {"jsonrpc": "2.0", "id": 1, "result": {"status": "ok"}}
    mock_stdout.readline.return_value = json.dumps(response)

    mock_proc = MagicMock()
    mock_proc.stdin = mock_stdin
    mock_proc.stdout = mock_stdout
    client._process = mock_proc

    result = client._send_request("test_method", {"key": "value"})

    assert result == {"status": "ok"}
    mock_stdin.write.assert_called_once()
    written = mock_stdin.write.call_args[0][0]
    parsed = json.loads(written.strip())
    assert parsed["method"] == "test_method"
    assert parsed["params"] == {"key": "value"}


def test_mcp_client_send_request_error() -> None:
    """Verifica tratamento de erro JSON-RPC."""
    client = _make_client()

    mock_stdout = MagicMock()
    error_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32600, "message": "Invalid Request"},
    }
    mock_stdout.readline.return_value = json.dumps(error_response)

    mock_proc = MagicMock()
    mock_proc.stdin = MagicMock()
    mock_proc.stdout = mock_stdout
    client._process = mock_proc

    with pytest.raises(Exception, match="MCP Error"):
        client._send_request("bad_method")


def test_mcp_client_list_tools() -> None:
    """Verifica a descoberta de ferramentas."""
    client = _make_client()

    tools_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "tools": [
                {
                    "name": "get_weather",
                    "description": "Get weather for a city",
                    "inputSchema": {"type": "object", "properties": {"city": {"type": "string"}}},
                }
            ]
        },
    }
    mock_stdout = MagicMock()
    mock_stdout.readline.return_value = json.dumps(tools_response)

    mock_proc = MagicMock()
    mock_proc.stdin = MagicMock()
    mock_proc.stdout = mock_stdout
    client._process = mock_proc

    tools = client.list_tools()
    assert len(tools) == 1
    assert isinstance(tools[0], McpToolSchema)
    assert tools[0].name == "get_weather"
    assert tools[0].description == "Get weather for a city"


@patch("subprocess.Popen")
def test_mcp_client_start_stop(mock_popen: MagicMock) -> None:
    """Verifica start e stop do processo."""
    mock_proc = MagicMock()
    mock_popen.return_value = mock_proc

    client = _make_client()
    client.start()

    assert client._process is not None
    mock_popen.assert_called_once()

    client.stop()
    mock_proc.terminate.assert_called_once()
    assert client._process is None
