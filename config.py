from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from data_models import EnergyType
from utils import assert_never


class ProjectConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="", case_sensitive=False
    )

    # Octopus Info
    api_url: str = "https://api.octopus.energy/v1"
    product_code: str = "SILVER-FLEX-22-11-25"
    account: SecretStr = Field(default=None, alias="account_no")
    api_key: SecretStr = Field(default=None, alias="API_KEY")

    # Electricity Info
    e_tariff_code: str = "E-1R-SILVER-FLEX-22-11-25-B"
    e_MPAN: SecretStr = Field(default=None, alias="electricity_MPAN")
    e_serial_no: SecretStr = Field(default=None, alias="electricity_serial_no")

    # Gas Info
    g_tariff_code: str = "G-1R-SILVER-FLEX-22-11-25-B"
    g_MPRN: SecretStr = Field(default=None, alias="gas_MPRN")
    g_serial_no: SecretStr = Field(default=None, alias="gas_serial_no")

    # Database
    db_url: SecretStr = Field(default=None, alias="DATABASE_URL")


def get_rates_url(energy_type: EnergyType) -> str:
    config = ProjectConfig()
    match energy_type:
        case EnergyType.ELECTRICITY:
            url = (
                f"{config.api_url}/products/"
                + f"{config.product_code}/electricity-tariffs/"
                + f"{config.e_tariff_code}/standard-unit-rates/"
                + "?period_from=2022-07-20&page_size=1000"
            )
            return url
        case EnergyType.GAS:
            url = (
                f"{config.api_url}/products/"
                + f"{config.product_code}/gas-tariffs/"
                + f"{config.g_tariff_code}/standard-unit-rates/"
                + "?period_from=2022-07-20&page_size=1000"
            )
            return url
        case _:
            assert_never(energy_type)


def get_consumption_url(energy_type: EnergyType) -> str:
    config = ProjectConfig()
    match energy_type:
        case EnergyType.electricity:
            url = (
                f"{config.api_url}/electricity-meter-points/"
                + f"{config.e_MPAN.get_secret_value()}/meters/"
                + f"{config.e_serial_no.get_secret_value()}/consumption/"
                + "?group_by=day&period_from=2022-07-20&page_size=1000"
            )
            return url
        case EnergyType.gas:
            url = (
                f"{config.api_url}/gas-meter-points/"
                + f"{config.g_MPRN.get_secret_value()}/meters/"
                + f"{config.g_serial_no.get_secret_value()}/consumption/"
                + "?group_by=day&period_from=2022-07-20&page_size=1000"
            )
            return url
        case _:
            assert_never(energy_type)


if __name__ == "__main__":
    print(ProjectConfig().model_dump())
