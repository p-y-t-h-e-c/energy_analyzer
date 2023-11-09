"""Data models module."""
from enum import Enum
from typing import Any, List

from pydantic import BaseModel


class ElectricityRates(BaseModel):
    """Electric rates dataclass."""

    date: str
    unit_rate_exc_vat: str
    unit_rate_inc_vat: str


class ElectricityData(BaseException):
    """Electric data dataclass."""

    unit_rate: List[dict[str, Any]]
    consumption: List[dict[str, Any]]


class EnergyType(str, Enum):
    """Energy type dataclass."""

    ELECTRICITY = "ELECTRICITY"
    GAS = "GAS"


class EnergyFactor(str, Enum):
    """Energy factor dataclass."""

    RATE = "RATE"
    CONSUMPTION = "CONSUMPTION"
