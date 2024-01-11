"""Energy rates analyzer."""
import numpy as np
import pandas as pd

from data_models import ElectricityData, GasData


class EnergyAnalyzer:
    """Energy Analyzer class."""

    def __init__(self, energy_data: ElectricityData | GasData) -> None:
        """Class initiator method."""
        self.energy_data = energy_data

    def energy_data_to_df(self) -> pd.DataFrame:
        """Transform energy data into DataFrame."""
        df = pd.DataFrame(self.energy_data.unit_rate)
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
    from config import ProjectConfig, UrlGenerator
    from octopus_data.data_extract import ElectricityDataExtractor

    config = ProjectConfig()
    url_generator = UrlGenerator()

    electricity_data_extractor = ElectricityDataExtractor()
    electricity_data = electricity_data_extractor.get_electricity_data(
        rates_url=url_generator.get_electricity_rates_url(),
        consumption_url=url_generator.get_electricity_consumption_url(),
        api_key=config.octopus_api_key.get_secret_value(),
    )

    # print(electricity_data.unit_rate)
    energy_analyzer = EnergyAnalyzer(electricity_data)
    print(type(energy_analyzer.get_last_value()))
    print(energy_analyzer.energy_rates_percentage_analysis())
