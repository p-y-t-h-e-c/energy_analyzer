"""Tariff's data models module."""

import re

from pydantic_settings import BaseSettings


def get_product_code(tariff_code: str) -> str:
    """Extract product code from a respective tariff code.

    Args:
        tariff_code: a tariff code

    Returns:
        a product code in string format
    """
    product_code: str = re.compile("[EG]-1R-(.*)-B").findall(tariff_code)[0]
    return product_code


class OctopusElectricityImport2022(BaseSettings):
    """Electricity Import 2022."""

    tariff_code: str = "E-1R-VAR-22-04-02-B"
    valid_from: str = "2022-08-01"
    valid_to: str = "2023-02-13"


class OctopusElectricityImport2023(BaseSettings):
    """Electricity Import 2023."""

    tariff_code: str = "E-1R-SILVER-FLEX-22-11-25-B"
    valid_from: str = "2023-02-13"
    valid_to: str = "2024-02-15"


class OctopusElectricityImport2024(BaseSettings):
    """Electricity Import 2024."""

    tariff_code: str = "E-1R-SILVER-23-12-06-B"
    valid_from: str = "2024-02-15"
    valid_to: str = "2025-02-15"


class OctopusGasImport2022(BaseSettings):
    """Electricity Import 2022."""

    tariff_code: str = "G-1R-VAR-22-04-02-B"
    valid_from: str = "2022-08-01"
    valid_to: str = "2023-02-13"


class OctopusGasImport2023(BaseSettings):
    """Electricity Import 2023."""

    tariff_code: str = "G-1R-SILVER-FLEX-22-11-25-B"
    valid_from: str = "2023-02-13"
    valid_to: str = "2024-02-15"


class OctopusGasImport2024(BaseSettings):
    """Electricity Import 2024."""

    tariff_code: str = "G-1R-SILVER-23-12-06-B"
    valid_from: str = "2024-02-15"
    valid_to: str = "2025-02-15"


if __name__ == "__main__":
    print(OctopusElectricityImport2024().tariff_code)
    print(get_product_code(OctopusGasImport2024().tariff_code))
