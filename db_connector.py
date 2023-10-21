from sqlalchemy import create_engine

from settings import Settings

CONF = Settings()


class SqliteConnector:
    """Sqlite database connector."""

    def __init__(self, database_path: str, echo: bool = False):
        self._engine = create_engine(
            f"sqlite:///{database_path}",
            echo=echo,
        )


# notifications / database / develop_notifications_backend.db
