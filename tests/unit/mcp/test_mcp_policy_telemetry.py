"""Testes para MCP policy e telemetry."""

from __future__ import annotations

import json
from pathlib import Path

from assistant.mcp.policy import McpPolicy
from assistant.mcp.telemetry import McpTelemetry

# === Policy Tests ===


def test_policy_allows_by_default() -> None:
    policy = McpPolicy(server_name="test")
    assert policy.is_tool_allowed("read_file") is True


def test_policy_blocks_global_patterns() -> None:
    policy = McpPolicy(server_name="test")
    assert policy.is_tool_allowed("delete_all_users") is False
    assert policy.is_tool_allowed("rm_rf_home") is False


def test_policy_blocks_explicit_tool() -> None:
    policy = McpPolicy(server_name="test", blocked_tools=["dangerous_tool"])
    assert policy.is_tool_allowed("dangerous_tool") is False
    assert policy.is_tool_allowed("safe_tool") is True


def test_policy_allow_list_restricts() -> None:
    policy = McpPolicy(server_name="test", allowed_tools=["read_file", "list_dir"])
    assert policy.is_tool_allowed("read_file") is True
    assert policy.is_tool_allowed("write_file") is False


# === Telemetry Tests ===


def test_telemetry_records(tmp_path: Path) -> None:
    log_file = tmp_path / "mcp_telemetry.jsonl"
    telemetry = McpTelemetry(log_file)

    telemetry.record(
        server_name="test-server",
        method="tools/call",
        tool_name="get_weather",
        success=True,
        duration_ms=150.5,
    )

    assert log_file.exists()
    with open(log_file, encoding="utf-8") as f:
        record = json.loads(f.readline())
        assert record["event"] == "mcp_operation"
        assert record["server"] == "test-server"
        assert record["tool"] == "get_weather"
        assert record["success"] is True
        assert record["duration_ms"] == 150.5


def test_telemetry_records_error(tmp_path: Path) -> None:
    log_file = tmp_path / "mcp_telemetry.jsonl"
    telemetry = McpTelemetry(log_file)

    telemetry.record(
        server_name="test-server",
        method="tools/call",
        tool_name="bad_tool",
        success=False,
        error="Tool not found",
    )

    with open(log_file, encoding="utf-8") as f:
        record = json.loads(f.readline())
        assert record["success"] is False
        assert record["error"] == "Tool not found"
