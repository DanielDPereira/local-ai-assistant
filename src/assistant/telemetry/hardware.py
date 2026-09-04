"""Coleta de métricas de hardware."""

from __future__ import annotations

import time
from dataclasses import dataclass

import psutil


@dataclass(frozen=True)
class HardwareSample:
    """Amostra de uso de hardware em um determinado instante."""

    timestamp: float
    cpu_percent: float
    ram_percent: float
    ram_used_mb: float

    # GPU (opcional/não suportado nativamente pelo psutil sem extensões)
    gpu_percent: float | None = None
    gpu_memory_used_mb: float | None = None
    gpu_memory_percent: float | None = None
    gpu_temperature: float | None = None
    power_watts: float | None = None


class HardwareSampler:
    """Coletor de métricas de hardware."""

    def __init__(self) -> None:
        """Inicializa o coletor."""
        # Primeira chamada para inicializar o cálculo de CPU do psutil
        psutil.cpu_percent()

    def sample(self) -> HardwareSample:
        """Coleta e retorna uma amostra de hardware atual."""
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()

        return HardwareSample(
            timestamp=time.time(),
            cpu_percent=cpu,
            ram_percent=mem.percent,
            ram_used_mb=mem.used / (1024 * 1024),
            gpu_percent=None,
            gpu_memory_used_mb=None,
            gpu_memory_percent=None,
            gpu_temperature=None,
            power_watts=None,
        )
