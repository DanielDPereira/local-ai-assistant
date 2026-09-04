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


@dataclass(frozen=True)
class HardwareAggregation:
    """Métricas agregadas de hardware."""

    avg_cpu_percent: float
    max_cpu_percent: float
    avg_ram_percent: float
    max_ram_percent: float
    avg_gpu_percent: float | None = None
    max_gpu_percent: float | None = None


def aggregate_samples(samples: list[HardwareSample]) -> HardwareAggregation | None:
    """Agrega uma lista de amostras e retorna as métricas."""
    if not samples:
        return None

    cpu = [s.cpu_percent for s in samples]
    ram = [s.ram_percent for s in samples]
    gpu = [s.gpu_percent for s in samples if s.gpu_percent is not None]

    avg_gpu = sum(gpu) / len(gpu) if gpu else None
    max_gpu = max(gpu) if gpu else None

    return HardwareAggregation(
        avg_cpu_percent=sum(cpu) / len(cpu),
        max_cpu_percent=max(cpu),
        avg_ram_percent=sum(ram) / len(ram),
        max_ram_percent=max(ram),
        avg_gpu_percent=avg_gpu,
        max_gpu_percent=max_gpu,
    )


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
