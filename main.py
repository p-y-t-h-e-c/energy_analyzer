"""Main module."""
import time

import requests
from prefect import flow, logging, task

from config import ProjectConfig, UrlGenerator
from data_models import ElectricityData, GasData
from database.db_connector import DbConnector
from database.db_models import (
    ElectricityConsumptionTable,
    ElectricityRatesTable,
    ElectricityWeeklyConsumptionTable2022,
    ElectricityWeeklyConsumptionTable2023,
    GasConsumptionTable,
    GasRatesTable,
)
from octopus_data.data_extract import ElectricityDataExtractor, GasDataExtractor

CONFIG = ProjectConfig()
URL_GENERATOR = UrlGenerator()
DB_CONNECTOR = DbConnector(CONFIG.db_url.get_secret_value())
LOGGER = logging.get_logger()

url = "https://api.octopus.energy/v1/products"
r = requests.get(url, auth=(CONFIG.octopus_api_key.get_secret_value(), ""))
output_dict = r.json()
# print(output_dict)


def get_account_info():
    """Get Octopus account info."""
    url = "https://api.octopus.energy/v1/accounts/" + CONFIG.account.get_secret_value()
    r = requests.get(url, auth=(CONFIG.octopus_api_key.get_secret_value(), ""))
    output_dict = r.json()
    return output_dict["properties"]


@task(name="Get Octopus Electricity Data")
def get_octopus_electricity_data() -> ElectricityData:
    """Get Octopus electricity data."""
    electricity_data_extractor = ElectricityDataExtractor()
    electricity_data = electricity_data_extractor.get_electricity_data(
        rates_url=URL_GENERATOR.get_electricity_rates_url(),
        consumption_url=URL_GENERATOR.get_electricity_consumption_url(),
        api_key=CONFIG.octopus_api_key.get_secret_value(),
    )
    return electricity_data


@task(name="Add Octopus Electricity Data to Db")
def add_octopus_electricity_data_to_db(electricity_data: ElectricityData) -> None:
    """Process Octopus electricity data.

    :param electricity_data: rates and consumption electricity data
    """
    for unit_rate in electricity_data.unit_rate:
        DB_CONNECTOR.upsert_db(table=ElectricityRatesTable, data=unit_rate)
        time.sleep(1)
    for consumption_unit in electricity_data.consumption:
        DB_CONNECTOR.upsert_db(
            table=ElectricityConsumptionTable,
            data=consumption_unit,
        )
        time.sleep(1)


@task(name="Get Weekly Electricity Data")
def get_weekly_electricity_consumption_data(
    group_by="week", period_from="2023-01-01", period_to="2023-12-31"
):
    """Get Octopus weekly electricity data."""
    electricity_data_extractor = ElectricityDataExtractor()
    electricity_data = electricity_data_extractor.get_electricity_data(
        rates_url=URL_GENERATOR.get_electricity_rates_url(),
        consumption_url=URL_GENERATOR.get_electricity_consumption_url(
            group_by, period_from, period_to
        ),
        api_key=CONFIG.octopus_api_key.get_secret_value(),
        group_by=group_by,
    )
    return electricity_data


@task(name="Add Weekly Electricity Data to Db")
def add_weekly_electricity_consumption_data(electricity_data: ElectricityData):
    """Process Octopus electricity weekly consumption data.

    :param electricity_data: rates and consumption electricity data
    """
    for consumption_unit in electricity_data.consumption:
        DB_CONNECTOR.upsert_db(
            table=ElectricityWeeklyConsumptionTable2023,
            data=consumption_unit,
        )
        time.sleep(1)


@task(name="Get Octopus Gas Data")
def get_octopus_gas_data() -> GasData:
    """Get Octopus gas data."""
    gas_data_extractor = GasDataExtractor()
    gas_data = gas_data_extractor.get_gas_data(
        rates_url=URL_GENERATOR.get_gas_rates_url(),
        consumption_url=URL_GENERATOR.get_gas_consumption_url(),
        api_key=CONFIG.octopus_api_key.get_secret_value(),
        gas_m3_to_kwh_conversion=CONFIG.gas_m3_to_kwh_conversion,
    )
    return gas_data


@task(name="Add Octopus Gas Data to Db")
def add_octopus_gas_data_to_db(gas_data: GasData) -> None:
    """Process Octopus gas data.

    :param gas_data: rates and consumption gas data
    """
    for unit_rate in gas_data.unit_rate:
        DB_CONNECTOR.upsert_db(table=GasRatesTable, data=unit_rate)
        time.sleep(1)
    for consumption_unit in gas_data.consumption:
        DB_CONNECTOR.upsert_db(
            table=GasConsumptionTable,
            data=consumption_unit,
        )
        time.sleep(1)


@flow(name="Process Octopus Data")
def process_octopus_data():
    """Process Octopus Electricity Data."""
    LOGGER.info("Extracting Electricity Data.")
    electricity_data = get_octopus_electricity_data()

    LOGGER.info("Adding Electricity Data to DB.")
    electricity_data_to_db = add_octopus_electricity_data_to_db(electricity_data)

    time.sleep(5)

    LOGGER.info("Extracting Gas Data.")
    gas_data = get_octopus_gas_data()

    LOGGER.info("Adding Gas Data to DB.")
    gas_data_to_db = add_octopus_gas_data_to_db(gas_data)

    time.sleep(5)

    LOGGER.info("Extracting Electricity Weekly Consumption.")
    weekly_electricity_consumption_data = get_weekly_electricity_consumption_data()

    LOGGER.info("Adding Electricity Weekly Consumption Data to Db.")
    weekly_electricity_consumption_data_to_db = add_weekly_electricity_consumption_data(
        weekly_electricity_consumption_data
    )


if __name__ == "__main__":
    from database.db_models import Base

    # process_electricity_data()
    # process_octopus_gas_data()
    # properties = get_account_info()
    # for property in properties:
    #     print(f"{property}")
    process_octopus_data.serve(name="Process Ocotpus Data", interval=3600)
    # data = get_weekly_electricity_consumption_data()
    # add_weekly_electricity_consumption_data(data)
