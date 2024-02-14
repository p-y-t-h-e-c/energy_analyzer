"""Config module."""
import datetime
from datetime import date, timedelta
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.exc import NoResultFound

from energy_analyzer.database.db_connector import DbConnector
from energy_analyzer.database.db_models import (
    ElectricityConsumptionTable,
    ElectricityRatesTable,
    GasConsumptionTable,
    GasRatesTable,
)


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


class UrlGenerator:
    """URL generator class."""

    def _get_group_by(self, group_by: Optional[str] = "day") -> str:
        """Get group by condition."""
        return f"group_by={group_by}"

    def _get_period_from(self, table, period_from: Optional[str] = None) -> str:
        """Generate period_from date.

        :param from_date: implicitly specified from date in the format 2023-01-01

        :return: period_from attribute
        """
        if period_from:
            # the first Monday of the year
            mon_date = datetime.datetime.strptime(period_from + "1" + "1", "%Y%W%w")
            # print(mon_date.date())
            return f"period_from={mon_date}"
        else:
            db_url = CONFIG.db_url.get_secret_value()
            db_connector = DbConnector(db_url)
            try:
                date_from = db_connector.get_latest_row(table) - timedelta(days=30)
                return f"period_from={date_from}"
            except NoResultFound:
                return "period_from=2022-07-01"

    def _get_period_to(self, period_to: Optional[str] = None) -> str:
        """Generate period_to date.

        :param to_date: implicitly specified to date in the format 2023-12-31

        :return: period_to attribute
        """
        if period_to:
            period_to = datetime.datetime(
                year=int(period_to), month=12, day=31
            ).strftime("%Y-%m-%d")
            return f"&period_to={period_to}"
        else:
            date_to = date.today() + timedelta(days=14)
            return f"&period_to={date_to}"

    def get_electricity_rates_url(
        self, period_from: Optional[str] = None, period_to: Optional[str] = None
    ) -> str:
        """Create electricity rates url.

        :param period_from:
        :param period_to:

        :return: rates url link
        """
        # page_size - default is 100, maximum is 1,500 for rates
        url = (
            f"{CONFIG.octopus_api_url}/products/"
            + f"{CONFIG.product_code}/electricity-tariffs/"
            + f"{CONFIG.e_tariff_code}/standard-unit-rates/"
            + f"?{self._get_period_from(ElectricityRatesTable, period_from)}"
            + f"{self._get_period_to(period_to)}&page_size=1500"
        )
        return url

    def get_gas_rates_url(
        self, period_from: Optional[str] = None, period_to: Optional[str] = None
    ) -> str:
        """Create gas rates url.

        :param period_from:
        :param period_to:

        :return: rates url link
        """
        # page_size - default is 100, maximum is 1,500 for rates
        url = (
            f"{CONFIG.octopus_api_url}/products/"
            + f"{CONFIG.product_code}/gas-tariffs/"
            + f"{CONFIG.g_tariff_code}/standard-unit-rates/"
            + f"?{self._get_period_from(GasRatesTable, period_from)}"
            + f"{self._get_period_to(period_to)}&page_size=1500"
        )
        return url

    def get_electricity_consumption_url(
        self,
        group_by: Optional[str] = "day",
        period_from: Optional[str] = None,
        period_to: Optional[str] = None,
    ) -> str:
        """Create electricity consumption url.

        :param energy_type: either electricity or gas energy type

        :return: consumption url link
        """
        # page_size - default is 100, maximum is 25,000 for consumption
        url = (
            f"{CONFIG.octopus_api_url}/electricity-meter-points/"
            + f"{CONFIG.e_MPAN.get_secret_value()}/meters/"
            + f"{CONFIG.e_serial_no.get_secret_value()}/consumption/"
            + f"?{self._get_group_by(group_by)}&"
            + f"{self._get_period_from(ElectricityConsumptionTable, period_from)}"
            + f"{self._get_period_to(period_to)}&page_size=25000"
        )
        return url

    def get_gas_consumption_url(
        self,
        group_by: Optional[str] = "day",
        period_from: Optional[str] = None,
        period_to: Optional[str] = None,
    ) -> str:
        """Create gas consumption url.

        :param energy_type: either electricity or gas energy type

        :return: consumption url link
        """
        # page_size - default is 100, maximum is 25,000 for consumption
        url = (
            f"{CONFIG.octopus_api_url}/gas-meter-points/"
            + f"{CONFIG.g_MPRN.get_secret_value()}/meters/"
            + f"{CONFIG.g_serial_no.get_secret_value()}/consumption/"
            + f"?{self._get_group_by(group_by)}&"
            + f"{self._get_period_from(GasConsumptionTable, period_from)}"
            + f"{self._get_period_to(period_to)}&page_size=25000"
        )
        return url


if __name__ == "__main__":
    # print(ProjectConfig().model_dump())

    url_generator = UrlGenerator()
    # # print(url_generator.get_electricity_consumption_url())
    # # print(url_generator._get_group_by())
    print(url_generator._get_period_from(ElectricityConsumptionTable))
    # print(url_generator.get_electricity_rates_url())
