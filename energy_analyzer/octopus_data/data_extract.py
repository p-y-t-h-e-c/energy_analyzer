"""Data extractor module."""

from typing import Any, List

import requests


class DataExtractor:
    """Data extractor class."""

    def get_standard_unit_rates(self, rates_url: str) -> List[dict[str, Any]]:
        """Export standard unit rates.

        Args:
            url: specific standard unit rates url for the API request

        Returns:
            output["results"]: standard unit rates data in
                                a format of list of dictionaries
        """
        response = requests.get(rates_url)
        output = response.json()
        return output["results"]

    def get_consumption_values(
        self,
        consumption_url: str,
        api_key: str,
    ) -> List[dict[str, Any]]:
        """Extract consumption values from the API call.

        Args:
            url: specific consumption url for the API request
            api_key: API Key required for the request

        Returns:
            output["results"]: standard unit rates data in
                                a format of list of dictionaries
        """
        response = requests.get(consumption_url, auth=(api_key, ""))
        output = response.json()
        return output["results"]


if __name__ == "__main__":
    from energy_analyzer.octopus_data.tariffs_data_models import (
        OctopusElectricityImport2024,
        OctopusGasImport2024,
        get_product_code,
    )
    from energy_analyzer.octopus_data.url_generator import UrlGenerator
    from energy_analyzer.utils.config import ProjectConfig

    config = ProjectConfig()
    url_generator = UrlGenerator(config)
    tariff_info = OctopusElectricityImport2024()

    data_extractor = DataExtractor()
    rates_url = url_generator.get_electricity_rates_url(
        tariff_code=tariff_info.tariff_code,
        period_from=tariff_info.valid_from,
        period_to=tariff_info.valid_to,
    )
    print(rates_url)
    electricity_daily_rates = data_extractor.get_standard_unit_rates(rates_url)
    print(electricity_daily_rates)

    # url = (
    #     f"{config.octopus_api_url}/electricity-meter-points/"
    #     + "2700008467789/meters/"
    #     + f"{config.e_serial_no.get_secret_value()}/consumption/"
    #     + "?group_by=day&page_size=25000"
    # )
    # response = requests.get(
    #     url_generator.get_electricity_export_url(year_from="2022", year_to=2024),
    #     auth=(config.octopus_api_key.get_secret_value(), ""),
    # )
    # output = response.json()

    # print(output["results"])
