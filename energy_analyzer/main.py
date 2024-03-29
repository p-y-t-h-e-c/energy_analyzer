"""Main module."""

import pandas as pd
from dagster import asset, get_dagster_logger

from energy_analyzer.database.db_connector import DbConnector
from energy_analyzer.database.db_models import (
    ElectricityConsumptionTable,
    ElectricityRatesTable,
    ElectricityWeeklyConsumptionTable2024,
    GasConsumptionTable,
    GasRatesTable,
    GasWeeklyConsumptionTable2024,
)
from energy_analyzer.octopus_data.data_extract import DataExtractor
from energy_analyzer.octopus_data.data_handler import (
    DailyDataHandler,
    WeeklyDataHandler,
)
from energy_analyzer.octopus_data.url_generator import UrlGenerator
from energy_analyzer.utils.config import ProjectConfig

CONFIG = ProjectConfig()
URL_GENERATOR = UrlGenerator()
DB_CONNECTOR = DbConnector(CONFIG.db_url.get_secret_value())
LOGGER = get_dagster_logger()


@asset(name="Get_Octopus_Electricity_Rates_Data")
def get_electricity_rates_data() -> pd.DataFrame:
    """Get Octopus electricity data."""
    LOGGER.info("Extracting electricity rates data.")
    data_extractor = DataExtractor()

    electricity_raw = data_extractor.get_standard_unit_rates(
        rates_url=URL_GENERATOR.get_electricity_rates_url()
    )

    daily_data_handler = DailyDataHandler()

    electricity_rates_df = daily_data_handler.parse_data_to_df(electricity_raw)

    electricity_rates_formatted = daily_data_handler.format_standard_unit_rates_data(
        electricity_rates_df
    )

    update_point = DB_CONNECTOR.get_latest_row(ElectricityRatesTable)
    data_to_add_to_db = daily_data_handler.select_data_to_add_to_db(
        electricity_rates_formatted, update_point
    )

    return data_to_add_to_db


@asset(name="Add_Octopus_Electricity_Rates_Data_to_Database")
def add_electricity_rates_data_to_db(
    Get_Octopus_Electricity_Rates_Data: pd.DataFrame,
) -> None:
    """Add Octopus electricity rates data to database.

    Args:
        data: electricity standard unit rates data in the form of DataFrame
    """
    LOGGER.info("Adding electricity rates data to database.")
    DB_CONNECTOR.add_data_to_db(
        Get_Octopus_Electricity_Rates_Data,
        table_name=ElectricityRatesTable.__tablename__,
    )


@asset(name="Get_Octopus_Gas_Rates_Data", deps=[add_electricity_rates_data_to_db])
def get_gas_rates_data() -> pd.DataFrame:
    """Get Octopus standard unit rates data."""
    data_extractor = DataExtractor()

    gas_raw = data_extractor.get_standard_unit_rates(
        rates_url=URL_GENERATOR.get_gas_rates_url()
    )

    daily_data_handler = DailyDataHandler()

    gas_rates_df = daily_data_handler.parse_data_to_df(gas_raw)

    gas_rates_formatted = daily_data_handler.format_standard_unit_rates_data(
        gas_rates_df
    )

    update_point = DB_CONNECTOR.get_latest_row(GasRatesTable)
    data_to_add_to_db = daily_data_handler.select_data_to_add_to_db(
        gas_rates_formatted, update_point
    )

    return data_to_add_to_db


@asset(name="Add_Octopus_Gas_Rates_Data_to_Database")
def add_gas_rates_data_to_db(Get_Octopus_Gas_Rates_Data: pd.DataFrame) -> None:
    """Add Octopus gas rates data to database.

    Args:
        data: gas standard unit rates data in the form of DataFrame
    """
    DB_CONNECTOR.add_data_to_db(
        Get_Octopus_Gas_Rates_Data, table_name=GasRatesTable.__tablename__
    )


@asset(
    name="Get_Octopus_Electricity_Daily_Consumption_Data",
    deps=[add_gas_rates_data_to_db],
)
def get_electricity_consumption_data() -> pd.DataFrame:
    """Get Octopus electricity consumption data."""
    data_extractor = DataExtractor()

    electricity_consumption_raw = data_extractor.get_consumption_values(
        consumption_url=URL_GENERATOR.get_electricity_consumption_url(year_from="2022"),
        api_key=CONFIG.octopus_api_key.get_secret_value(),
    )

    daily_data_handler = DailyDataHandler()

    electricity_consumption_df = daily_data_handler.parse_data_to_df(
        electricity_consumption_raw
    )

    electricity_consumption_formatted = daily_data_handler.format_consumption_data(
        electricity_consumption_df
    )

    update_point = DB_CONNECTOR.get_latest_row(ElectricityConsumptionTable)
    data_to_add_to_db = daily_data_handler.select_data_to_add_to_db(
        electricity_consumption_formatted, update_point
    )

    return data_to_add_to_db


