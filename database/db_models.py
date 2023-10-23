from sqlalchemy import Date, Float, Table
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass

    @classmethod
    def db_table(cls) -> Table:
        return Table(cls.__tablename__, Base.metadata)


class ElectricityRatesTable(Base):
    """Electricity Rates table."""

    __tablename__ = "electricity_rates"

    date = mapped_column(Date, primary_key=True)
    unit_rate_exc_vat = mapped_column(Float, nullable=False)
    unit_rate_inc_vat = mapped_column(Float, nullable=False)


class GasRatesTable(Base):
    """Electricity Rates table."""

    __tablename__ = "gas_rates"

    date = mapped_column(Date, primary_key=True)
    unit_rate_exc_vat = mapped_column(Float, nullable=False)
    unit_rate_inc_vat = mapped_column(Float, nullable=False)
