from typing import Any

from sqlalchemy import Table, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


class DbConnector:
    """Database connector."""

    def __init__(self, database_url: str, echo: bool = False):
        self._engine = create_engine(
            database_url,
            echo=echo,
        )

    def add_unit_rates(self, ref_table: Table, unit_rate: dict[str, Any]):
        with Session(self._engine) as session:
            rates_table = ref_table
            rates_dict = unit_rate

            insert = rates_table.insert().values(**rates_dict)

            try:
                session.execute(insert)
                session.commit()
            except IntegrityError:
                print("Record already in already exists in the database.")

    def add_consumption_values(
        self, ref_table: Table, consumption_unit: dict[str, Any]
    ):
        with Session(self._engine) as session:
            rates_table = ref_table
            rates_dict = consumption_unit

            insert = rates_table.insert().values(**rates_dict)

            try:
                session.execute(insert)
                session.commit()
            except IntegrityError:
                print("Record already in already exists in the database.")
