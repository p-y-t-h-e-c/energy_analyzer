"""Data processing module."""
from config import ProjectConfig, get_consumption_url, get_rates_url
from data_models import EnergyType
from database.db_connector import DbConnector
from database.db_models import (
    ElectricityConsumptionTable,
    ElectricityRatesTable,
    GasConsumptionTable,
    GasRatesTable,
)
from octopus_data.data_extract import get_consumption_values, get_standard_unit_rates


def process_data(
    energy_type: EnergyType, config: ProjectConfig, db_connector: DbConnector
):
    """Process electricity and gas data from Octopus into Neon database."""
    match energy_type:
        case EnergyType.ELECTRICITY:
            electricity_unit_rates = get_standard_unit_rates(get_rates_url(energy_type))
            for unit_rate in electricity_unit_rates:
                db_connector.add_data_to_db(
                    ref_table=ElectricityRatesTable.db_table(), data=unit_rate
                )
            electricity_consumption_values = get_consumption_values(
                get_consumption_url(energy_type),
                config.octopus_api_key.get_secret_value(),
            )
            for consumption_unit in electricity_consumption_values:
                db_connector.add_data_to_db(
                    ref_table=ElectricityConsumptionTable.db_table(),
                    data=consumption_unit,
                )
        case EnergyType.GAS:
            gas_unit_rates = get_standard_unit_rates(get_rates_url(energy_type))
            for unit_rate in gas_unit_rates:
                db_connector.add_data_to_db(
                    ref_table=GasRatesTable.db_table(), data=unit_rate
                )
            gas_consumption_values = get_consumption_values(
                get_consumption_url(energy_type),
                config.octopus_api_key.get_secret_value(),
                config.gas_m3_to_kwh_conversion,
            )
            for consumption_unit in gas_consumption_values:
                db_connector.add_data_to_db(
                    ref_table=GasConsumptionTable.db_table(),
                    data=consumption_unit,
                )


if __name__ == "__main__":
    pass
