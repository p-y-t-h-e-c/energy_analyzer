"""Main module."""
import requests
from prefect import flow, task

from config import ProjectConfig, UrlGenerator
from data_models import ElectricityData, EnergyType, GasData
from database.db_connector import DbConnector
from database.db_models import (
    ElectricityConsumptionTable,
    ElectricityRatesTable,
    GasConsumptionTable,
    GasRatesTable,
)
from octopus_data.data_extract import ElectricityDataExtractor, GasDataExtractor

CONFIG = ProjectConfig()
URL_GENERATOR = UrlGenerator()
DB_CONNECTOR = DbConnector(CONFIG.db_url.get_secret_value())


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

    for consumption_unit in electricity_data.consumption:
        DB_CONNECTOR.upsert_db(
            table=ElectricityConsumptionTable,
            data=consumption_unit,
        )


@task(name="Get Octopus Gas Data")
def get_octopus_gas_data() -> GasData:
    """Get Octopus gas data."""
    pass


@flow(name="Process Octopus Data")
def process_octopus_electricity_data():
    """Process Octopus Electricity Data."""
    electricity_data = get_octopus_electricity_data()
    print(electricity_data.unit_rate)
    add_octopus_electricity_data_to_db(electricity_data)


def process_electricity_data() -> None:
    """Process Octopus electricity data from REST API into Neon database."""
    electricity_data_extractor = ElectricityDataExtractor()
    electricity_data = electricity_data_extractor.get_electricity_data(
        rates_url=URL_GENERATOR.get_electricity_rates_url(),
        consumption_url=URL_GENERATOR.get_electricity_consumption_url(),
        api_key=CONFIG.octopus_api_key.get_secret_value(),
    )

    for unit_rate in electricity_data.unit_rate:
        DB_CONNECTOR.upsert_db(table=ElectricityRatesTable, data=unit_rate)

    for consumption_unit in electricity_data.consumption:
        DB_CONNECTOR.upsert_db(
            table=ElectricityConsumptionTable,
            data=consumption_unit,
        )


def process_octopus_gas_data() -> None:
    """Process Octopus gas data from REST API into Neon database."""
    gas_data_extractor = GasDataExtractor()
    gas_data = gas_data_extractor.get_gas_data(
        rates_url=URL_GENERATOR.get_gas_rates_url(),
        consumption_url=URL_GENERATOR.get_gas_consumption_url(),
        api_key=CONFIG.octopus_api_key.get_secret_value(),
        gas_m3_to_kwh_conversion=CONFIG.gas_m3_to_kwh_conversion,
    )

    for unit_rate in gas_data.unit_rate:
        DB_CONNECTOR.upsert_db(table=GasRatesTable, data=unit_rate)

    for consumption_unit in gas_data.consumption:
        DB_CONNECTOR.upsert_db(
            table=GasConsumptionTable,
            data=consumption_unit,
        )


if __name__ == "__main__":
    from database.db_models import Base

    # process_electricity_data()
    # process_octopus_gas_data()
    # properties = get_account_info()
    # for property in properties:
    #     print(f"{property}")
    process_octopus_electricity_data.serve(name="Process Ocotpus Data")
