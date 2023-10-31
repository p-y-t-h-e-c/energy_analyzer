from datetime import datetime
from typing import Any, List

import requests

from config import get_consumption_url, get_rates_url


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


def get_consumption_values(url: str, api_key: str) -> List[dict[str, Any]]:
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
            "consumption": result["consumption"],
        }
        consumption_values.append(consumption_unit)
    # print(consumption_values)
    return consumption_values


if __name__ == "__main__":
    from config import ProjectConfig
    from data_models import EnergyType

    url = get_rates_url(EnergyType.ELECTRICITY)
    get_standard_unit_rates(url)

    url = get_consumption_url(EnergyType.ELECTRICITY)
    get_consumption_values(url, ProjectConfig().api_key.get_secret_value())