@asset(name="Add_Octopus_Electricity_Consumption_Data_to_Database")
def add_electricity_consumption_data_to_db(
    Get_Octopus_Electricity_Daily_Consumption_Data: pd.DataFrame,
) -> None:
    """Add Octopus electricity consumption data to database.

    Args:
        data: electricity consumption data in the form of DataFrame
    """
    DB_CONNECTOR.add_data_to_db(
        Get_Octopus_Electricity_Daily_Consumption_Data,
        table_name=ElectricityConsumptionTable.__tablename__,
    )


@asset(
    name="Get_Octopus_Gas_Daily_Consumption_Data",
    deps=[add_electricity_consumption_data_to_db],
)
def get_gas_consumption_data() -> pd.DataFrame:
    """Get Octopus gas consumption data."""
    data_extractor = DataExtractor()

    gas_consumption_raw = data_extractor.get_consumption_values(
        consumption_url=URL_GENERATOR.get_gas_consumption_url(year_from="2022"),
        api_key=CONFIG.octopus_api_key.get_secret_value(),
    )

    daily_data_handler = DailyDataHandler()

    gas_consumption_df = daily_data_handler.parse_data_to_df(gas_consumption_raw)

    gas_consumption_formatted = daily_data_handler.format_consumption_data(
        gas_consumption_df, CONFIG.gas_m3_to_kwh_conversion
    )

    update_point = DB_CONNECTOR.get_latest_row(GasConsumptionTable)
    data_to_add_to_db = daily_data_handler.select_data_to_add_to_db(
        gas_consumption_formatted, update_point
    )

    return data_to_add_to_db


@asset(name="Add_Octopus_Gas_Consumption_Data_to_Database")
def add_gas_consumption_data_to_db(
    Get_Octopus_Gas_Daily_Consumption_Data: pd.DataFrame,
) -> None:
    """Add Octopus gas consumption data to database.

    Args:
        data: gas daily consumption data in the form of DataFrame
    """
    DB_CONNECTOR.add_data_to_db(
        Get_Octopus_Gas_Daily_Consumption_Data,
        table_name=GasConsumptionTable.__tablename__,
    )


@asset(
    name="Get_Octopus_Electricity_Weekly_Consumption_Data",
    deps=[add_gas_consumption_data_to_db],
)
def get_electricity_weekly_consumption_data() -> pd.DataFrame:
    """Get Octopus electricity weekly consumption data."""
    data_extractor = DataExtractor()

    electricity_consumption_weekly_raw = data_extractor.get_consumption_values(
        consumption_url=URL_GENERATOR.get_electricity_consumption_url(
            group_by="week", year_from="2024", year_to=2024
        ),
        api_key=CONFIG.octopus_api_key.get_secret_value(),
    )

    weekly_data_handler = WeeklyDataHandler()
    electricity_consumption_weekly_df = weekly_data_handler.parse_data_to_df(
        electricity_consumption_weekly_raw
    )
    electricity_consumption_weekly_formatted = (
        weekly_data_handler.format_weekly_consumption_data(
            electricity_consumption_weekly_df
        )
    )

    return electricity_consumption_weekly_formatted


@asset(name="Add_Octopus_Electricity_Weekly_Consumption_Data_to_Database")
def add_electricity_weekly_consumption_data_to_db(
    Get_Octopus_Electricity_Weekly_Consumption_Data: pd.DataFrame,
) -> None:
    """Add Octopus electricity weekly consumption data to database.

    Args:
        data: electricity weekly consumption data in the form of DataFrame
    """
    DB_CONNECTOR.add_data_to_db(
        Get_Octopus_Electricity_Weekly_Consumption_Data,
        table_name=ElectricityWeeklyConsumptionTable2024.__tablename__,
        if_exists="replace",
    )


@asset(
    name="Get_Octopus_Gas_Weekly_Consumption_Data",
    deps=[add_electricity_weekly_consumption_data_to_db],
)
def get_gas_weekly_consumption_data() -> pd.DataFrame:
    """Get Octopus gas weekly consumption data."""
    data_extractor = DataExtractor()

    gas_consumption_weekly_raw = data_extractor.get_consumption_values(
        consumption_url=URL_GENERATOR.get_gas_consumption_url(
            group_by="week", year_from="2024", year_to=2024
        ),
        api_key=CONFIG.octopus_api_key.get_secret_value(),
    )

    weekly_data_handler = WeeklyDataHandler()
    gas_consumption_weekly_df = weekly_data_handler.parse_data_to_df(
        gas_consumption_weekly_raw
    )
    gas_consumption_weekly_formatted = (
        weekly_data_handler.format_weekly_consumption_data(gas_consumption_weekly_df)
    )

    return gas_consumption_weekly_formatted


@asset(name="Add_Octopus_Gas_Weekly_Consumption_Data_to_Database")
def add_gas_weekly_consumption_data_to_db(
    Get_Octopus_Gas_Weekly_Consumption_Data: pd.DataFrame,
) -> None:
    """Add Octopus gas weekly consumption data to database.

    Args:
        data: gas weekly consumption data in the form of DataFrame
    """
    DB_CONNECTOR.add_data_to_db(
        Get_Octopus_Gas_Weekly_Consumption_Data,
        table_name=GasWeeklyConsumptionTable2024.__tablename__,
        if_exists="replace",
    )
