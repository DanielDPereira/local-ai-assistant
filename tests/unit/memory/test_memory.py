"""Testes para o sistema de memória."""

from __future__ import annotations

from pathlib import Path

from assistant.memory.persistent import PersistentMemory
from assistant.memory.policies import MemoryPolicy
from assistant.memory.session import SessionState

# === Session State ===


def test_session_state_set_get() -> None:
    state = SessionState()
    state.set("key1", "value1")
    assert state.get("key1") == "value1"
    assert state.get("missing", "default") == "default"


def test_session_state_delete() -> None:
    state = SessionState()
    state.set("key1", "value1")
    assert state.delete("key1") is True
    assert state.delete("key1") is False
    assert state.get("key1") is None


def test_session_state_clear() -> None:
    state = SessionState()
    state.set("k1", "v1")
    state.add_message("user", "hello")
    state.clear()
    assert state.keys == []
    assert state.get_history() == []


def test_session_state_history() -> None:
    state = SessionState()
    state.add_message("user", "hi")
    state.add_message("assistant", "hello")
    history = state.get_history()
    assert len(history) == 2
    assert history[0] == {"role": "user", "content": "hi"}


# === Persistent Memory ===


def test_persistent_memory_save_load(tmp_path: Path) -> None:
    mem = PersistentMemory(tmp_path / "memory.jsonl")
    mem.save("Lembrar: usar Python 3.12+", scope="project", origin="user")
    mem.save("Preferir dark mode", scope="global", origin="user")

    all_memories = mem.load_all()
    assert len(all_memories) == 2

    project_memories = mem.load_all(scope="project")
    assert len(project_memories) == 1
    assert project_memories[0]["content"] == "Lembrar: usar Python 3.12+"


def test_persistent_memory_remove(tmp_path: Path) -> None:
    mem = PersistentMemory(tmp_path / "memory.jsonl")
    mem.save("item1")
    mem.save("item2")

    assert mem.remove("item1") is True
    assert mem.remove("item1") is False

    remaining = mem.load_all()
    assert len(remaining) == 1
    assert remaining[0]["content"] == "item2"


def test_persistent_memory_load_empty(tmp_path: Path) -> None:
    mem = PersistentMemory(tmp_path / "memory.jsonl")
    assert mem.load_all() == []


# === Memory Policies ===


def test_policy_allows_by_default() -> None:
    policy = MemoryPolicy()
    allowed, _ = policy.can_persist("Lembrete normal")
    assert allowed is True


def test_policy_blocks_secrets() -> None:
    policy = MemoryPolicy()
    allowed, reason = policy.can_persist("my password is 123")
    assert allowed is False
    assert "password" in reason


def test_policy_blocks_large_content() -> None:
    policy = MemoryPolicy(max_memory_size=10)
    allowed, reason = policy.can_persist("a" * 100)
    assert allowed is False
    assert "tamanho máximo" in reason


def test_policy_blocks_agent_when_disabled() -> None:
    policy = MemoryPolicy(allow_agent_memories=False)
    allowed, _ = policy.can_persist("note", origin="agent")
    assert allowed is False


def test_policy_restricts_scopes() -> None:
    policy = MemoryPolicy(allowed_scopes=["global"])
    allowed, _ = policy.can_persist("test", scope="project")
    assert allowed is False
    allowed, _ = policy.can_persist("test", scope="global")
    assert allowed is True
