"""Data extractor module."""
from abc import ABC
from datetime import date, datetime
from typing import Any, List, Optional

import pandas as pd
from dateutil.parser import parse


class _DataHandler:
    """Data extractor class."""

    @classmethod
    def parse_data_to_df(cls, data: List[dict[str, Any]]) -> pd.DataFrame:
        """Parse the list of dictionaries data into a DataFrame.

        Args:
            data: either electricity or gas data

        Returns:
            df: DataFrame
        """
        df = pd.DataFrame(data)
        return df


class DailyDataHandler(_DataHandler):
    """Daily data extractor class."""

    def format_standard_unit_rates_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Format standard unit rates data.

        Args:
            df: raw data in DataFrame format

        Returns:
            standard_unit_rates_data: formatted data
        """
        standard_unit_rates_data = df.loc[:, ["valid_from", "value_inc_vat"]]
        standard_unit_rates_data.rename(
            columns={
                "valid_from": "date",
                "value_inc_vat": "unit_rate_inc_vat",
            },
            inplace=True,
        )
        standard_unit_rates_data["date"] = standard_unit_rates_data["date"].apply(
            lambda x: parse(datetime.fromisoformat(x).strftime("%Y-%m-%d"))
        )
        standard_unit_rates_data.sort_values(by=["date"], inplace=True)

        return standard_unit_rates_data

    def format_consumption_data(
        self,
        df: pd.DataFrame,
        gas_m3_to_kwh_conversion: float = 1,
    ) -> pd.DataFrame:
        """Format consumption data.

        Args:
            df: raw data in DataFrame format

        Returns:
            consumption_data: formatted data
        """
        consumption_data = df.loc[:, ["interval_start", "consumption"]]
        consumption_data.rename(
            columns={"interval_start": "date"},
            inplace=True,
        )
        consumption_data["date"] = consumption_data["date"].apply(
            lambda x: parse(datetime.fromisoformat(x).strftime("%Y-%m-%d"))
        )
        consumption_data["consumption"] = consumption_data["consumption"].multiply(
            gas_m3_to_kwh_conversion
        )
        consumption_data.sort_values(by=["date"], inplace=True)

        return consumption_data

    def select_data_to_add_to_db(
        self, data: pd.DataFrame, update_point: date
    ) -> pd.DataFrame:
        """Select data to be uploaded based on the latest uploaded data.

        Args:
            data: data fetched via API call in DataFrame format
            update_point: the latest date or week withing respective table

        Returns:
            new_data: only new data to be added to db
        """
        # print(data.iloc[:, 0])
        new_data = data[(data.iloc[:, 0] > update_point)]
        return new_data


class WeeklyDataHandler(_DataHandler):
    """Weekly data extractor class."""

    def format_weekly_consumption_data(
        self, data: pd.DataFrame, gas_m3_to_kwh_conversion: float = 1
    ):
        """Format weekly consumption data."""
        weekly_consumption_data = data.loc[:, ["interval_start", "consumption"]]
        weekly_consumption_data.rename(
            columns={"interval_start": "week"},
            inplace=True,
        )
        weekly_consumption_data["week"] = weekly_consumption_data["week"].apply(
            lambda x: datetime.fromisoformat(x).strftime("%V")
        )

        weekly_consumption_data["consumption"] = weekly_consumption_data[
            "consumption"
        ].multiply(gas_m3_to_kwh_conversion)
        weekly_consumption_data.sort_values(by=["week"], inplace=True)

        return weekly_consumption_data


if __name__ == "__main__":
    from config import ProjectConfig, UrlGenerator

    config = ProjectConfig()
    url_generator = UrlGenerator()

    from data_extract import DataExtractor

    data_extractor = DataExtractor()

    electricity_consumption_weekly_raw = data_extractor.get_consumption_values(
        url=url_generator.get_electricity_consumption_url(
            group_by="week", period_from="2024", period_to="2024"
        ),
        api_key=config.octopus_api_key.get_secret_value(),
    )

    # print(electricity_consumption_weekly_raw)

    weekly_data_handler = WeeklyDataHandler()
    electricity_consumption_weekly_df = weekly_data_handler.parse_data_to_df(
        electricity_consumption_weekly_raw
    )
    electricity_consumption_weekly_formatted = (
        weekly_data_handler.format_weekly_consumption_data(
            electricity_consumption_weekly_df
        )
    )
    print(electricity_consumption_weekly_formatted)
