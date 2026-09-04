"""Cálculo de custos computacionais e de energia."""

from __future__ import annotations


class CostEstimator:
    """Estima uso de energia e custos computacionais."""

    def __init__(self, electricity_price_per_kwh: float, system_power_watts: float) -> None:
        """Inicializa o estimador.

        Args:
            electricity_price_per_kwh: Preço da energia por kWh na moeda local.
            system_power_watts: Consumo de potência médio do sistema em Watts.
        """
        self._price_per_kwh = electricity_price_per_kwh
        self._power_watts = system_power_watts

    def estimate_energy_kwh(self, duration_seconds: float) -> float:
        """Estima a energia consumida em kWh durante o período.

        Args:
            duration_seconds: Duração da execução em segundos.

        Returns:
            Energia consumida em kWh.
        """
        duration_hours = duration_seconds / 3600.0
        # Energia (kWh) = Potência (W) * Tempo (h) / 1000
        return (self._power_watts * duration_hours) / 1000.0

    def estimate_cost(self, duration_seconds: float) -> float:
        """Estima o custo financeiro da execução.

        Args:
            duration_seconds: Duração da execução em segundos.

        Returns:
            Custo estimado na moeda configurada.
        """
        energy_kwh = self.estimate_energy_kwh(duration_seconds)
        return energy_kwh * self._price_per_kwh
