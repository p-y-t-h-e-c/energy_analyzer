"""Data extractor module."""
from typing import Any, List

import requests


class DataExtractor:
    """Data extractor class."""

    def get_standard_unit_rates(self, url: str) -> List[dict[str, Any]]:
        """Export standard unit rates.

        Args:
            url: specific standard unit rates url for the API request

        Returns:
            output["results"]: standard unit rates data in
                                a format of list of dictionaries
        """
        response = requests.get(url)
        output = response.json()
        return output["results"]

    def get_consumption_values(
        self,
        url: str,
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
        response = requests.get(url, auth=(api_key, ""))
        output = response.json()
        return output["results"]


if __name__ == "__main__":
    from config import ProjectConfig, UrlGenerator

    config = ProjectConfig()
    url_generator = UrlGenerator()

    data_extractor = DataExtractor()
    electricity_daily_rates = data_extractor.get_standard_unit_rates(
        url=url_generator.get_electricity_rates_url()
    )
    print(electricity_daily_rates)
