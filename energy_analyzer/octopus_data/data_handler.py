"""Data extractor module."""

from datetime import date, datetime, timedelta
from typing import Any, List

import pandas as pd
from dateutil import parser
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

    @classmethod
    def select_data_to_add_to_db(
        cls, data: pd.DataFrame, update_point: date | None
    ) -> pd.DataFrame:
        """Select data to be uploaded based on the latest uploaded data.

        Args:
            data: data fetched via API call in DataFrame format
            update_point: the latest date or week withing respective table

        Returns:
            new_data: only new data to be added to db
        """
        if update_point:
            new_data = data[(data.iloc[:, 0] > update_point)]
            return new_data
        else:
            return data


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
            lambda x: parse(
                (parser.isoparse(x) + timedelta(hours=2)).strftime("%Y-%m-%d")
            )
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
            lambda x: parse(parser.isoparse(x).strftime("%Y-%m-%d"))
        )
        consumption_data["consumption"] = consumption_data["consumption"].multiply(
            gas_m3_to_kwh_conversion
        )
        consumption_data.sort_values(by=["date"], inplace=True)
        consumption_data = consumption_data.iloc[:-1]
        return consumption_data


class WeeklyDataHandler(_DataHandler):
    """Weekly data extractor class."""

    def format_weekly_consumption_data(
        self, data: pd.DataFrame, gas_m3_to_kwh_conversion: float = 1
    ):
        """Format weekly consumption data."""
        weekly_consumption_data = data.loc[:, ["interval_start", "consumption"]]
        weekly_consumption_data.rename(
            columns={"interval_start": "date"},
            inplace=True,
        )
        weekly_consumption_data["date"] = weekly_consumption_data["date"].apply(
            lambda x: parse(parser.isoparse(x).strftime("%Y-%m-%d"))
        )
        weekly_data = weekly_consumption_data["date"].apply(lambda x: x.strftime("%V"))
        weekly_consumption_data.insert(loc=0, column="week", value=weekly_data)
        # weekly_consumption_data["week"] = weekly_consumption_data["date"].apply(
        #     lambda x: x.strftime("%V")
        # )

        weekly_consumption_data["consumption"] = weekly_consumption_data[
            "consumption"
        ].multiply(gas_m3_to_kwh_conversion)
        weekly_consumption_data.sort_values(by=["week"], inplace=True)
        last_week_date = weekly_consumption_data["date"].iloc[-1]
        if last_week_date < (datetime.now() - timedelta(weeks=1)):
            return weekly_consumption_data
        else:
            weekly_consumption_data = weekly_consumption_data.iloc[:-2]
            return weekly_consumption_data


if __name__ == "__main__":
    from energy_analyzer.octopus_data.url_generator import UrlGenerator
    from energy_analyzer.utils.config import (
        OctopusElectricityImport2023,
        OctopusGasImport2024,
        ProjectConfig,
    )

    config = ProjectConfig()
    url_generator = UrlGenerator(config)

    from data_extract import DataExtractor

    data_extractor = DataExtractor()
    electricity_tariff = OctopusElectricityImport2023()
    gas_tariff = OctopusGasImport2024()
    data_handler = DailyDataHandler()
    weekly_data_handler = WeeklyDataHandler()

    # electricity_unit_rates = data_extractor.get_standard_unit_rates(
    #     rates_url=url_generator.get_electricity_rates_url(
    #         electricity_tariff.tariff_code,
    #         electricity_tariff.valid_from,
    #         electricity_tariff.valid_to,
    #     )
    # )
    # electricity_unit_rates_df = data_handler.parse_data_to_df(electricity_unit_rates)
    # electricity_unit_rates_formatted = data_handler.format_standard_unit_rates_data(
    #     electricity_unit_rates_df
    # )

    # print(electricity_unit_rates_formatted)

    # electricity_consumption_url = url_generator.get_electricity_consumption_url(
    #     period_from=electricity_tariff.valid_from,
    #     period_to=electricity_tariff.valid_to,
    # )
    # electricity_daily_consumption = data_extractor.get_consumption_values(
    #     electricity_consumption_url, config.octopus_api_key.get_secret_value()
    # )
    # electricity_daily_consumption_df = data_handler.parse_data_to_df(
    #     electricity_daily_consumption
    # )
    # electricity_daily_consumption_formatted = data_handler.format_consumption_data(
    #     electricity_daily_consumption_df
    # )
    # print(electricity_daily_consumption_formatted)
    # period_to = (datetime.now() + timedelta(hours=0)).strftime("%Y-%m-%d")
    # print(period_to)

    gas_weekly_consumption_url = url_generator.get_gas_consumption_url(
        period_from="2023",
        period_to="2023",
        group_by="week",
    )
    gas_weekly_consumption = data_extractor.get_consumption_values(
        gas_weekly_consumption_url, config.octopus_api_key.get_secret_value()
    )
    gas_weekly_consumption_df = data_handler.parse_data_to_df(gas_weekly_consumption)

    gas_weekly_consumption_formatted = (
        weekly_data_handler.format_weekly_consumption_data(
            gas_weekly_consumption_df, config.gas_m3_to_kwh_conversion
        )
    )
    print(gas_weekly_consumption_formatted)
