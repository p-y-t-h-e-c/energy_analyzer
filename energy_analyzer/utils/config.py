"""Config module."""

import re

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


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


if __name__ == "__main__":
    print(ProjectConfig().model_dump())
