"""Testes para estimativa de custo e energia."""

from __future__ import annotations

from assistant.telemetry.cost import CostEstimator


class TestCostEstimator:
    """Testes para a classe CostEstimator."""

    def test_estimate_energy_kwh(self) -> None:
        """Verifica o cálculo de energia."""
        # 1000 Watts por 3600 segundos (1 hora) = 1 kWh
        estimator = CostEstimator(electricity_price_per_kwh=1.0, system_power_watts=1000.0)
        assert estimator.estimate_energy_kwh(3600.0) == 1.0

        # 45 Watts por 2 horas (7200 s) = 0.09 kWh
        estimator2 = CostEstimator(electricity_price_per_kwh=1.0, system_power_watts=45.0)
        assert estimator2.estimate_energy_kwh(7200.0) == 0.09

    def test_estimate_cost(self) -> None:
        """Verifica o cálculo de custo."""
        # 1000W por 1h = 1 kWh. A 0.80 por kWh = 0.80
        estimator = CostEstimator(electricity_price_per_kwh=0.80, system_power_watts=1000.0)
        assert estimator.estimate_cost(3600.0) == 0.80
