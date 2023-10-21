from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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


if __name__ == "__main__":
    print(Settings().model_dump())
