from datetime import datetime

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


def get_electricity_consumption():
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
    from config import get_consumption_url, get_rates_url
    from data_models import EnergyType
    from database.db_connector import DbConnector
    from database.db_models import (
        Base,
        ElectricityConsumptionTable,
        ElectricityRatesTable,
        GasConsumptionTable,
        GasRatesTable,
    )
    from octopus_data_extract.data_extract import (
        get_consumption_values,
        get_standard_unit_rates,
    )

    db_connector = DbConnector(CONFIG.db_url.get_secret_value())
    Base.metadata.drop_all(db_connector._engine)
    Base.metadata.create_all(db_connector._engine)

    electricity_rates_url = get_rates_url(EnergyType.electricity)
    electricity_unit_rates = get_standard_unit_rates(electricity_rates_url)

    for unit_rate in electricity_unit_rates:
        db_connector.add_unit_rates(
            ref_table=ElectricityRatesTable.db_table(), unit_rate=unit_rate
        )

    gas_rates_url = get_rates_url(EnergyType.gas)
    gas_unit_rates = get_standard_unit_rates(gas_rates_url)

    for unit_rate in gas_unit_rates:
        db_connector.add_unit_rates(
            ref_table=GasRatesTable.db_table(), unit_rate=unit_rate
        )

    electricity_consumption_url = get_consumption_url(EnergyType.electricity)
    electricity_consumption_values = get_consumption_values(
        electricity_consumption_url, CONFIG.api_key.get_secret_value()
    )

    for consumption_unit in electricity_consumption_values:
        db_connector.add_consumption_values(
            ref_table=ElectricityConsumptionTable.db_table(),
            consumption_unit=consumption_unit,
        )

    gas_consumption_url = get_consumption_url(EnergyType.gas)
    gas_consumption_values = get_consumption_values(
        gas_consumption_url, CONFIG.api_key.get_secret_value()
    )

    for consumption_unit in gas_consumption_values:
        db_connector.add_consumption_values(
            ref_table=GasConsumptionTable.db_table(),
            consumption_unit=consumption_unit,
        )

    # get_gas_standard_unit_rates()
    # get_electricity_consumption()
    # get_electricity_standard_unit_rates()
