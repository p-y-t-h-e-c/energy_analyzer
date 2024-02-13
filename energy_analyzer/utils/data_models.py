"""Data models module."""
from enum import Enum
from typing import Any, List

from pydantic import BaseModel


class RatesData(BaseModel):
    """Energy Rates dataclass."""

    date: str
    unit_rate_exc_vat: float
    unit_rate_inc_vat: float


class ElectricityRates(RatesData):
    """Electricity Rates dataclass."""


class GasRates(RatesData):
    """Gas Rates dataclass."""


class ConsumptionData(BaseModel):
    """Energy Consumption dataclass."""

    consumption: float


class DailyConsumption(ConsumptionData):
    """Daily Consumption dataclass."""

    date: str


class DailyElectricityConsumption(DailyConsumption):
    """Daily Electricity Consumption dataclass."""


class DailyGasConsumption(DailyConsumption):
    """Daily Gas Consumption dataclass."""


class WeeklyConsumption(ConsumptionData):
    """Weekly Consumption dataclass."""

    week: str


class WeeklyElectricityConsumption(DailyConsumption):
    """Weekly Electricity Consumption dataclass."""


class WeeklyGasConsumption(DailyConsumption):
    """Weekly Gas Consumption dataclass."""


class EnergyData(BaseModel):
    """Energy Data dataclass."""

    unit_rate: List[dict[str, Any]] = []
    consumption: List[dict[str, Any]] = []


class ElectricityData(EnergyData):
    """Electric data dataclass."""


class GasData(EnergyData):
    """Gas data dataclass."""
