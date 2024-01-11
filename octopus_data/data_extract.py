"""Data extractor module."""
from datetime import datetime
from typing import Any, List, Optional

import requests

from data_models import ElectricityData, GasData


class _DataExtractor:
    """Data extractor class."""

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
        """Extract daily consumption values.

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

    def _get_weekly_consumption_values(
        self, url: str, api_key: str, gas_m3_to_kwh_conversion: Optional[float] = 1
    ) -> List[dict[str, Any]]:
        """Extract weekly consumption values.

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
                "week": datetime.fromisoformat(result["interval_start"]).strftime("%V"),
                "consumption": result["consumption"] * gas_m3_to_kwh_conversion,
            }
            consumption_values.append(consumption_unit)
        consumption_values.sort(key=lambda item: item["week"], reverse=False)
        return consumption_values


class ElectricityDataExtractor(_DataExtractor):
    """Electricity Data Extractor class."""

    def get_electricity_data(
        self,
        rates_url: str,
        consumption_url: str,
        api_key: str,
        group_by: str = "day",
    ) -> ElectricityData:
        """Gather electricity rates and consumption data.

        :param rates_url: rates url for the API request
        :param consumption_url: consumption url for the API request
        :param api_key: API Key required of the request

        :return: instance of ElectricityData class
        """
        electricity_data = ElectricityData()
        if group_by == "day":
            electricity_data.unit_rate = self._get_standard_unit_rates(rates_url)

            electricity_data.consumption = self._get_consumption_values(
                consumption_url, api_key
            )
        else:
            electricity_data.consumption = self._get_weekly_consumption_values(
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
        gas_m3_to_kwh_conversion: float,
        group_by: str = "day",
    ) -> GasData:
        """Gather electricity rates and consumption data.

        :param rates_url: rates url for the API request
        :param consumption_url: consumption url for the API request
        :param api_key: API Key required of the request

        :return: instance of ElectricityData class
        """
        gas_data = GasData()
        if group_by == "day":
            gas_data.unit_rate = self._get_standard_unit_rates(rates_url)

            gas_data.consumption = self._get_consumption_values(
                consumption_url, api_key, gas_m3_to_kwh_conversion
            )
        else:
            gas_data.consumption = self._get_weekly_consumption_values(
                consumption_url, api_key, gas_m3_to_kwh_conversion
            )
        return gas_data


if __name__ == "__main__":
    import pandas as pd

    from config import ProjectConfig, UrlGenerator

    config = ProjectConfig()
    url_generator = UrlGenerator()

    # electricity_data_extractor = ElectricityDataExtractor()
    # electricity_data = electricity_data_extractor.get_electricity_data(
    #     rates_url=url_generator.get_electricity_rates_url(),
    #     consumption_url=url_generator.get_electricity_consumption_url(
    #         group_by="week", period_from="2022", period_to="2022-12-31"
    #     ),
    #     api_key=config.octopus_api_key.get_secret_value(),
    # )

    # gas_data_extractor = GasDataExtractor()
    # gas_data = gas_data_extractor.get_gas_data(
    #     rates_url=url_generator.get_gas_rates_url(),
    #     consumption_url=url_generator.get_gas_consumption_url(
    #         group_by="week", period_from="2022", period_to="2022-12-31"
    #     ),
    #     api_key=config.octopus_api_key.get_secret_value(),
    #     gas_m3_to_kwh_conversion=config.gas_m3_to_kwh_conversion,
    # )

    # print(electricity_data.unit_rate)
    # print(gas_data.unit_rate)

    from data_models import ElectricityData, GasData, RatesData

    def get_standard_unit_rates(
        url: str = url_generator.get_electricity_rates_url(),
    ) -> List[RatesData]:
        """Export standard unit rates.

        :param url: url for the API request

        :return: A list of dictionaries
        """
        unit_rates: List[RatesData] = []
        response = requests.get(url)
        output_dict = response.json()

        for result in output_dict["results"]:
            unit_rate = {
                "date": datetime.fromisoformat(result["valid_from"]).strftime(
                    "%Y-%m-%d"
                ),
                "unit_rate_exc_vat": result["value_exc_vat"],
                "unit_rate_inc_vat": result["value_inc_vat"],
            }
            unit_rates.append(RatesData(**unit_rate))
        unit_rates.sort(key=lambda item: item.date, reverse=False)
        return unit_rates

    unit_rates = get_standard_unit_rates()
    # print(unit_rates)
    print([(item.date, item.unit_rate_inc_vat) for item in unit_rates])
