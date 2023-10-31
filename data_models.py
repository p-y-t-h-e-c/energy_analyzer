from enum import Enum

from pydantic import BaseModel


class ElectricityRates(BaseModel):
    date: str
    unit_rate_exc_vat: str
    unit_rate_inc_vat: str


class EnergyType(str, Enum):
    ELECTRICITY = "ELECTRICITY"
    GAS = "GAS"


class EnergyFactor(str, Enum):
    RATE = "RATE"
    CONSUMPTION = "CONSUMPTION"
