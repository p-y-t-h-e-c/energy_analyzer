"""Main module."""
import requests

from config import ProjectConfig
from data_models import EnergyType
from database.db_connector import DbConnector
from octopus_data.data_process import process_data

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


def process_octopus_data():
    """Process Octopus data."""
    for energy_type in EnergyType:
        process_data(energy_type=energy_type, config=CONFIG, db_connector=DB_CONNECTOR)


if __name__ == "__main__":
    # for energy_type in EnergyType:
    #     print(energy_type)
    process_octopus_data()
