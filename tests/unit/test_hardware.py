"""Testes para o coletor de hardware."""

from __future__ import annotations

from assistant.telemetry.hardware import HardwareSampler


class TestHardwareSampler:
    """Testes para a classe HardwareSampler."""

    def test_sample(self) -> None:
        """Verifica a coleta de hardware basica."""
        sampler = HardwareSampler()

        sample = sampler.sample()

        assert sample.timestamp > 0
        assert 0.0 <= sample.cpu_percent <= 100.0
        assert 0.0 <= sample.ram_percent <= 100.0
        assert sample.ram_used_mb >= 0.0
        assert sample.gpu_percent is None
