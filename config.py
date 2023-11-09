"""Config module."""
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from data_models import EnergyType
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


def get_rates_url(energy_type: EnergyType) -> str:
    """Create either electricity or gas rates url.

    :param energy_type: either electricity or gas energy type

    :return: rates url link
    """
    config = ProjectConfig()
    match energy_type:
        case EnergyType.ELECTRICITY:
            url = (
                f"{config.octopus_api_url}/products/"
                + f"{config.product_code}/electricity-tariffs/"
                + f"{config.e_tariff_code}/standard-unit-rates/"
                + "?period_from=2022-07-20&page_size=1000"
            )
            return url
        case EnergyType.GAS:
            url = (
                f"{config.octopus_api_url}/products/"
                + f"{config.product_code}/gas-tariffs/"
                + f"{config.g_tariff_code}/standard-unit-rates/"
                + "?period_from=2022-07-20&page_size=1000"
            )
            return url
        case _:
            assert_never(energy_type)


def get_consumption_url(energy_type: EnergyType) -> str:
    """Create either electricity or gas consumption url.

    :param energy_type: either electricity or gas energy type

    :return: consumption url link
    """
    config = ProjectConfig()
    match energy_type:
        case EnergyType.ELECTRICITY:
            url = (
                f"{config.octopus_api_url}/electricity-meter-points/"
                + f"{config.e_MPAN.get_secret_value()}/meters/"
                + f"{config.e_serial_no.get_secret_value()}/consumption/"
                + "?group_by=day&period_from=2022-07-20&page_size=1000"
            )
            return url
        case EnergyType.GAS:
            url = (
                f"{config.octopus_api_url}/gas-meter-points/"
                + f"{config.g_MPRN.get_secret_value()}/meters/"
                + f"{config.g_serial_no.get_secret_value()}/consumption/"
                + "?group_by=day&period_from=2022-07-20&page_size=1000"
            )
            return url
        case _:
            assert_never(energy_type)


if __name__ == "__main__":
    print(ProjectConfig().model_dump())
