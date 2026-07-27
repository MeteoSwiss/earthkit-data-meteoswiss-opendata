"""Tests for Earthkit plugin discovery."""

from importlib.metadata import entry_points

from earthkit_data_meteoswiss_opendata.source import (
    MeteoSwissOpenDataSource,
)


def test_plugin_entry_point_is_registered() -> None:
    (plugin,) = entry_points(
        group="earthkit.data.sources",
        name="meteoswiss-opendata",
    )

    assert plugin.load() is MeteoSwissOpenDataSource
