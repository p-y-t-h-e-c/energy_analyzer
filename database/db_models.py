from sqlalchemy import Date, DateTime, Float, Table
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    @classmethod
    def db_table(cls) -> Table:
        return Table(cls.__tablename__, Base.metadata)


class ElectricityRatesTable(Base):
    """Electricity rates table."""

    __tablename__ = "electricity_rates"

    date = mapped_column(Date, primary_key=True)
    unit_rate_exc_vat = mapped_column(Float, nullable=False)
    unit_rate_inc_vat = mapped_column(Float, nullable=False)


class GasRatesTable(Base):
    """Electricity rates table."""

    __tablename__ = "gas_rates"

    date = mapped_column(Date, primary_key=True)
    unit_rate_exc_vat = mapped_column(Float, nullable=False)
    unit_rate_inc_vat = mapped_column(Float, nullable=False)


class ElectricityConsumptionTable(Base):
    """Electricity consumption table"""

    __tablename__ = "electricity_consumption"

    date = mapped_column(DateTime, primary_key=True)
    consumption = mapped_column(Float, nullable=False)


class GasConsumptionTable(Base):
    """Gas consumption table"""

    __tablename__ = "gas_consumption"

    date = mapped_column(DateTime, primary_key=True)
    consumption = mapped_column(Float, nullable=False)
