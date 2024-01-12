"""Data extractor module."""
from abc import ABC
from datetime import datetime
from typing import Any, List, Optional

import requests

from data_models import ElectricityData, GasData


class _DataExtractor(ABC):
    """Data extractor class."""


class DailyDataExtractor(_DataExtractor):
    """Daily data extractor class."""

    def __init__(self) -> None:
        """Class constructor method."""
        self.unit_rates: List[dict[str, Any]] = []
        self.consumption_values: List[dict[str, Any]] = []

    def get_standard_unit_rates(self, rates_url: str) -> List[dict[str, Any]]:
        """Export standard unit rates.

        :param url: url for the API request

        :return: A list of dictionaries
        """
        response = requests.get(rates_url)
        output = response.json()
        # print(output["results"])

        for result in output["results"]:
            unit_rate = {
                "date": datetime.fromisoformat(result["valid_from"]).strftime(
                    "%Y-%m-%d"
                ),
                "unit_rate_exc_vat": result["value_exc_vat"],
                "unit_rate_inc_vat": result["value_inc_vat"],
            }
            self.unit_rates.append(unit_rate)
        self.unit_rates.sort(key=lambda item: item["date"], reverse=False)
        return self.unit_rates

    def _get_consumption_values(
        self,
        consumption_url: str,
        api_key: str,
        gas_m3_to_kwh_conversion: Optional[float] = 1,
    ) -> List[dict[str, Any]]:
        """Extract daily consumption values.

        :param url: url for the API request
        :param api_key: API Key required of the request
        :param gas_m3_to_kwh_conversion: gas cubic meter to KWh conversion factor

        :return: A list of dictionaries
        """
        response = requests.get(consumption_url, auth=(api_key, ""))
        output = response.json()
        # print(output["results"])

        for result in output["results"]:
            consumption_unit = {
                "date": datetime.fromisoformat(result["interval_start"]).strftime(
                    "%Y-%m-%d"
                ),
                "consumption": result["consumption"] * gas_m3_to_kwh_conversion,
            }
            self.consumption_values.append(consumption_unit)
        self.consumption_values.sort(key=lambda item: item["date"], reverse=False)
        return self.consumption_values


#     def _get_weekly_consumption_values(
#         self, url: str, api_key: str, gas_m3_to_kwh_conversion: Optional[float] = 1
#     ) -> List[dict[str, Any]]:
#         """Extract weekly consumption values.

#         :param url: url for the API request
#         :param api_key: API Key required of the request
#         :param gas_m3_to_kwh_conversion: gas cubic meter to KWh conversion factor

#         :return: A list of dictionaries
#         """
#         response = requests.get(url, auth=(api_key, ""))
#         output_dict = response.json()
#         consumption_values = []
#         for result in output_dict["results"]:
#             consumption_unit = {
#                 "week": datetime.fromisoformat(result["interval_start"]).strftime("%V"),
#                 "consumption": result["consumption"] * gas_m3_to_kwh_conversion,
#             }
#             consumption_values.append(consumption_unit)
#         consumption_values.sort(key=lambda item: item["week"], reverse=False)
#         return consumption_values


# class ElectricityDataExtractor(_DataExtractor):
#     """Electricity Data Extractor class."""

#     def get_electricity_data(
#         self,
#         rates_url: str,
#         consumption_url: str,
#         api_key: str,
#         group_by: str = "day",
#     ) -> ElectricityData:
#         """Gather electricity rates and consumption data.

#         :param rates_url: rates url for the API request
#         :param consumption_url: consumption url for the API request
#         :param api_key: API Key required of the request

#         :return: instance of ElectricityData class
#         """
#         electricity_data = ElectricityData()
#         if group_by == "day":
#             electricity_data.unit_rate = self._get_standard_unit_rates(rates_url)

#             electricity_data.consumption = self._get_consumption_values(
#                 consumption_url, api_key
#             )
#         else:
#             electricity_data.consumption = self._get_weekly_consumption_values(
#                 consumption_url, api_key
#             )

#         return electricity_data


# class GasDataExtractor(_DataExtractor):
#     """Electricity Data Extractor class."""

#     def get_gas_data(
#         self,
#         rates_url: str,
#         consumption_url: str,
#         api_key: str,
#         gas_m3_to_kwh_conversion: float,
#         group_by: str = "day",
#     ) -> GasData:
#         """Gather electricity rates and consumption data.

#         :param rates_url: rates url for the API request
#         :param consumption_url: consumption url for the API request
#         :param api_key: API Key required of the request

#         :return: instance of ElectricityData class
#         """
#         gas_data = GasData()
#         if group_by == "day":
#             gas_data.unit_rate = self._get_standard_unit_rates(rates_url)

#             gas_data.consumption = self._get_consumption_values(
#                 consumption_url, api_key, gas_m3_to_kwh_conversion
#             )
#         else:
#             gas_data.consumption = self._get_weekly_consumption_values(
#                 consumption_url, api_key, gas_m3_to_kwh_conversion
#             )
#         return gas_data


if __name__ == "__main__":
    from config import ProjectConfig, UrlGenerator

    config = ProjectConfig()
    url_generator = UrlGenerator()

    daily_data_extractor = DailyDataExtractor()
    electricity_daily_rates = daily_data_extractor.get_standard_unit_rates(
        url=url_generator.get_electricity_rates_url()
    )
    print(electricity_daily_rates)
