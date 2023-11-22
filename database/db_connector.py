"""Database connector module."""
from datetime import date
from typing import Any

from sqlalchemy import create_engine, desc, insert, select, update
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

    def add_data_to_db(self, ref_table: OctopusTables, data: dict[str, Any]) -> None:
        """Add data to database.

        :param ref_table: db table reference
        :param data: a row of data in dict format to be added te a table
        """
        with self.session as session:
            stmt = insert(ref_table.db_table()).values(**data)

            try:
                session.execute(stmt)
                session.commit()
            except IntegrityError:
                print("Record already in already exists in the database.")

    def get_date(self, ref_table: OctopusTables, data: dict[str, Any]) -> None:
        """Get primary key date data from a table.

        :param ref_table: db table reference
        :param data: a row of data in dict format
        """
        with self.session as session:
            result = session.get(ref_table, data["date"])
            if result:
                print("already in")
                print(result.date)
            else:
                print("not in db")

    def get_latest_date(self, ref_table: OctopusTables) -> date:
        """Get latest date from a table."""
        with self.session as session:
            stmt = select(ref_table.date).order_by(desc(ref_table.date)).limit(1)
            result = session.execute(stmt)
            return result.scalar_one()

    def db_update(self, ref_table: OctopusTables, data: dict[str, Any]) -> None:
        """Update an existing record in the table.

        :param ref_table: db table reference
        :param data: a row of data in dict format to be  te a table
        """
        with self.session as session:
            stmt = update(ref_table).where(ref_table.date == data["date"])
            result = session.execute(stmt)


if __name__ == "__main__":
    from config import ProjectConfig
    from database.db_models import Base, ElectricityRatesTable

    config = ProjectConfig()

    data = {
        "date": "2023-11-21",
        "unit_rate_exc_vat": 18.42,
        "unit_rate_inc_vat": 19.341,
    }
    db_url = config.db_url
    db_connector = DbConnector(db_url.get_secret_value())

    engine = create_engine(db_url.get_secret_value())
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # db_connector.get_date(ElectricityRatesTable, data)

    print(db_connector.get_latest_date(ElectricityRatesTable))
