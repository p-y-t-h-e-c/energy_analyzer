"""Database connector module."""
import logging
from datetime import date
from typing import Literal

import pandas as pd
from sqlalchemy import create_engine, desc, select
from sqlalchemy.orm import Session

from energy_analyzer.database.db_models import OctopusTables


class DbConnector:
    """Database connector."""

    def __init__(self, database_url: str, echo: bool = False):
        """Class constructor method."""
        self.engine = create_engine(
            database_url,
            echo=echo,
        )
        self.session = Session(self.engine)

    def add_data_to_db(
        self,
        data: pd.DataFrame,
        table_name: str,
        if_exists: Literal["fail", "replace", "append"] = "append",
    ) -> None:
        """Add data in DataFrame form to respective database table.

        Args:
            data: new data to be added to db table
            table_name: name of the table to which data to be added

        Returns:
            nothing: adds data to database table
        """
        if not data.empty:
            data.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
        else:
            logging.info("No new data to be added to db.")

    def get_latest_row(self, table: OctopusTables, column_name: str = "date") -> date:
        """Get latest row from a specific column.

        Args:
            table: a selected table to get the data from
            column_name: a name of the column from which the last row to be retrieved

        Returns:
            the latest record of specified table, column
        """
        with self.session as session:
            table_column = table.db_table().columns.__getattr__(column_name)
            stmt = select(table_column).order_by(desc(table_column)).limit(1)
            result = session.execute(stmt)
            session.commit()
            return result.scalar_one()

    def reset_database(self) -> None:
        """Reset Database."""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)


if __name__ == "__main__":
    from database.db_models import (
        Base,
        ElectricityRatesTable,
        ElectricityWeeklyConsumptionTable2024,
    )

    from energy_analyzer.utils.config import ProjectConfig

    config = ProjectConfig()

    data = {
        "date": "2023-11-21",
        "unit_rate_exc_vat": 1800,
        "unit_rate_inc_vat": 19.341,
    }
    db_url = config.db_url
    db_connector = DbConnector(db_url.get_secret_value())

    # print(db_connector.get_latest_date(ElectricityWeeklyConsumptionTable2022))

    # db_connector.reset_database()

    print(db_connector.get_latest_row(ElectricityRatesTable))
    print(
        db_connector.get_latest_row(
            ElectricityWeeklyConsumptionTable2024, column_name="week"
        )
    )
