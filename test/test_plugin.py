"""Tests for Earthkit plugin discovery."""

from importlib.metadata import entry_points

from earthkit_data_meteoswiss_opendata.constants_source import (
    MeteoSwissConstantsSource,
)
from earthkit_data_meteoswiss_opendata.source import (
    MeteoSwissOpenDataSource,
)


def test_forecast_plugin_is_registered() -> None:
    (plugin,) = entry_points(
        group="earthkit.data.sources",
        name="meteoswiss-opendata",
    )

    assert plugin.load() is MeteoSwissOpenDataSource


def test_constants_plugin_is_registered() -> None:
    (plugin,) = entry_points(
        group="earthkit.data.sources",
        name="meteoswiss-opendata-constants",
    )

    assert plugin.load() is MeteoSwissConstantsSource
