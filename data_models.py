"""Data models module."""
from enum import Enum
from typing import Any, List

from pydantic import BaseModel


class EnergyData(BaseModel):
    """Energy Data dataclass."""

    unit_rate: List[dict[str, Any]] = []
    consumption: List[dict[str, Any]] = []


class ElectricityData(EnergyData):
    """Electric data dataclass."""


class GasData(EnergyData):
    """Gas data dataclass."""


class ElectricityRates(BaseModel):
    """Electric rates dataclass."""

    date: str
    unit_rate_exc_vat: str
    unit_rate_inc_vat: str


class EnergyType(str, Enum):
    """Energy type dataclass."""

    ELECTRICITY = "ELECTRICITY"
    GAS = "GAS"


class EnergyFactor(str, Enum):
    """Energy factor dataclass."""

    RATE = "RATE"
    CONSUMPTION = "CONSUMPTION"
