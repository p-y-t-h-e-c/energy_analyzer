"""Module to test endpoints."""

from energy_analyzer.utils.config import ProjectConfig

CONFIG = ProjectConfig()

import requests

if __name__ == "__main__":
    # url = "https://api.octopus.energy/v1/products"
    # r = requests.get(url, auth=(CONFIG.octopus_api_key.get_secret_value(), ""))
    # output_dict = r.json()
    # print(output_dict)

    def get_account_info():
        """Get Octopus account info."""
        url = (
            "https://api.octopus.energy/v1/accounts/"
            + CONFIG.account.get_secret_value()
        )
        r = requests.get(url, auth=(CONFIG.octopus_api_key.get_secret_value(), ""))
        output_dict = r.json()
        return output_dict["properties"]


print(get_account_info())
