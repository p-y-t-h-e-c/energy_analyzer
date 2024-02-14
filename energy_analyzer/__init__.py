from dagster import Definitions, load_assets_from_modules

from . import main

all_assets = load_assets_from_modules([main])

defs = Definitions(
    assets=all_assets,
)
