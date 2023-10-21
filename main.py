from datetime import datetime

import pandas as pd
import requests

from settings import Settings

CONF = Settings()


url = "https://api.octopus.energy/v1/products"
r = requests.get(url, auth=(CONF.api_key.get_secret_value(), ""))
output_dict = r.json()
# print(output_dict)

url = "https://api.octopus.energy/v1/accounts/" + CONF.account.get_secret_value()
r = requests.get(url, auth=(CONF.api_key.get_secret_value(), ""))
output_dict = r.json()
# print(output_dict)


def get_electricity_standard_unit_rates() -> pd.DataFrame:
    #   link = /v1/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates/  # Noqa: E501
    url = (
        CONF.api_url
        + "/products/"
        + CONF.product_code
        + "/electricity-tariffs/"
        + CONF.e_tariff_code
        + "/standard-unit-rates/"
    )
    response = requests.get(url)
    print(response)
    output_dict = response.json()
    # print(output_dict)

    valid_from = [
        datetime.fromisoformat(x["valid_from"]).strftime("%Y-%m-%d")
        for x in output_dict["results"]
    ]
    unit_rate_exc_vat = [x["value_exc_vat"] for x in output_dict["results"]]
    unit_rate_inc_vat = [x["value_inc_vat"] for x in output_dict["results"]]
    unit_rates = pd.DataFrame(
        {
            "date": valid_from,
            "unit_rate_exc_vat": unit_rate_exc_vat,
            "unit_rate_inc_vat": unit_rate_inc_vat,
        }
    )

    print(unit_rates)
    return unit_rates


def get_gas_standard_unit_rates() -> pd.DataFrame:
    # link = https://api.octopus.energy/v1/products/{product_code}/gas-tariffs/{tariff_code}/standard-unit-rates/  # Noqa: E501
    url = (
        CONF.api_url
        + "/products/"
        + CONF.product_code
        + "/gas-tariffs/"
        + CONF.g_tariff_code
        + "/standard-unit-rates/"
    )
    response = requests.get(url)
    print(response)
    output_dict = response.json()
    # print(output_dict)

    valid_from = [
        datetime.fromisoformat(x["valid_from"]).strftime("%Y-%m-%d")
        for x in output_dict["results"]
    ]
    unit_rate_exc_vat = [x["value_exc_vat"] for x in output_dict["results"]]
    unit_rate_inc_vat = [x["value_inc_vat"] for x in output_dict["results"]]
    unit_rates = pd.DataFrame(
        {
            "date": valid_from,
            "unit_rate_exc_vat": unit_rate_exc_vat,
            "unit_rate_inc_vat": unit_rate_inc_vat,
        }
    )

    print(unit_rates)
    return unit_rates


def get_electricity_consumption():
    # https://api.octopus.energy/electricity-meter-points/{mpan}/meters/{serial_number}/consumption/
    # https://api.octopus.energy/gas-meter-points/{mprn}/meters/{serial_number}/consumption/
    url = (
        CONF.api_url
        + "/electricity-meter-points/"
        + CONF.e_MPAN.get_secret_value()
        + "/meters/"
        + CONF.e_serial_no.get_secret_value()
        + "/consumption/"
    )
    response = requests.get(url, auth=(CONF.api_key.get_secret_value(), ""))
    print(response)
    output_dict = response.json()

    interval_start = [
        datetime.fromisoformat(x["interval_start"]).strftime("%Y-%m-%d %H:%M:%S")
        for x in output_dict["results"]
    ]
    interval_end = [
        datetime.fromisoformat(x["interval_end"]).strftime("%Y-%m-%d %H:%M:%S")
        for x in output_dict["results"]
    ]
    consumption = [x["consumption"] for x in output_dict["results"]]

    electricity_consumption = pd.DataFrame(
        {
            "interval_start": interval_start,
            "interval_end": interval_end,
            "consumption": consumption,
        }
    )
    print(electricity_consumption.sort_values(by=["interval_start"]))
    return electricity_consumption.sort_values(by=["interval_start"])


if __name__ == "__main__":
    get_electricity_standard_unit_rates()
    get_gas_standard_unit_rates()
    get_electricity_consumption()
