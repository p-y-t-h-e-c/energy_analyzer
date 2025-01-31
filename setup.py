"""Dagster setup module."""

from setuptools import find_packages, setup

setup(
    name="energy_analyzer",
    packages=find_packages(exclude=["energy_analyzer_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "dagster-graphql",
        "dagster-webserver",
        "dagster-postgres",
    ],
    extras_require={"dev": ["dagster-webserver", "pytest", "pre_commit"]},
)
