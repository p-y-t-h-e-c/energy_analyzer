"""Config module."""

import re

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from energy_analyzer.database.db_models import (
    ElectricityWeeklyConsumptionTable2022,
    ElectricityWeeklyConsumptionTable2023,
    ElectricityWeeklyConsumptionTable2024,
    GasWeeklyConsumptionTable2022,
    GasWeeklyConsumptionTable2023,
    GasWeeklyConsumptionTable2024,
    OctopusTables,
)


class ProjectConfig(BaseSettings):
    """Project config class."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Solis Info
    solis_api_url: str = "https://www.soliscloud.com:13333/"
    solis_key_id: SecretStr = Field(default=None, alias="SOLIS_KEY_ID")
    solis_key_secret: SecretStr = Field(default=None, alias="SOLIS_KEY_SECRET")

    # Octopus Info
    octopus_api_url: str = "https://api.octopus.energy/v1"
    account: SecretStr = Field(default=None, alias="OCTOPUS_ACCOUNT_NO")
    octopus_api_key: SecretStr = Field(default=None, alias="OCTOPUS_API_KEY")

    # Electricity Info
    e_import_MPAN: SecretStr = Field(default=None, alias="ELECTRICITY_IMPORT_MPAN")
    e_serial_no: SecretStr = Field(default=None, alias="ELECTRICITY_SERIAL_NO")
    e_export_MPAN: SecretStr = Field(default=None, alias="ELECTRICITY_EXPORT_MPAN")

    # Gas Info
    g_MPRN: SecretStr = Field(default=None, alias="GAS_MPRN")
    g_serial_no: SecretStr = Field(default=None, alias="GAS_SERIAL_NO")
    gas_m3_to_kwh_conversion: float = 1.02264 * 39.5 / 3.6

    # Database
    db_url: SecretStr = Field(default=None, alias="DATABASE_URL")

    # PushStaq
    pushstaq_api_url: str = "https://www.pushstaq.com/api/push/"
    pushstaq_api_key: SecretStr = Field(default=None, alias="PUSHSTAQ_API_KEY")

    POSTGRES_USER: str = "postgres_user"
    POSTGRES_PASSWORD: str = "postgres_password"
    POSTGRES_DB: str = "postgres_db"


class OctopusElectricityImport2022(BaseSettings):
    """Electricity Import 2022."""

    tariff_code: str = "E-1R-VAR-22-04-02-B"
    valid_from: str = "2022-08-01"
    valid_to: str = "2023-02-13"


class OctopusElectricityImport2023(BaseSettings):
    """Electricity Import 2023."""

    tariff_code: str = "E-1R-SILVER-FLEX-22-11-25-B"
    valid_from: str = "2023-02-13"
    valid_to: str = "2024-02-15"


class OctopusElectricityImport2024(BaseSettings):
    """Electricity Import 2024."""

    tariff_code: str = "E-1R-SILVER-23-12-06-B"
    valid_from: str = "2024-02-15"
    valid_to: str = "2025-02-15"


class OctopusGasImport2022(BaseSettings):
    """Electricity Import 2022."""

    tariff_code: str = "G-1R-VAR-22-04-02-B"
    valid_from: str = "2022-08-01"
    valid_to: str = "2023-02-13"


class OctopusGasImport2023(BaseSettings):
    """Electricity Import 2023."""

    tariff_code: str = "G-1R-SILVER-FLEX-22-11-25-B"
    valid_from: str = "2023-02-13"
    valid_to: str = "2024-02-15"


class OctopusGasImport2024(BaseSettings):
    """Electricity Import 2024."""

    tariff_code: str = "G-1R-SILVER-23-12-06-B"
    valid_from: str = "2024-02-15"
    valid_to: str = "2025-02-15"


def get_product_code(tariff_code: str) -> str:
    """Extract product code from a respective tariff code.

    Args:
        tariff_code: a tariff code

    Returns:
        a product code in string format
    """
    product_code: str = re.compile("[EG]-1R-(.*)-B").findall(tariff_code)[0]
    return product_code


class ElectricityWeeklyConsumption2022(BaseSettings):
    """Electricity Weekly Consumption 2022."""

    period_from: str = "2022"
    period_to: str = "2022"
    table: OctopusTables = ElectricityWeeklyConsumptionTable2022


class ElectricityWeeklyConsumption2023(BaseSettings):
    """Electricity Weekly Consumption 2023."""

    period_from: str = "2023"
    period_to: str = "2023"
    table: OctopusTables = ElectricityWeeklyConsumptionTable2023


class ElectricityWeeklyConsumption2024(BaseSettings):
    """Electricity Weekly Consumption 2024."""

    period_from: str = "2024"
    period_to: str = "2024"
    table: OctopusTables = ElectricityWeeklyConsumptionTable2024


class GasWeeklyConsumption2022(BaseSettings):
    """Gas Weekly Consumption 2022."""

    period_from: str = "2022"
    period_to: str = "2022"
    table: OctopusTables = GasWeeklyConsumptionTable2022


class GasWeeklyConsumption2023(BaseSettings):
    """Gas Weekly Consumption 2023."""

    period_from: str = "2023"
    period_to: str = "2023"
    table: OctopusTables = GasWeeklyConsumptionTable2023


class GasWeeklyConsumption2024(BaseSettings):
    """Gas Weekly Consumption 2024."""

    period_from: str = "2024"
    period_to: str = "2024"
    table: OctopusTables = GasWeeklyConsumptionTable2024


if __name__ == "__main__":
    print(ProjectConfig().model_dump())
