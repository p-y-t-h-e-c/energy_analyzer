from datetime import datetime
from typing import Any, List

import requests


def get_standard_unit_rates(
    api_url, product_code, tariff_type, tariff_code
) -> List[dict[str, Any]]:
    #   link = /v1/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates/  # Noqa: E501
    url = (
        api_url
        + "/products/"
        + product_code
        + tariff_type
        + tariff_code
        + "/standard-unit-rates/"
        + "?period_from=2022-07-20T00:00Z"
    )
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


if __name__ == "__main__":
    from main import CONFIG

    get_standard_unit_rates(
        api_url=CONFIG.api_url,
        product_code=CONFIG.product_code,
        tariff_type=CONFIG.electricity_tariff,
        tariff_code=CONFIG.e_tariff_code,
    )
