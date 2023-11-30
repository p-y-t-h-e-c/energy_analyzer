"""Database connector module."""
import logging
from datetime import date
from typing import Any

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

        :return:
        """
        with self.session as session:
            stmt = select(table.date).order_by(desc(table.date)).limit(1)
            result = session.execute(stmt)
            return result.scalar_one()

    def reset_database(self) -> None:
        """Reset Database."""
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)


if __name__ == "__main__":
    from config import ProjectConfig
    from database.db_models import Base, ElectricityRatesTable

    config = ProjectConfig()

    data = {
        "date": "2023-11-21",
        "unit_rate_exc_vat": 1800,
        "unit_rate_inc_vat": 19.341,
    }
    db_url = config.db_url
    db_connector = DbConnector(db_url.get_secret_value())

    # print(db_connector.get_latest_date(ElectricityRatesTable))

    db_connector.reset_database()

    # db_connector.upsert_db(ElectricityRatesTable, data)
