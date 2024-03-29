"""Octopus API endpoint url generation module."""

import datetime
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.exc import NoResultFound

from energy_analyzer.database.db_connector import DbConnector
from energy_analyzer.database.db_models import (
    ElectricityConsumptionTable,
    ElectricityExportTable,
    ElectricityRatesTable,
    GasConsumptionTable,
    GasRatesTable,
)
from energy_analyzer.utils.config import ProjectConfig

CONFIG = ProjectConfig()


class UrlGenerator:
    """URL generator class."""

    def _get_group_by(self, group_by: Optional[str] = "day") -> str:
        """Get group by condition."""
        return f"group_by={group_by}"

    def _get_period_from(self, table, year_from: Optional[str] = None) -> str:
        """Generate period_from date.

        Args:
            table: respective data table based on which the period
                from is being created
            year_from: a year for witch the weekly data to be gathered
        """
        if year_from:
            # calculate the first Monday of the year
            mon_date = datetime.datetime.strptime(year_from + "1" + "1", "%Y%W%w")
            return f"period_from={mon_date}"
        else:
            db_url = CONFIG.db_url.get_secret_value()
            db_connector = DbConnector(db_url)
            try:
                date_from = db_connector.get_latest_row(table) - timedelta(days=60)
                return f"period_from={date_from}"
            except NoResultFound:
                return "period_from=2022-07-01"

    def _get_period_to(self, year_to: Optional[int] = None) -> str:
        """Generate period_to date.

        Args:
            year_to: year to the end of which data to be gathered
        """
        if year_to:
            period_to = datetime.datetime(year=year_to, month=12, day=31).strftime(
                "%Y-%m-%d"
            )
            return f"&period_to={period_to}"
        else:
            date_to = date.today() + timedelta(days=14)
            return f"&period_to={date_to}"

    def get_electricity_rates_url(self) -> str:
        """Generate electricity standard-unit-rates url.

        Returns:
            electricity standard-unit-rates url
        """
        # page_size - default is 100, maximum is 1,500 for rates
        url = (
            f"{CONFIG.octopus_api_url}/products/"
            + f"{CONFIG.product_code}/electricity-tariffs/"
            + f"{CONFIG.e_tariff_code}/standard-unit-rates/"
            + f"?{self._get_period_from(ElectricityRatesTable)}"
            + f"{self._get_period_to()}&page_size=1500"
        )
        return url

    def get_gas_rates_url(self) -> str:
        """Create gas standard-unit-rates url.

        Returns:
            gas standard-unit-rates url
        """
        # page_size - default is 100, maximum is 1,500 for rates
        url = (
            f"{CONFIG.octopus_api_url}/products/"
            + f"{CONFIG.product_code}/gas-tariffs/"
            + f"{CONFIG.g_tariff_code}/standard-unit-rates/"
            + f"?{self._get_period_from(GasRatesTable)}"
            + f"{self._get_period_to()}&page_size=1500"
        )
        return url

    def get_electricity_consumption_url(
        self,
        group_by: Optional[str] = "day",
        year_from: Optional[str] = None,
        year_to: Optional[int] = None,
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
            f"{CONFIG.octopus_api_url}/electricity-meter-points/"
            + f"{CONFIG.e_MPAN.get_secret_value()}/meters/"
            + f"{CONFIG.e_serial_no.get_secret_value()}/consumption/"
            + f"?{self._get_group_by(group_by)}&"
            + f"{self._get_period_from(ElectricityConsumptionTable, year_from)}"
            + f"{self._get_period_to(year_to)}&page_size=25000"
        )
        return url

    def get_gas_consumption_url(
        self,
        group_by: Optional[str] = "day",
        year_from: Optional[str] = None,
        year_to: Optional[int] = None,
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
            f"{CONFIG.octopus_api_url}/gas-meter-points/"
            + f"{CONFIG.g_MPRN.get_secret_value()}/meters/"
            + f"{CONFIG.g_serial_no.get_secret_value()}/consumption/"
            + f"?{self._get_group_by(group_by)}&"
            + f"{self._get_period_from(GasConsumptionTable, year_from)}"
            + f"{self._get_period_to(year_to)}&page_size=25000"
        )
        return url

    def get_electricity_export_url(
        self,
        group_by: Optional[str] = "day",
        year_from: Optional[str] = None,
        year_to: Optional[int] = None,
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
            f"{CONFIG.octopus_api_url}/electricity-meter-points/"
            + f"{CONFIG.e_export_MPAN.get_secret_value()}/meters/"
            + f"{CONFIG.e_serial_no.get_secret_value()}/consumption/"
            + f"?{self._get_group_by(group_by)}&"
            + f"{self._get_period_from(ElectricityExportTable, year_from)}"
            + f"{self._get_period_to(year_to)}&page_size=25000"
        )
        return url


if __name__ == "__main__":
    url_generator = UrlGenerator()

    print(url_generator._get_period_to(2023))

    print(url_generator.get_electricity_rates_url())

    # # print(url_generator.get_electricity_consumption_url())
    # # print(url_generator._get_group_by())
    # print(url_generator._get_period_from(ElectricityRatesTable))
