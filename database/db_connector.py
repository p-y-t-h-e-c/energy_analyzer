"""Database connector module."""
import datetime
from datetime import date
from typing import Any

import pandas as pd
from prefect import logging
from sqlalchemy import create_engine, desc, select
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.db_models import OctopusTables


class DbConnector:
    """Database connector."""

    def __init__(self, database_url: str, echo: bool = False):
        """Class constructor method."""
        self.engine = create_engine(
            database_url,
            echo=echo,
        )
        self.session = Session(self.engine)

    def add_data_to_db(self, data: pd.DataFrame, table_name: str) -> None:
        """Add data in DataFrame form to respective database table.

        Args:
            data: new data to be added to db table
            table_name: name of the table to which data to be added

        Returns:
            nothing: adds data to database table
        """
        if not data.empty:
            data.to_sql(table_name, self.engine, if_exists="replace", index=False)
        else:
            logging.get_logger().info("No new data to be added to db.")

    def get_latest_date(self, table: OctopusTables) -> date:
        """Get latest date from a table.

        :param table: a selected table to get the latest date from

        :return: the latest date from a table
        """
        with self.session as session:
            if table.db_table().primary_key.columns.values()[0].name == "date":
                table_column = table.db_table().columns.__getattr__("date")
                stmt = select(table_column).order_by(desc(table_column)).limit(1)
                result = session.execute(stmt)
                session.commit()
                return result.scalar_one()
            else:
                current_year = datetime.date.today().year
                from_date = f"{current_year}-01-01"
                datetime_object = datetime.datetime.strptime(
                    from_date, "%Y-%m-%d"
                ).date()
                return datetime_object

    def reset_database(self) -> None:
        """Reset Database."""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)


if __name__ == "__main__":
    from config import ProjectConfig
    from database.db_models import (
        Base,
        ElectricityRatesTable,
        ElectricityWeeklyConsumptionTable2022,
    )

    config = ProjectConfig()

    data = {
        "date": "2023-11-21",
        "unit_rate_exc_vat": 1800,
        "unit_rate_inc_vat": 19.341,
    }
    db_url = config.db_url
    db_connector = DbConnector(db_url.get_secret_value())

    # print(db_connector.get_latest_date(ElectricityWeeklyConsumptionTable2022))

    db_connector.reset_database()

    # db_connector.upsert_db(ElectricityRatesTable, data)
