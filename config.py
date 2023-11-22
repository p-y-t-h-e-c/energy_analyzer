"""Config module."""
from datetime import date, timedelta

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from data_models import EnergyType
from database.db_connector import DbConnector
from database.db_models import ElectricityRatesTable
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


CONFIG = ProjectConfig()


def period_from() -> str:
    """Generate period_from date.

    :return: period_from attribute
    """
    db_url = CONFIG.db_url
    db_connector = DbConnector(db_url.get_secret_value())
    date = db_connector.get_latest_date(ElectricityRatesTable) - timedelta(days=7)
    return f"period_from={date}"


def period_to() -> str:
    """Generate period_to date.

    :return: period_to attribute
    """
    period_to = date.today() + timedelta(days=1)
    return f"period_to={period_to}"


def get_rates_url(energy_type: EnergyType) -> str:
    """Create either electricity or gas rates url.

    :param energy_type: either electricity or gas energy type

    :return: rates url link
    """
    match energy_type:
        case EnergyType.ELECTRICITY:
            url = (
                f"{CONFIG.octopus_api_url}/products/"
                + f"{CONFIG.product_code}/electricity-tariffs/"
                + f"{CONFIG.e_tariff_code}/standard-unit-rates/"
                + f"?period_from=2022-07-20&{period_to()}&page_size=1000"
            )
            return url
        case EnergyType.GAS:
            url = (
                f"{CONFIG.octopus_api_url}/products/"
                + f"{CONFIG.product_code}/gas-tariffs/"
                + f"{CONFIG.g_tariff_code}/standard-unit-rates/"
                + f"?period_from=2022-07-20&{period_to()}&page_size=1000"
            )
            return url
        case _:
            assert_never(energy_type)


def get_consumption_url(energy_type: EnergyType) -> str:
    """Create either electricity or gas consumption url.

    :param energy_type: either electricity or gas energy type

    :return: consumption url link
    """
    match energy_type:
        case EnergyType.ELECTRICITY:
            url = (
                f"{CONFIG.octopus_api_url}/electricity-meter-points/"
                + f"{CONFIG.e_MPAN.get_secret_value()}/meters/"
                + f"{CONFIG.e_serial_no.get_secret_value()}/consumption/"
                + "?group_by=day&period_from=2022-07-20&page_size=1000"
            )
            return url
        case EnergyType.GAS:
            url = (
                f"{CONFIG.octopus_api_url}/gas-meter-points/"
                + f"{CONFIG.g_MPRN.get_secret_value()}/meters/"
                + f"{CONFIG.g_serial_no.get_secret_value()}/consumption/"
                + "?group_by=day&period_from=2022-07-20&page_size=1000"
            )
            return url
        case _:
            assert_never(energy_type)


if __name__ == "__main__":
    # print(ProjectConfig().model_dump())
    # print(period_to())
    print(period_from())
