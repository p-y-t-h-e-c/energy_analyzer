"""Config module."""
from datetime import date, timedelta
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.exc import NoResultFound

from data_models import EnergyType
from database.db_connector import DbConnector
from database.db_models import (
    ElectricityConsumptionTable,
    ElectricityRatesTable,
    GasConsumptionTable,
    GasRatesTable,
)
from utils import assert_never


class ProjectConfig(BaseSettings):
    """Project config class."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="", case_sensitive=False
    )

    # Solis Info
    solis_api_url: str = "https://www.soliscloud.com:13333/"
    solis_key_id: SecretStr = Field(default=None, alias="SOLIS_KEY_ID")
    solis_key_secret: SecretStr = Field(default=None, alias="SOLIS_KEY_SECRET")

    # Octopus Info
    octopus_api_url: str = "https://api.octopus.energy/v1"
    product_code: str = "SILVER-FLEX-22-11-25"
    account: SecretStr = Field(default=None, alias="OCTOPUS_ACCOUNT_NO")
    octopus_api_key: SecretStr = Field(default=None, alias="OCTOPUS_API_KEY")

    # Electricity Info
    e_tariff_code: str = "E-1R-SILVER-FLEX-22-11-25-B"
    e_MPAN: SecretStr = Field(default=None, alias="electricity_MPAN")
    e_serial_no: SecretStr = Field(default=None, alias="electricity_serial_no")

    # Gas Info
    g_tariff_code: str = "G-1R-SILVER-FLEX-22-11-25-B"
    g_MPRN: SecretStr = Field(default=None, alias="gas_MPRN")
    g_serial_no: SecretStr = Field(default=None, alias="gas_serial_no")
    gas_m3_to_kwh_conversion: float = 1.02264 * 39.5 / 3.6

    # Database
    db_url: SecretStr = Field(default=None, alias="DATABASE_URL")

    # PushStaq
    pushstaq_api_url: str = "https://www.pushstaq.com/api/push/"
    pushstaq_api_key: SecretStr = Field(default=None, alias="PUSHSTAQ_API_KEY")


# {'tariff_code': 'E-1R-VAR-22-04-02-B', 'valid_from': '2022-08-01T00:00:00+01:00', 'valid_to': '2023-02-13T00:00:00Z'}
# {'tariff_code': 'E-1R-SILVER-FLEX-22-11-25-B', 'valid_from': '2023-02-13T00:00:00Z', 'valid_to': None}
# {'tariff_code': 'G-1R-VAR-22-04-02-B', 'valid_from': '2022-08-01T00:00:00+01:00', 'valid_to': '2023-02-13T00:00:00Z'}
# {'tariff_code': 'G-1R-SILVER-FLEX-22-11-25-B', 'valid_from': '2023-02-13T00:00:00Z', 'valid_to': None}


CONFIG = ProjectConfig()


def period_from(table) -> str:
    """Generate period_from date.

    :param from_date: implicitly specified from date in the format 2023-01-01

    :return: period_from attribute
    """
    db_url = CONFIG.db_url
    db_connector = DbConnector(db_url.get_secret_value())
    try:
        date = db_connector.get_latest_date(table) - timedelta(days=20)
        return f"period_from={date}"
    except NoResultFound:
        # db_url = CONFIG.db_url
        # db_connector = DbConnector(db_url.get_secret_value())
        # date = db_connector.get_latest_date(ElectricityRatesTable) - timedelta(days=20)
        return "period_from=2022-07-01"


def period_to(to_date: Optional[str] = None) -> str:
    """Generate period_to date.

    :param to_date: implicitly specified to date in the format 2023-12-31

    :return: period_to attribute
    """
    if to_date:
        return f"&period_to={to_date}"
    else:
        period_to = date.today() + timedelta(days=1)
        return f"period_to={period_to}"


def get_rates_url(energy_type: EnergyType) -> str:
    """Create either electricity or gas rates url.

    :param energy_type: either electricity or gas energy type

    :return: rates url link
    """
    # page_size - default is 100, maximum is 1,500 for rates
    match energy_type:
        case EnergyType.ELECTRICITY:
            url = (
                f"{CONFIG.octopus_api_url}/products/"
                + f"{CONFIG.product_code}/electricity-tariffs/"
                + f"{CONFIG.e_tariff_code}/standard-unit-rates/"
                + f"?{period_from(ElectricityRatesTable)}&{period_to()}&page_size=1500"
            )
            return url
        case EnergyType.GAS:
            url = (
                f"{CONFIG.octopus_api_url}/products/"
                + f"{CONFIG.product_code}/gas-tariffs/"
                + f"{CONFIG.g_tariff_code}/standard-unit-rates/"
                + f"?{period_from(GasRatesTable)}&{period_to()}&page_size=1500"
            )
            return url
        case _:
            assert_never(energy_type)


# TODO: need a weekly tables for which group_by=week, period_from=01-01-2022/23
# also period_to=31-12-2022/2023
def get_consumption_url(
    energy_type: EnergyType,
    group_by: Optional[str] = "day",
) -> str:
    """Create either electricity or gas consumption url.

    :param energy_type: either electricity or gas energy type

    :return: consumption url link
    """
    # page_size - default is 100, maximum is 25,000 for consumption
    match energy_type:
        case EnergyType.ELECTRICITY:
            url = (
                f"{CONFIG.octopus_api_url}/electricity-meter-points/"
                + f"{CONFIG.e_MPAN.get_secret_value()}/meters/"
                + f"{CONFIG.e_serial_no.get_secret_value()}/consumption/"
                + f"?group_by={group_by}&{period_from(ElectricityConsumptionTable)}&page_size=25000"
            )
            return url
        case EnergyType.GAS:
            url = (
                f"{CONFIG.octopus_api_url}/gas-meter-points/"
                + f"{CONFIG.g_MPRN.get_secret_value()}/meters/"
                + f"{CONFIG.g_serial_no.get_secret_value()}/consumption/"
                + f"?group_by={group_by}&{period_from(GasConsumptionTable)}&page_size=25000"
            )
            return url
        case _:
            assert_never(energy_type)


if __name__ == "__main__":
    print(ProjectConfig().model_dump())
    # print(period_to())
    # print(period_from(ElectricityRatesTable))
    # print(get_rates_url(EnergyType.ELECTRICITY))
