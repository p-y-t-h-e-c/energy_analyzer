from enum import Enum
from typing import Any, List

from pydantic import BaseModel


class ElectricityRates(BaseModel):
    date: str
    unit_rate_exc_vat: str
    unit_rate_inc_vat: str


class ElectricityData(BaseException):
    unit_rate: List[dict[str, Any]]
    consumption: List[dict[str, Any]]


class EnergyType(str, Enum):
    ELECTRICITY = "ELECTRICITY"
    GAS = "GAS"


class EnergyFactor(str, Enum):
    RATE = "RATE"
    CONSUMPTION = "CONSUMPTION"
