"""Testes para o módulo de segurança."""

from __future__ import annotations

from pathlib import Path

import pytest

from assistant.security.audit import AuditTrail
from assistant.security.destructive import DestructiveOperationPolicy
from assistant.security.secrets import SecretProtection
from assistant.security.workspace import WorkspaceBoundary, WorkspaceBoundaryError

# === Workspace Boundary ===


def test_workspace_allows_internal_path(tmp_path: Path) -> None:
    internal = tmp_path / "src" / "main.py"
    internal.parent.mkdir(parents=True, exist_ok=True)
    internal.touch()

    boundary = WorkspaceBoundary(tmp_path)
    result = boundary.validate(internal)
    assert result == internal.resolve()


def test_workspace_blocks_external_path(tmp_path: Path) -> None:
    boundary = WorkspaceBoundary(tmp_path)
    with pytest.raises(WorkspaceBoundaryError, match="fora do workspace"):
        boundary.validate("/etc/passwd")


def test_workspace_is_within(tmp_path: Path) -> None:
    boundary = WorkspaceBoundary(tmp_path)
    assert boundary.is_within(tmp_path / "file.txt") is True
    assert boundary.is_within("/etc/passwd") is False


# === Secret Protection ===


def test_secret_detects_api_key() -> None:
    text = "api_key=sk_live_abc123def456"
    found = SecretProtection.contains_secrets(text)
    assert len(found) > 0


def test_secret_detects_github_pat() -> None:
    text = "token: ghp_abcdefghijklmnopqrstuvwxyz1234567890"
    found = SecretProtection.contains_secrets(text)
    assert "GitHub PAT" in found


def test_secret_masks_content() -> None:
    text = "api_key=my_super_secret_key_123"
    masked = SecretProtection.mask(text)
    assert "my_super_secret" not in masked
    assert "[REDACTED]" in masked


def test_secret_clean_text() -> None:
    text = "This is normal text without secrets"
    found = SecretProtection.contains_secrets(text)
    assert found == []


# === Destructive Operation Policy ===


def test_destructive_blocks_rm_rf_root() -> None:
    policy = DestructiveOperationPolicy()
    action, _ = policy.evaluate("rm -rf /")
    assert action == "block"


def test_destructive_blocks_drop_database() -> None:
    policy = DestructiveOperationPolicy()
    action, _ = policy.evaluate("DROP DATABASE production")
    assert action == "block"


def test_destructive_requires_confirmation_rm() -> None:
    policy = DestructiveOperationPolicy()
    action, _ = policy.evaluate("rm -rf ./build")
    assert action == "confirm"


def test_destructive_allows_safe_commands() -> None:
    policy = DestructiveOperationPolicy()
    action, _ = policy.evaluate("ls -la")
    assert action == "allow"


def test_destructive_custom_blocked() -> None:
    policy = DestructiveOperationPolicy(blocked_commands=["deploy prod"])
    action, _ = policy.evaluate("deploy prod --force")
    assert action == "block"


# === Audit Trail ===


def test_audit_trail_log_and_read(tmp_path: Path) -> None:
    log_file = tmp_path / "audit.jsonl"
    audit = AuditTrail(log_file)

    audit.log("workspace_access", "blocked", "denied", "Tentou acessar /etc/passwd")
    audit.log("secret_detected", "masked", "success", "API key mascarada")

    all_events = audit.get_events()
    assert len(all_events) == 2
    assert all_events[0]["event_type"] == "workspace_access"

    filtered = audit.get_events(event_type="secret_detected")
    assert len(filtered) == 1
    assert filtered[0]["action"] == "masked"


def test_audit_trail_empty(tmp_path: Path) -> None:
    audit = AuditTrail(tmp_path / "audit.jsonl")
    assert audit.get_events() == []
