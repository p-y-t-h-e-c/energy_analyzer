from pydantic import BaseModel


class ElectricityRates(BaseModel):
    date: str
    unit_rate_exc_vat: str
    unit_rate_inc_vat: str
