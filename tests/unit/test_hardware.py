"""Testes para o coletor de hardware."""

from __future__ import annotations

from assistant.telemetry.hardware import HardwareSample, HardwareSampler, aggregate_samples


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

    def test_aggregate_samples(self) -> None:
        """Verifica a agregação de amostras."""
        samples = [
            HardwareSample(timestamp=1.0, cpu_percent=10.0, ram_percent=40.0, ram_used_mb=100.0, gpu_percent=None),
            HardwareSample(timestamp=2.0, cpu_percent=20.0, ram_percent=50.0, ram_used_mb=120.0, gpu_percent=5.0),
            HardwareSample(timestamp=3.0, cpu_percent=30.0, ram_percent=60.0, ram_used_mb=140.0, gpu_percent=15.0),
        ]

        agg = aggregate_samples(samples)
        assert agg is not None
        assert agg.avg_cpu_percent == 20.0
        assert agg.max_cpu_percent == 30.0
        assert agg.avg_ram_percent == 50.0
        assert agg.max_ram_percent == 60.0
        assert agg.avg_gpu_percent == 10.0
        assert agg.max_gpu_percent == 15.0

        assert aggregate_samples([]) is None
