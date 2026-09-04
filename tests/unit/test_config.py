"""Testes para o sistema de configuração centralizada."""

from __future__ import annotations

import os
from unittest import mock

import pytest

from assistant.config import Settings, get_settings
from assistant.config.settings import (
    CostSettings,
    DatabaseSettings,
    HarnessSettings,
    ModelSettings,
    OllamaSettings,
    TelemetrySettings,
    WorkspaceSettings,
)


class TestDefaultValues:
    """Verificar que todos os valores padrão estão corretos."""

    def test_settings_has_defaults(self) -> None:
        """Settings deve ser instanciável sem argumentos."""
        settings = Settings()
        assert settings.ollama is not None
        assert settings.models is not None
        assert settings.harness is not None
        assert settings.database is not None
        assert settings.telemetry is not None
        assert settings.cost is not None
        assert settings.workspace is not None

    def test_ollama_defaults(self) -> None:
        """Ollama deve ter URL padrão localhost:11434."""
        ollama = OllamaSettings()
        assert ollama.base_url == "http://localhost:11434"
        assert ollama.timeout_seconds == 120

    def test_model_defaults(self) -> None:
        """Modelos devem ter nomes padrão configurados."""
        models = ModelSettings()
        assert models.general == "qwen3:4b"
        assert models.coding == "qwen2.5-coder:3b"
        assert models.lightweight == "qwen3:1.7b"

    def test_harness_defaults(self) -> None:
        """Harness deve ter limites padrão razoáveis."""
        harness = HarnessSettings()
        assert harness.max_iterations == 10
        assert harness.timeout_seconds == 300
        assert harness.max_retries == 3

    def test_database_defaults(self) -> None:
        """Database deve apontar para data/assistant.db."""
        db = DatabaseSettings()
        assert db.path == "data/assistant.db"

    def test_telemetry_defaults(self) -> None:
        """Telemetria deve estar habilitada por padrão."""
        telemetry = TelemetrySettings()
        assert telemetry.enabled is True
        assert telemetry.hardware_sampling_interval_seconds == 2.0
        assert telemetry.retention_days == 90

    def test_cost_defaults(self) -> None:
        """Custo deve ter valores padrão razoáveis."""
        cost = CostSettings()
        assert cost.electricity_price_per_kwh == 0.80
        assert cost.system_power_watts == 45.0

    def test_workspace_defaults(self) -> None:
        """Workspace deve apontar para diretório corrente."""
        ws = WorkspaceSettings()
        assert ws.path == "."


