"""Octopus API endpoint url generation module."""

import datetime
import re
from typing import Optional

from energy_analyzer.utils.config import ProjectConfig, get_product_code


class UrlGenerator:
    """URL generator class."""

    def __init__(self, config: ProjectConfig) -> None:
        """Class constructor."""
        self.config = config
        self.date_pattern = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"

    def _get_group_by(self, group_by: Optional[str] = "day") -> str:
        """Get group by condition."""
        return f"group_by={group_by}"

    def _get_period_from(self, period_from: str) -> str:
        """Generate period_from date.

        Args:
            table: respective data table based on which the period
                from is being created
            year_from: a year for witch the weekly data to be gathered
        """
        if re.search(self.date_pattern, period_from):
            return f"period_from={period_from}"
        else:
            # calculate the first Monday of the year
            mon_date = datetime.datetime.strptime(period_from + "1" + "1", "%Y%W%w")
            return f"period_from={mon_date}"

    def _get_period_to(self, period_to: str) -> str:
        """Generate period_to date.

        Args:
            year_to: year to the end of which data to be gathered
        """
        if re.search(self.date_pattern, period_to):
            return f"&period_to={period_to}"
        else:
            period_to = datetime.datetime(
                year=int(period_to), month=12, day=31
            ).strftime("%Y-%m-%d")
            return f"&period_to={period_to}"

    def get_electricity_rates_url(
        self,
        tariff_code: str,
        period_from: str,
        period_to: str,
    ) -> str:
        """Generate electricity standard-unit-rates url.

        Returns:
            electricity standard-unit-rates url
        """
        # page_size - default is 100, maximum is 1,500 for rates
        url = (
            f"{self.config.octopus_api_url}/products/"
            + f"{get_product_code(tariff_code)}/electricity-tariffs/"
            + f"{tariff_code}/standard-unit-rates/"
            + f"?{self._get_period_from(period_from)}"
            + f"{self._get_period_to(period_to)}&page_size=1500"
        )
        return url

    def get_gas_rates_url(
        self,
        tariff_code: str,
        period_from: str,
        period_to: str,
    ) -> str:
        """Create gas standard-unit-rates url.

        Returns:
            gas standard-unit-rates url
        """
        # page_size - default is 100, maximum is 1,500 for rates
        url = (
            f"{self.config.octopus_api_url}/products/"
            + f"{get_product_code(tariff_code)}/gas-tariffs/"
            + f"{tariff_code}/standard-unit-rates/"
            + f"?{self._get_period_from(period_from)}"
            + f"{self._get_period_to(period_to)}&page_size=1500"
        )
        return url

    def get_electricity_consumption_url(
        self, period_from: str, period_to: str, group_by: Optional[str] = "day"
    ) -> str:
        """Generate electricity consumption url.

        Args:
            group_by: default day, can be week for weekly data
            year_from: mainly required for weekly data
            year_to: mainly required for weekly data

        Returns:
            electricity consumption url link
        """
        # page_size - default is 100, maximum is 25,000 for consumption
        url = (
            f"{self.config.octopus_api_url}/electricity-meter-points/"
            + f"{self.config.e_import_MPAN.get_secret_value()}/meters/"
            + f"{self.config.e_serial_no.get_secret_value()}/consumption/"
            + f"?{self._get_group_by(group_by)}&"
            + f"{self._get_period_from(period_from)}"
            + f"{self._get_period_to(period_to)}&page_size=25000"
        )
        return url

    def get_gas_consumption_url(
        self, period_from: str, period_to: str, group_by: Optional[str] = "day"
    ) -> str:
        """Create gas consumption url.

        Args:
            group_by: default day, can be week for weekly data
            year_from: mainly required for weekly data
            year_to: mainly required for weekly data

        Returns:
            gas consumption url link
        """
        # page_size - default is 100, maximum is 25,000 for consumption
        url = (
            f"{self.config.octopus_api_url}/gas-meter-points/"
            + f"{self.config.g_MPRN.get_secret_value()}/meters/"
            + f"{self.config.g_serial_no.get_secret_value()}/consumption/"
            + f"?{self._get_group_by(group_by)}&"
            + f"{self._get_period_from(period_from)}"
            + f"{self._get_period_to(period_to)}&page_size=25000"
        )
        return url

    def get_electricity_export_url(
        self, period_from: str, period_to: str, group_by: Optional[str] = "day"
    ) -> str:
        """Generate electricity consumption url.

        Args:
            group_by: default day, can be week for weekly data
            year_from: mainly required for weekly data
            year_to: mainly required for weekly data

        Returns:
            electricity consumption url link
        """
        # page_size - default is 100, maximum is 25,000 for consumption
        url = (
            f"{self.config.octopus_api_url}/electricity-meter-points/"
            + f"{self.config.e_export_MPAN.get_secret_value()}/meters/"
            + f"{self.config.e_serial_no.get_secret_value()}/consumption/"
            + f"?{self._get_group_by(group_by)}&"
            + f"{self._get_period_from(period_from)}"
            + f"{self._get_period_to(period_to)}&page_size=25000"
        )
        return url


if __name__ == "__main__":
    # url_generator = UrlGenerator()

    # print(url_generator._get_period_to(2023))

    # print(url_generator.get_electricity_rates_url())

    # # print(url_generator.get_electricity_consumption_url())
    # # print(url_generator._get_group_by())
    # print(url_generator._get_period_from(ElectricityRatesTable))

    import re

    date_value = "2023-02-13"
    pattern = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
    if re.search(pattern, date_value):
        print("day date")
    else:
        print("year date")
