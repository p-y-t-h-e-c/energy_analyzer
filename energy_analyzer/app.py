"""Main app module."""
from dagster import (
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_modules,
)

from energy_analyzer import main

all_assets = load_assets_from_modules([main])

all_asset_job = define_asset_job(name="all_asset_job")

default_schedule = ScheduleDefinition(job=all_asset_job, cron_schedule="0 */2 * * *")

defs = Definitions(
    assets=all_assets, jobs=[all_asset_job], schedules=[default_schedule]
)