class TestGetSettings:
    """Verificar que get_settings carrega configurações corretamente."""

    def test_get_settings_returns_settings(self) -> None:
        """get_settings deve retornar instância de Settings."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_defaults(self) -> None:
        """get_settings sem variáveis de ambiente deve usar padrões."""
        env_vars = {
            k: v for k, v in os.environ.items()
            if not k.startswith("ASSISTANT_") and not k.startswith("OLLAMA_")
        }
        with mock.patch.dict(os.environ, env_vars, clear=True):
            settings = get_settings()
        assert settings.ollama.base_url == "http://localhost:11434"
        assert settings.models.general == "qwen3:4b"

    def test_workspace_is_absolute(self) -> None:
        """Workspace deve ser resolvido para caminho absoluto."""
        settings = get_settings()
        assert os.path.isabs(settings.workspace.path)


class TestEnvironmentOverrides:
    """Verificar que variáveis de ambiente sobrescrevem configurações."""

    def test_ollama_url_override(self) -> None:
        """OLLAMA_BASE_URL deve sobrescrever URL do Ollama."""
        with mock.patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://custom:1234"}):
            settings = get_settings()
        assert settings.ollama.base_url == "http://custom:1234"

    def test_model_override(self) -> None:
        """Variáveis ASSISTANT_MODEL_* devem sobrescrever modelos."""
        env = {
            "ASSISTANT_MODEL_GENERAL": "llama3:8b",
            "ASSISTANT_MODEL_CODING": "codellama:7b",
            "ASSISTANT_MODEL_LIGHTWEIGHT": "phi3:mini",
        }
        with mock.patch.dict(os.environ, env):
            settings = get_settings()
        assert settings.models.general == "llama3:8b"
        assert settings.models.coding == "codellama:7b"
        assert settings.models.lightweight == "phi3:mini"

    def test_harness_override(self) -> None:
        """Variáveis ASSISTANT_HARNESS_* devem sobrescrever harness."""
        env = {
            "ASSISTANT_HARNESS_MAX_ITERATIONS": "20",
            "ASSISTANT_HARNESS_TIMEOUT_SECONDS": "600",
            "ASSISTANT_HARNESS_MAX_RETRIES": "5",
        }
        with mock.patch.dict(os.environ, env):
            settings = get_settings()
        assert settings.harness.max_iterations == 20
        assert settings.harness.timeout_seconds == 600
        assert settings.harness.max_retries == 5

    def test_database_override(self) -> None:
        """ASSISTANT_DB_PATH deve sobrescrever caminho do banco."""
        with mock.patch.dict(os.environ, {"ASSISTANT_DB_PATH": "/tmp/test.db"}):
            settings = get_settings()
        assert settings.database.path == "/tmp/test.db"

    def test_telemetry_override(self) -> None:
        """Variáveis de telemetria devem ser configuráveis."""
        env = {
            "ASSISTANT_TELEMETRY_ENABLED": "false",
            "ASSISTANT_HARDWARE_SAMPLING_INTERVAL": "5.0",
            "ASSISTANT_TELEMETRY_RETENTION_DAYS": "30",
        }
        with mock.patch.dict(os.environ, env):
            settings = get_settings()
        assert settings.telemetry.enabled is False
        assert settings.telemetry.hardware_sampling_interval_seconds == 5.0
        assert settings.telemetry.retention_days == 30

    def test_cost_override(self) -> None:
        """Variáveis de custo devem ser configuráveis."""
        env = {
            "ASSISTANT_ELECTRICITY_PRICE_KWH": "1.20",
            "ASSISTANT_SYSTEM_POWER_WATTS": "65.0",
        }
        with mock.patch.dict(os.environ, env):
            settings = get_settings()
        assert settings.cost.electricity_price_per_kwh == 1.20
        assert settings.cost.system_power_watts == 65.0

    def test_workspace_override(self) -> None:
        """ASSISTANT_WORKSPACE deve sobrescrever workspace."""
        with mock.patch.dict(os.environ, {"ASSISTANT_WORKSPACE": "/home/user/project"}):
            settings = get_settings()
        # Deve ser resolvido para absoluto
        assert os.path.isabs(settings.workspace.path)

    def test_telemetry_enabled_truthy(self) -> None:
        """Valores truthy devem ativar telemetria."""
        for val in ("true", "1", "yes", "on", "True", "YES"):
            with mock.patch.dict(os.environ, {"ASSISTANT_TELEMETRY_ENABLED": val}):
                settings = get_settings()
            assert settings.telemetry.enabled is True, f"Failed for {val}"

    def test_telemetry_enabled_falsy(self) -> None:
        """Valores falsy devem desativar telemetria."""
        for val in ("false", "0", "no", "off", "anything"):
            with mock.patch.dict(os.environ, {"ASSISTANT_TELEMETRY_ENABLED": val}):
                settings = get_settings()
            assert settings.telemetry.enabled is False, f"Failed for {val}"


class TestInvalidConfiguration:
    """Verificar que configurações inválidas são reportadas."""

    def test_invalid_int_raises(self) -> None:
        """Valor não-inteiro para configuração inteira deve gerar erro."""
        with (
            mock.patch.dict(os.environ, {"ASSISTANT_HARNESS_MAX_ITERATIONS": "abc"}),
            pytest.raises(ValueError, match="não é um inteiro válido"),
        ):
            get_settings()

    def test_invalid_float_raises(self) -> None:
        """Valor não-numérico para configuração float deve gerar erro."""
        with (
            mock.patch.dict(os.environ, {"ASSISTANT_ELECTRICITY_PRICE_KWH": "xyz"}),
            pytest.raises(ValueError, match="não é um número válido"),
        ):
            get_settings()

    def test_invalid_timeout_raises(self) -> None:
        """Timeout não-inteiro deve gerar erro."""
        with (
            mock.patch.dict(os.environ, {"OLLAMA_TIMEOUT_SECONDS": "not_a_number"}),
            pytest.raises(ValueError, match="não é um inteiro válido"),
        ):
            get_settings()


class TestImmutability:
    """Verificar que Settings é imutável (frozen)."""

    def test_settings_frozen(self) -> None:
        """Settings não deve permitir atribuição."""
        settings = Settings()
        with pytest.raises(AttributeError):
            settings.ollama = OllamaSettings()  # type: ignore[misc]

    def test_ollama_frozen(self) -> None:
        """OllamaSettings não deve permitir atribuição."""
        ollama = OllamaSettings()
        with pytest.raises(AttributeError):
            ollama.base_url = "http://other"  # type: ignore[misc]

    def test_model_frozen(self) -> None:
        """ModelSettings não deve permitir atribuição."""
        models = ModelSettings()
        with pytest.raises(AttributeError):
            models.general = "other"  # type: ignore[misc]
