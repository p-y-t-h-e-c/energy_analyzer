"""Energy rates analyzer."""

from typing import Any, List

import pandas as pd


class EnergyAnalyzer:
    """Energy Analyzer class."""

    def __init__(self, data: List[dict[str, Any]]) -> None:
        """Class initiator method."""
        self.data = data

    def energy_data_to_df(self) -> pd.DataFrame:
        """Transform energy data into DataFrame."""
        df = pd.DataFrame(self.data)
        print(df)
        return df

    def get_last_value(self) -> float:
        """Get the energy last value."""
        df = self.energy_data_to_df()
        last_value = df["unit_rate_inc_vat"].iloc[-1:].values[0]
        return last_value

    def get_next_to_last_value(self) -> float:
        """Get the energy next to last value."""
        df = self.energy_data_to_df()
        next_to_last_value = df["unit_rate_inc_vat"].iloc[-2:-1].values[0]
        return next_to_last_value

    def get_energy_rates_value_analysis(self) -> float:
        """Analyze rates value fluctuation."""
        value_analysis = self.get_last_value() - self.get_next_to_last_value()
        return value_analysis

    def energy_rates_percentage_analysis(self):
        """Analyze rates percentage fluctuation."""
        percentage_analysis = (
            self.get_energy_rates_value_analysis() / self.get_next_to_last_value() * 100
        )
        return percentage_analysis


# ("{:.4f}".format(value_analysis), "{:.1f}".format(percentage_analysis) + "%")

if __name__ == "__main__":
    from data_extract import DataExtractor

    from energy_analyzer.octopus_data.url_generator import UrlGenerator
    from energy_analyzer.utils.config import ProjectConfig

    config = ProjectConfig()
    url_generator = UrlGenerator()

    data_extractor = DataExtractor()

    electricity_unit_rates_data = data_extractor.get_standard_unit_rates(
        rates_url=url_generator.get_electricity_rates_url()
    )
    electricity_consumption_data = data_extractor.get_consumption_values(
        consumption_url=url_generator.get_electricity_consumption_url(),
        api_key=config.octopus_api_key.get_secret_value(),
    )

    # print(electricity_data.unit_rate)
    energy_analyzer = EnergyAnalyzer(electricity_unit_rates_data)
    print(type(energy_analyzer.get_last_value()))
    print(energy_analyzer.energy_rates_percentage_analysis())
