"""Main module."""
import requests

from config import ProjectConfig, get_consumption_url, get_rates_url
from data_models import EnergyType
from database.db_connector import DbConnector
from database.db_models import (
    ElectricityConsumptionTable,
    ElectricityRatesTable,
    GasConsumptionTable,
    GasRatesTable,
)
from octopus_data.data_extract import ElectricityDataExtractor, GasDataExtractor

CONFIG = ProjectConfig()
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
    return output_dict


def process_octopus_electricity_data() -> None:
    """Process Octopus electricity data from REST API into Neon database."""
    electricity_data_extractor = ElectricityDataExtractor()
    electricity_data = electricity_data_extractor.get_electricity_data(
        rates_url=get_rates_url(energy_type=EnergyType.ELECTRICITY),
        consumption_url=get_consumption_url(energy_type=EnergyType.ELECTRICITY),
        api_key=CONFIG.octopus_api_key.get_secret_value(),
    )

    for unit_rate in electricity_data.unit_rate:
        DB_CONNECTOR.add_data_to_db(ref_table=ElectricityRatesTable, data=unit_rate)

    for consumption_unit in electricity_data.consumption:
        DB_CONNECTOR.add_data_to_db(
            ref_table=ElectricityConsumptionTable,
            data=consumption_unit,
        )


def process_octopus_gas_data() -> None:
    """Process Octopus gas data from REST API into Neon database."""
    gas_data_extractor = GasDataExtractor()
    gas_data = gas_data_extractor.get_gas_data(
        rates_url=get_rates_url(energy_type=EnergyType.GAS),
        consumption_url=get_consumption_url(energy_type=EnergyType.GAS),
        api_key=CONFIG.octopus_api_key.get_secret_value(),
    )

    for unit_rate in gas_data.unit_rate:
        DB_CONNECTOR.add_data_to_db(ref_table=GasRatesTable, data=unit_rate)

    for consumption_unit in gas_data.consumption:
        DB_CONNECTOR.add_data_to_db(
            ref_table=GasConsumptionTable,
            data=consumption_unit,
        )


if __name__ == "__main__":
    from database.db_models import Base

    process_octopus_electricity_data()
    process_octopus_gas_data()
