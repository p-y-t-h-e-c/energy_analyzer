from datetime import datetime
from typing import Any, List

import pandas as pd
import requests

from config import ProjectConfig
from database.db_connector import DbConnector

CONFIG = ProjectConfig()
DB_CONNECTOR = DbConnector(CONFIG.db_url.get_secret_value())


url = "https://api.octopus.energy/v1/products"
r = requests.get(url, auth=(CONFIG.api_key.get_secret_value(), ""))
output_dict = r.json()
# print(output_dict)


def get_account_info():
    url = "https://api.octopus.energy/v1/accounts/" + CONFIG.account.get_secret_value()
    r = requests.get(url, auth=(CONFIG.api_key.get_secret_value(), ""))
    output_dict = r.json()
    # print(output_dict)


def get_gas_standard_unit_rates() -> pd.DataFrame:
    # link = https://api.octopus.energy/v1/products/{product_code}/gas-tariffs/{tariff_code}/standard-unit-rates/  # Noqa: E501
    url = (
        CONFIG.api_url
        + "/products/"
        + CONFIG.product_code
        + "/gas-tariffs/"
        + CONFIG.g_tariff_code
        + "/standard-unit-rates/"
    )
    response = requests.get(url)
    print(response)
    output_dict = response.json()
    # print(output_dict)

    valid_to = [
        datetime.fromisoformat(x["valid_to"]).strftime("%Y-%m-%d")
        for x in output_dict["results"]
    ]
    unit_rate_exc_vat = [x["value_exc_vat"] for x in output_dict["results"]]
    unit_rate_inc_vat = [x["value_inc_vat"] for x in output_dict["results"]]
    unit_rates = pd.DataFrame(
        {
            "date": valid_to,
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
        CONFIG.api_url
        + "/electricity-meter-points/"
        + CONFIG.e_MPAN.get_secret_value()
        + "/meters/"
        + CONFIG.e_serial_no.get_secret_value()
        + "/consumption/"
    )
    response = requests.get(url, auth=(CONFIG.api_key.get_secret_value(), ""))

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
    from database.db_connector import DbConnector
    from database.db_models import Base, ElectricityRatesTable, GasRatesTable
    from octopus_data_extract.data_extract import get_standard_unit_rates

    db_connector = DbConnector(CONFIG.db_url.get_secret_value())
    Base.metadata.drop_all(db_connector._engine)
    Base.metadata.create_all(db_connector._engine)

    electricity_unit_rates = get_standard_unit_rates(
        api_url=CONFIG.api_url,
        product_code=CONFIG.product_code,
        tariff_type=CONFIG.electricity_tariff,
        tariff_code=CONFIG.e_tariff_code,
    )
    for unit_rate in electricity_unit_rates:
        db_connector.add_unit_rates(
            ref_table=ElectricityRatesTable.db_table(), unit_rate=unit_rate
        )

    gas_unit_rates = get_standard_unit_rates(
        api_url=CONFIG.api_url,
        product_code=CONFIG.product_code,
        tariff_type=CONFIG.gas_tariff,
        tariff_code=CONFIG.g_tariff_code,
    )
    for unit_rate in gas_unit_rates:
        db_connector.add_unit_rates(
            ref_table=GasRatesTable.db_table(), unit_rate=unit_rate
        )
    # get_gas_standard_unit_rates()
    # get_electricity_consumption()
    # get_electricity_standard_unit_rates()
