"""Configuração centralizada da aplicação.

Utiliza dataclasses para definir todas as configurações com valores padrão.
Suporta sobrescrita via variáveis de ambiente com prefixo ASSISTANT_.

Uso:
    from assistant.config import get_settings

    settings = get_settings()
    print(settings.ollama.base_url)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class OllamaSettings:
    """Configurações de conexão com Ollama."""

    base_url: str = "http://localhost:11434"
    timeout_seconds: int = 120


@dataclass(frozen=True)
class ModelSettings:
    """Configurações dos modelos de IA.

    Os nomes dos modelos são centralizados aqui.
    Alterar o modelo exige apenas alterar a configuração.
    """

    general: str = "qwen3:4b"
    coding: str = "qwen2.5-coder:3b"
    lightweight: str = "qwen3:1.7b"


@dataclass(frozen=True)
class HarnessSettings:
    """Configurações do Harness (controle de execução)."""

    max_iterations: int = 10
    timeout_seconds: int = 300
    max_retries: int = 3


@dataclass(frozen=True)
class DatabaseSettings:
    """Configurações do banco de dados SQLite."""

    path: str = "data/assistant.db"


@dataclass(frozen=True)
class TelemetrySettings:
    """Configurações de telemetria e observabilidade."""

    enabled: bool = True
    hardware_sampling_interval_seconds: float = 2.0
    retention_days: int = 90


@dataclass(frozen=True)
class CostSettings:
    """Configurações para estimativa de custo computacional."""

    electricity_price_per_kwh: float = 0.80
    system_power_watts: float = 45.0


@dataclass(frozen=True)
class WorkspaceSettings:
    """Configurações de workspace do agente."""

    path: str = "."


@dataclass(frozen=True)
class Settings:
    """Configuração centralizada do assistente de IA local.

    Agrupa todas as configurações do sistema.
    Nenhum componente deve definir valores diretamente no código.
    """

    ollama: OllamaSettings = field(default_factory=OllamaSettings)
    models: ModelSettings = field(default_factory=ModelSettings)
    harness: HarnessSettings = field(default_factory=HarnessSettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    telemetry: TelemetrySettings = field(default_factory=TelemetrySettings)
    cost: CostSettings = field(default_factory=CostSettings)
    workspace: WorkspaceSettings = field(default_factory=WorkspaceSettings)


def _env(key: str, default: str) -> str:
    """Lê variável de ambiente com fallback."""
    return os.environ.get(key, default)


def _env_int(key: str, default: int) -> int:
    """Lê variável de ambiente como inteiro."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Variável de ambiente {key}={value!r} não é um inteiro válido"
        ) from None


def _env_float(key: str, default: float) -> float:
    """Lê variável de ambiente como float."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        raise ValueError(
            f"Variável de ambiente {key}={value!r} não é um número válido"
        ) from None


def _env_bool(key: str, default: bool) -> bool:
    """Lê variável de ambiente como booleano."""
    value = os.environ.get(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


def _resolve_workspace(path_str: str) -> str:
    """Resolve o caminho do workspace para absoluto."""
    return str(Path(path_str).resolve())


def get_settings() -> Settings:
    """Cria instância de Settings a partir de variáveis de ambiente.

    Cada configuração pode ser sobrescrita por variável de ambiente
    com prefixo ASSISTANT_ (exceto Ollama que usa OLLAMA_).

    Returns:
        Settings configurado com valores do ambiente ou padrões.
    """
    ollama = OllamaSettings(
        base_url=_env("OLLAMA_BASE_URL", OllamaSettings.base_url),
        timeout_seconds=_env_int(
            "OLLAMA_TIMEOUT_SECONDS", OllamaSettings.timeout_seconds
        ),
    )

    models = ModelSettings(
        general=_env("ASSISTANT_MODEL_GENERAL", ModelSettings.general),
        coding=_env("ASSISTANT_MODEL_CODING", ModelSettings.coding),
        lightweight=_env("ASSISTANT_MODEL_LIGHTWEIGHT", ModelSettings.lightweight),
    )

    harness = HarnessSettings(
        max_iterations=_env_int(
            "ASSISTANT_HARNESS_MAX_ITERATIONS", HarnessSettings.max_iterations
        ),
        timeout_seconds=_env_int(
            "ASSISTANT_HARNESS_TIMEOUT_SECONDS", HarnessSettings.timeout_seconds
        ),
        max_retries=_env_int(
            "ASSISTANT_HARNESS_MAX_RETRIES", HarnessSettings.max_retries
        ),
    )

    database = DatabaseSettings(
        path=_env("ASSISTANT_DB_PATH", DatabaseSettings.path),
    )

    telemetry = TelemetrySettings(
        enabled=_env_bool("ASSISTANT_TELEMETRY_ENABLED", TelemetrySettings.enabled),
        hardware_sampling_interval_seconds=_env_float(
            "ASSISTANT_HARDWARE_SAMPLING_INTERVAL",
            TelemetrySettings.hardware_sampling_interval_seconds,
        ),
        retention_days=_env_int(
            "ASSISTANT_TELEMETRY_RETENTION_DAYS", TelemetrySettings.retention_days
        ),
    )

    cost = CostSettings(
        electricity_price_per_kwh=_env_float(
            "ASSISTANT_ELECTRICITY_PRICE_KWH", CostSettings.electricity_price_per_kwh
        ),
        system_power_watts=_env_float(
            "ASSISTANT_SYSTEM_POWER_WATTS", CostSettings.system_power_watts
        ),
    )

    workspace = WorkspaceSettings(
        path=_resolve_workspace(
            _env("ASSISTANT_WORKSPACE", WorkspaceSettings.path)
        ),
    )

    return Settings(
        ollama=ollama,
        models=models,
        harness=harness,
        database=database,
        telemetry=telemetry,
        cost=cost,
        workspace=workspace,
    )
