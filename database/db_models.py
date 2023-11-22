"""Database models."""
from typing import Type, Union

from sqlalchemy import Date, DateTime, Float, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(DeclarativeBase, MappedAsDataclass):
    """Tables dafinition base class."""

    date: Mapped[Date] = mapped_column(Date, primary_key=True)

    @classmethod
    def db_table(cls) -> Table:
        """Create a Table object."""
        return Table(cls.__tablename__, Base.metadata)


class ElectricityRatesTable(Base):
    """Electricity rates table."""

    __tablename__ = "electricity_rates"

    unit_rate_exc_vat: Mapped[Float] = mapped_column(Float, nullable=False)
    unit_rate_inc_vat: Mapped[Float] = mapped_column(Float, nullable=False)


class GasRatesTable(Base):
    """Electricity rates table."""

    __tablename__ = "gas_rates"

    unit_rate_exc_vat: Mapped[Float] = mapped_column(Float, nullable=False)
    unit_rate_inc_vat: Mapped[Float] = mapped_column(Float, nullable=False)


class ElectricityConsumptionTable(Base):
    """Electricity consumption table."""

    __tablename__ = "electricity_consumption"

    consumption: Mapped[Float] = mapped_column(Float, nullable=False)


class GasConsumptionTable(Base):
    """Gas consumption table."""

    __tablename__ = "gas_consumption"

    consumption: Mapped[Float] = mapped_column(Float, nullable=False)


OctopusTables = Union[
    Type[ElectricityRatesTable],
    Type[ElectricityConsumptionTable],
    Type[GasRatesTable],
    Type[GasConsumptionTable],
]
