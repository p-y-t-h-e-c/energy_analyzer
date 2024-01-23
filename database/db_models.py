"""Database models."""
from typing import Type, Union

from sqlalchemy import Date, Float, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(DeclarativeBase, MappedAsDataclass):
    """Tables dafinition base class."""

    @classmethod
    def db_table(cls) -> Table:
        """Create a Table object."""
        return Table(cls.__tablename__, Base.metadata)


class ElectricityRatesTable(Base):
    """Electricity rates table."""

    __tablename__ = "electricity_rates"

    date: Mapped[Date] = mapped_column(Date, primary_key=True)
    unit_rate_exc_vat: Mapped[Float] = mapped_column(Float, nullable=False)
    unit_rate_inc_vat: Mapped[Float] = mapped_column(Float, nullable=False)


class GasRatesTable(Base):
    """Electricity rates table."""

    __tablename__ = "gas_rates"

    date: Mapped[Date] = mapped_column(Date, primary_key=True)
    unit_rate_exc_vat: Mapped[Float] = mapped_column(Float, nullable=False)
    unit_rate_inc_vat: Mapped[Float] = mapped_column(Float, nullable=False)


class ElectricityConsumptionTable(Base):
    """Electricity consumption table."""

    __tablename__ = "electricity_consumption"

    date: Mapped[Date] = mapped_column(Date, primary_key=True)
    consumption: Mapped[Float] = mapped_column(Float, nullable=False)


class GasConsumptionTable(Base):
    """Gas consumption table."""

    __tablename__ = "gas_consumption"

    date: Mapped[Date] = mapped_column(Date, primary_key=True)
    consumption: Mapped[Float] = mapped_column(Float, nullable=False)


class ElectricityWeeklyConsumptionTable2022(Base):
    """Electricity consumption table."""

    __tablename__ = "electricity_weekly_consumption_2022"

    week: Mapped[str] = mapped_column(String, primary_key=True)
    consumption: Mapped[Float] = mapped_column(Float, nullable=False)


class ElectricityWeeklyConsumptionTable2023(Base):
    """Electricity consumption table."""

    __tablename__ = "electricity_weekly_consumption_2023"

    week: Mapped[str] = mapped_column(String, primary_key=True)
    consumption: Mapped[Float] = mapped_column(Float, nullable=False)


class ElectricityWeeklyConsumptionTable2024(Base):
    """Electricity consumption table."""

    __tablename__ = "electricity_weekly_consumption_2024"

    week: Mapped[str] = mapped_column(String, primary_key=True)
    consumption: Mapped[Float] = mapped_column(Float, nullable=False)


class GasWeeklyConsumptionTable2022(Base):
    """Gas consumption table."""

    __tablename__ = "gas_weekly_consumption_2022"

    week: Mapped[str] = mapped_column(String, primary_key=True)
    consumption: Mapped[Float] = mapped_column(Float, nullable=False)


class GasWeeklyConsumptionTable2023(Base):
    """Gas consumption table."""

    __tablename__ = "gas_weekly_consumption_2023"

    week: Mapped[str] = mapped_column(String, primary_key=True)
    consumption: Mapped[Float] = mapped_column(Float, nullable=False)


class GasWeeklyConsumptionTable2024(Base):
    """Gas consumption table."""

    __tablename__ = "gas_weekly_consumption_2024"

    week: Mapped[str] = mapped_column(String, primary_key=True)
    consumption: Mapped[Float] = mapped_column(Float, nullable=False)


OctopusTables = Union[
    Type[ElectricityRatesTable],
    Type[ElectricityConsumptionTable],
    Type[GasRatesTable],
    Type[GasConsumptionTable],
    Type[ElectricityWeeklyConsumptionTable2022],
    Type[ElectricityWeeklyConsumptionTable2023],
    Type[ElectricityWeeklyConsumptionTable2024],
    Type[GasWeeklyConsumptionTable2022],
    Type[GasWeeklyConsumptionTable2023],
    Type[GasWeeklyConsumptionTable2024],
]


if __name__ == "__main__":
    print(ElectricityRatesTable.__tablename__)
