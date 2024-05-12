"""Database connector module."""

import logging
from datetime import date
from typing import Literal

import pandas as pd
from dateutil.parser import parse
from sqlalchemy import create_engine, desc, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from energy_analyzer.database.db_models import Base, OctopusTables


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

    def get_latest_row(
        self, table: OctopusTables, column_name: str = "date"
    ) -> date | None:
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
            try:
                result = session.execute(stmt)
                session.commit()
                output: date = result.scalar_one()
                return parse(output.strftime("%Y-%m-%d"))
            except NoResultFound:
                return None

    def reset_database(self, table: OctopusTables) -> None:
        """Reset Database."""
        Base.metadata.drop_all(bind=db_connector.engine, tables=[table.db_table()])
        Base.metadata.create_all(bind=db_connector.engine, tables=[table.db_table()])


if __name__ == "__main__":
    from energy_analyzer.database.db_models import (
        GasWeeklyConsumptionTable2023,
    )
    from energy_analyzer.utils.config import ProjectConfig

    config = ProjectConfig()

    db_url = config.db_url
    db_connector = DbConnector(db_url.get_secret_value())

    db_connector.reset_database(table=GasWeeklyConsumptionTable2023)
