"""Main module."""
import time

import pandas as pd
import requests
from prefect import flow, logging, task

from config import ProjectConfig, UrlGenerator
from database.db_connector import DbConnector
from database.db_models import (
    ElectricityConsumptionTable,
    ElectricityRatesTable,
    ElectricityWeeklyConsumptionTable2022,
    ElectricityWeeklyConsumptionTable2023,
    ElectricityWeeklyConsumptionTable2024,
    GasConsumptionTable,
    GasRatesTable,
    GasWeeklyConsumptionTable2022,
    GasWeeklyConsumptionTable2023,
    GasWeeklyConsumptionTable2024,
)
from octopus_data.data_extract import DataExtractor
from octopus_data.data_handler import DailyDataHandler, WeeklyDataHandler

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


@task(name="Get Octopus electricity rates data")
def get_electricity_rates_data() -> pd.DataFrame:
    """Get Octopus electricity data."""
    data_extractor = DataExtractor()

    electricity_raw = data_extractor.get_standard_unit_rates(
        url=URL_GENERATOR.get_electricity_rates_url(period_from="2022")
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


@task(name="Add Octopus electricity rates data to database")
def add_electricity_rates_data_to_db(data: pd.DataFrame) -> None:
    """Add Octopus electricity rates data to database.

    Args:
        data: electricity standard unit rates data in the form of DataFrame
    """
    DB_CONNECTOR.add_data_to_db(data, table_name=ElectricityRatesTable.__tablename__)


@task(name="Get Octopus gas rates data")
def get_gas_rates_data() -> pd.DataFrame:
    """Get Octopus standard unit rates data."""
    data_extractor = DataExtractor()

    gas_raw = data_extractor.get_standard_unit_rates(
        url=URL_GENERATOR.get_gas_rates_url(period_from="2022")
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


@task(name="Add Octopus gas rates data to database")
def add_gas_rates_data_to_db(data: pd.DataFrame) -> None:
    """Add Octopus gas rates data to database.

    Args:
        data: gas standard unit rates data in the form of DataFrame
    """
    DB_CONNECTOR.add_data_to_db(data, table_name=GasRatesTable.__tablename__)


@task(name="Get Octopus electricity daily consumption data")
def get_electricity_consumption_data() -> pd.DataFrame:
    """Get Octopus electricity consumption data."""
    data_extractor = DataExtractor()

    electricity_consumption_raw = data_extractor.get_consumption_values(
        url=URL_GENERATOR.get_electricity_consumption_url(period_from="2022"),
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


@task(name="Add Octopus electricity consumption data to database")
def add_electricity_consumption_data_to_db(data: pd.DataFrame) -> None:
    """Add Octopus electricity consumption data to database.

    Args:
        data: electricity consumption data in the form of DataFrame
    """
    DB_CONNECTOR.add_data_to_db(
        data, table_name=ElectricityConsumptionTable.__tablename__
    )


@task(name="Get Octopus gas daily consumption data")
def get_gas_consumption_data() -> pd.DataFrame:
    """Get Octopus gas consumption data."""
    data_extractor = DataExtractor()

    gas_consumption_raw = data_extractor.get_consumption_values(
        url=URL_GENERATOR.get_gas_consumption_url(period_from="2022"),
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


@task(name="Add Octopus gas consumption data to database")
def add_gas_consumption_data_to_db(data: pd.DataFrame) -> None:
    """Add Octopus gas consumption data to database.

    Args:
        data: gas daily consumption data in the form of DataFrame
    """
    DB_CONNECTOR.add_data_to_db(data, table_name=GasConsumptionTable.__tablename__)


@task(name="Get Octopus electricity weekly consumption data")
def get_electricity_weekly_consumption_data() -> pd.DataFrame:
    """Get Octopus electricity weekly consumption data."""
    data_extractor = DataExtractor()

    electricity_consumption_weekly_raw = data_extractor.get_consumption_values(
        url=URL_GENERATOR.get_electricity_consumption_url(
            group_by="week", period_from="2024", period_to="2024"
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

    update_point = DB_CONNECTOR.get_latest_row(
        ElectricityWeeklyConsumptionTable2024, column_name="week"
    )
    data_to_add_to_db = weekly_data_handler.select_data_to_add_to_db(
        electricity_consumption_weekly_formatted, update_point
    )

    return data_to_add_to_db


@task(name="Add Octopus electricity weekly consumption data to database")
def add_electricity_weekly_consumption_data_to_db(data: pd.DataFrame) -> None:
    """Add Octopus electricity weekly consumption data to database.

    Args:
        data: electricity weekly consumption data in the form of DataFrame
    """
    DB_CONNECTOR.add_data_to_db(
        data, table_name=ElectricityWeeklyConsumptionTable2024.__tablename__
    )


@task(name="Get Octopus gas weekly consumption data")
def get_gas_weekly_consumption_data() -> pd.DataFrame:
    """Get Octopus gas weekly consumption data."""
    data_extractor = DataExtractor()

    gas_consumption_weekly_raw = data_extractor.get_consumption_values(
        url=URL_GENERATOR.get_gas_consumption_url(
            group_by="week", period_from="2024", period_to="2024"
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

    update_point = DB_CONNECTOR.get_latest_row(
        GasWeeklyConsumptionTable2024, column_name="week"
    )
    data_to_add_to_db = weekly_data_handler.select_data_to_add_to_db(
        gas_consumption_weekly_formatted, update_point
    )

    return data_to_add_to_db


@task(name="Add Octopus gas weekly consumption data to database")
def add_gas_weekly_consumption_data_to_db(data: pd.DataFrame) -> None:
    """Add Octopus gas weekly consumption data to database.

    Args:
        data: gas weekly consumption data in the form of DataFrame
    """
    DB_CONNECTOR.add_data_to_db(
        data, table_name=GasWeeklyConsumptionTable2024.__tablename__
    )


@flow(name="Process Octopus Data")
def process_octopus_data():
    """Process Octopus Data from API to database."""
    LOGGER.info("Extracting electricity rates data.")
    electricity_rates_data = get_electricity_rates_data()

    LOGGER.info("Adding electricity rates data to DB.")
    electricity_rates_data_to_db = add_electricity_rates_data_to_db(
        electricity_rates_data
    )

    time.sleep(1)

    LOGGER.info("Extracting gas rates data.")
    gas_rates_data = get_gas_rates_data()

    LOGGER.info("Adding gas rates data to DB.")
    gas_rates_data_to_db = add_gas_rates_data_to_db(gas_rates_data)

    time.sleep(1)

    LOGGER.info("Extracting electricity consumption data.")
    electricity_consumption_data = get_electricity_consumption_data()

    LOGGER.info("Adding electricity consumption data to DB.")
    electricity_consumption_data_to_db = add_electricity_consumption_data_to_db(
        electricity_consumption_data
    )

    time.sleep(1)

    LOGGER.info("Extracting gas consumption data.")
    gas_consumption_data = get_gas_consumption_data()

    LOGGER.info("Adding gas consumption data to DB.")
    gas_consumption_data_to_db = add_gas_consumption_data_to_db(gas_consumption_data)

    time.sleep(1)

    LOGGER.info("Extracting electricity weekly consumption data.")
    electricity_weekly_consumption_data = get_electricity_weekly_consumption_data()

    LOGGER.info("Adding electricity weekly consumption data to DB.")
    electricity_consumption_weekly_data_to_db = (
        add_electricity_weekly_consumption_data_to_db(
            electricity_weekly_consumption_data
        )
    )

    time.sleep(1)

    LOGGER.info("Extracting gas weekly consumption data.")
    gas_weekly_consumption_data = get_gas_weekly_consumption_data()

    LOGGER.info("Adding gas weekly consumption data to DB.")
    gas_consumption_weekly_data_to_db = add_gas_weekly_consumption_data_to_db(
        gas_weekly_consumption_data
    )


if __name__ == "__main__":
    process_octopus_data.serve(name="Process Octopus Data", cron="35 * * * *")
