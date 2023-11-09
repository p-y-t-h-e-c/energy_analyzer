"""Data extractor module."""
from datetime import datetime
from typing import Any, List, Optional

import requests

from config import get_consumption_url, get_rates_url
from data_models import ElectricityData, EnergyType


class _DataExtractor:
    """Data extractor class."""

    def __init__(self) -> None:
        """Class constructor."""
        self.unit_rates: List[dict[str, Any]] = []
        self.consumption_values: List[dict[str, Any]] = []

    def get_standard_unit_rates(self, url: str) -> List[dict[str, Any]]:
        """Export standard unit rates.

        :param url: url for the API request

        :return: A list of dictionaries
        """
        unit_rates: List[dict[str, Any]] = []
        response = requests.get(url)
        output_dict = response.json()
        # print(output_dict["results"])
        for result in output_dict["results"]:
            unit_rate = {
                "date": datetime.fromisoformat(result["valid_to"]).strftime("%Y-%m-%d"),
                "unit_rate_exc_vat": result["value_exc_vat"],
                "unit_rate_inc_vat": result["value_inc_vat"],
            }
            unit_rates.append(unit_rate)
        return unit_rates

    def get_consumption_values(self, url: str, api_key: str) -> None:
        """Export daily consumption values.

        :param url: url for the API request
        :param api_key: API Key required of the request

        :return: A list of dictionaries
        """
        response = requests.get(url, auth=(api_key, ""))
        output_dict = response.json()
        for result in output_dict["results"]:
            consumption_unit = {
                "date": datetime.fromisoformat(result["interval_start"]).strftime(
                    "%Y-%m-%d"
                ),
                "consumption": result["consumption"],
            }
            self.consumption_values.append(consumption_unit)


# class ElectricityDataExtractor(_DataExtractor):
#     def get_electricity_data(self, url: str, api_key: str):
#         electricity_data = ElectricityData()
#         electricity_data.unit_rate = self.get_standard_unit_rates(url)
#         electricity_data.consumption = self.consumption_values
#         return electricity_data


def get_standard_unit_rates(url: str) -> List[dict[str, Any]]:
    """Export standard unit rates, either electricity or gas.

    :param url: url for the API request

    :return: A list of dictionaries
    """
    response = requests.get(url)
    output_dict = response.json()
    # print(output_dict["results"])
    unit_rates = []
    for result in output_dict["results"]:
        unit_rate = {
            "date": datetime.fromisoformat(result["valid_to"]).strftime("%Y-%m-%d"),
            "unit_rate_exc_vat": result["value_exc_vat"],
            "unit_rate_inc_vat": result["value_inc_vat"],
        }
        unit_rates.append(unit_rate)
    print(unit_rates)
    return unit_rates


def get_consumption_values(
    url: str, api_key: str, gas_m3_to_kwh_conversion: Optional[float] = 1
) -> List[dict[str, Any]]:
    """Export half hourly consumption values either electricity or gas.

    :param url: url for the API request
    :param api_key: API Key required of the request

    :return: A list of dictionaries
    """
    response = requests.get(url, auth=(api_key, ""))
    output_dict = response.json()
    # print(output_dict)
    consumption_values = []
    for result in output_dict["results"]:
        consumption_unit = {
            "date": datetime.fromisoformat(result["interval_start"]).strftime(
                "%Y-%m-%d"
            ),
            "consumption": result["consumption"] * gas_m3_to_kwh_conversion,
        }
        consumption_values.append(consumption_unit)
    print(consumption_values)
    return consumption_values


if __name__ == "__main__":
    from config import ProjectConfig

    url = get_rates_url(EnergyType.ELECTRICITY)
    get_standard_unit_rates(url)

    url = get_consumption_url(EnergyType.ELECTRICITY)
    get_consumption_values(url, ProjectConfig().octopus_api_key.get_secret_value())

    url = get_consumption_url(EnergyType.GAS)
    get_consumption_values(
        url,
        ProjectConfig().octopus_api_key.get_secret_value(),
        ProjectConfig().gas_m3_to_kwh_conversion,
    )
