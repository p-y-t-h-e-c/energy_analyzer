"""Database connector module."""
import datetime
import logging
from datetime import date
from typing import Any

import sqlalchemy as sa
from sqlalchemy import create_engine, desc, select
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.db_models import OctopusTables


class DbConnector:
    """Database connector."""

    def __init__(self, database_url: str, echo: bool = False):
        """Class constructor method."""
        self._engine = create_engine(
            database_url,
            echo=echo,
        )
        self.session = Session(self._engine)

    def upsert_db(self, table: OctopusTables, data: dict[str, Any]) -> None:
        """Add or update data to/in database.

        :param table: selected db table
        :param data: a row of data in dict format to be added te a table

        :return: Nothing, add or update record to/in db
        """
        with self.session as session:
            stmt = upsert(table).values(data)
            do_update_stmt = stmt.on_conflict_do_update(
                constraint=table.db_table().primary_key,
                set_=dict(data),
            )
            try:
                session.execute(do_update_stmt)
                session.commit()
            except IntegrityError as error:
                logging.error(error)

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
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)


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
