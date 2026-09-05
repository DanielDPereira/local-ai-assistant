"""Testes para o sistema de Skills."""

import json
from pathlib import Path

import pytest

from assistant.skills.manager import SkillManager
from assistant.skills.models import Skill
from assistant.skills.validator import SkillValidationError, SkillValidator


def test_skill_validation_success() -> None:
    data = {
        "name": "python_expert",
        "description": "Ajuda com python",
        "instructions": "Escreva python idiomatico."
    }
    # Nao deve levantar excecao
    SkillValidator.validate_dict(data)


def test_skill_validation_missing_field() -> None:
    data = {
        "name": "python_expert",
        "description": "Ajuda com python"
    }
    with pytest.raises(SkillValidationError, match="Campo obrigatório ausente: 'instructions'"):
        SkillValidator.validate_dict(data)


def test_skill_validation_invalid_type() -> None:
    data = {
        "name": "python",
        "description": "desc",
        "instructions": ["lista", "invalida"]
    }
    with pytest.raises(SkillValidationError, match="Campo 'instructions' deve ser uma string"):
        SkillValidator.validate_dict(data)


def test_skill_manager_integration(tmp_path: Path) -> None:
    # Setup test env
    skills_dir = tmp_path / "skills"
    telemetry_file = tmp_path / "telemetry.jsonl"

    skills_dir.mkdir()

    # Cria uma skill mock
    skill_data = {
        "name": "test_skill",
        "description": "Teste",
        "instructions": "Seja um teste.",
        "version": "1.0",
        "metadata": {"author": "Daniel"}
    }

    with open(skills_dir / "test_skill.json", "w", encoding="utf-8") as f:
        json.dump(skill_data, f)

    # Inicializa manager
    manager = SkillManager(skills_dir=skills_dir, telemetry_file=telemetry_file)

    # 1. Discover
    available = manager.discover_skills()
    assert "test_skill" in available

    # 2. Apply (carrega, valida e telemetria)
    skill = manager.apply_skill("test_skill", context="Testing")
    assert isinstance(skill, Skill)
    assert skill.name == "test_skill"
    assert skill.metadata["author"] == "Daniel"

    # 3. Telemetry log verification
    assert telemetry_file.exists()
    with open(telemetry_file, encoding="utf-8") as f:
        log_line = f.readline()
        log_data = json.loads(log_line)

        assert log_data["event"] == "skill_usage"
        assert log_data["skill"] == "test_skill"
        assert log_data["context"] == "Testing"


def test_skill_manager_not_found(tmp_path: Path) -> None:
    manager = SkillManager(skills_dir=tmp_path / "skills", telemetry_file=tmp_path / "telemetry.jsonl")
    with pytest.raises(FileNotFoundError):
        manager.apply_skill("inexistente")
