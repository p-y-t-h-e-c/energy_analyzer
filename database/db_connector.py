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

    def add_data_to_db(self, ref_table: Table, data: dict[str, Any]) -> None:
        """Add data to database.

        :param ref_table: db table reference
        :param data: a row of data in dict format to be added te a table
        """
        with Session(self._engine) as session:
            insert = ref_table.insert().values(**data)

            try:
                session.execute(insert)
                session.commit()
            except IntegrityError:
                print("Record already in already exists in the database.")
