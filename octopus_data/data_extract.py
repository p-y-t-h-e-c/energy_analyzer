"""Data extractor module."""
from datetime import datetime
from typing import Any, List, Optional

import requests

from data_models import ElectricityData, GasData


class _DataExtractor:
    """Data extractor class."""

    def __init__(self) -> None:
        """Class constructor."""
        self.unit_rates: List[dict[str, Any]] = []
        self.consumption_values: List[dict[str, Any]] = []

    def _get_standard_unit_rates(self, url: str) -> List[dict[str, Any]]:
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
                "date": datetime.fromisoformat(result["valid_from"]).strftime(
                    "%Y-%m-%d"
                ),
                "unit_rate_exc_vat": result["value_exc_vat"],
                "unit_rate_inc_vat": result["value_inc_vat"],
            }
            unit_rates.append(unit_rate)
        unit_rates.sort(key=lambda item: item["date"], reverse=False)
        return unit_rates

    def _get_consumption_values(
        self, url: str, api_key: str, gas_m3_to_kwh_conversion: Optional[float] = 1
    ) -> List[dict[str, Any]]:
        """Export daily consumption values.

        :param url: url for the API request
        :param api_key: API Key required of the request
        :param gas_m3_to_kwh_conversion: gas cubic meter to KWh conversion factor

        :return: A list of dictionaries
        """
        response = requests.get(url, auth=(api_key, ""))
        output_dict = response.json()
        consumption_values = []
        for result in output_dict["results"]:
            consumption_unit = {
                "date": datetime.fromisoformat(result["interval_start"]).strftime(
                    "%Y-%m-%d"
                ),
                "consumption": result["consumption"] * gas_m3_to_kwh_conversion,
            }
            consumption_values.append(consumption_unit)
        consumption_values.sort(key=lambda item: item["date"], reverse=False)
        return consumption_values


class ElectricityDataExtractor(_DataExtractor):
    """Electricity Data Extractor class."""

    def get_electricity_data(
        self, rates_url: str, consumption_url: str, api_key: str
    ) -> ElectricityData:
        """Gather electricity rates and consumption data.

        :param rates_url: rates url for the API request
        :param consumption_url: consumption url for the API request
        :param api_key: API Key required of the request

        :return: instance of ElectricityData class
        """
        electricity_data = ElectricityData()
        electricity_data.unit_rate = self._get_standard_unit_rates(rates_url)
        electricity_data.consumption = self._get_consumption_values(
            consumption_url, api_key
        )
        return electricity_data


class GasDataExtractor(_DataExtractor):
    """Electricity Data Extractor class."""

    def get_gas_data(
        self,
        rates_url: str,
        consumption_url: str,
        api_key: str,
        gas_m3_to_kwh_conversion: Optional[float] = 1,
    ) -> GasData:
        """Gather electricity rates and consumption data.

        :param rates_url: rates url for the API request
        :param consumption_url: consumption url for the API request
        :param api_key: API Key required of the request

        :return: instance of ElectricityData class
        """
        gas_data = GasData()
        gas_data.unit_rate = self._get_standard_unit_rates(rates_url)
        gas_data.consumption = self._get_consumption_values(
            consumption_url, api_key, gas_m3_to_kwh_conversion
        )
        return gas_data


if __name__ == "__main__":
    from config import ProjectConfig, get_consumption_url, get_rates_url
    from data_models import EnergyType

    config = ProjectConfig()

    electricity_data_extractor = ElectricityDataExtractor()
    electricity_data = electricity_data_extractor.get_electricity_data(
        rates_url=get_rates_url(energy_type=EnergyType.ELECTRICITY),
        consumption_url=get_consumption_url(energy_type=EnergyType.ELECTRICITY),
        api_key=config.octopus_api_key.get_secret_value(),
    )

    print(electricity_data.unit_rate)
