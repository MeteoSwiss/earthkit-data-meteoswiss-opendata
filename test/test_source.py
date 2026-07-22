"""Tests for the Earthkit source adapter."""

from unittest.mock import MagicMock

import pytest

from earthkit_data_meteoswiss_opendata import source


def test_source_builds_validated_request() -> None:
    result = source.MeteoSwissOpenDataSource(
        collection="ogd-forecasting-icon-ch2",
        variable="TOT_PREC",
        perturbed=False,
        ref_time="latest",
        lead_time=["PT0H", "PT1H"],
    )

    assert result.request.variable == "TOT_PREC"
    assert len(result.request.lead_times) == 2


def test_source_delegates_to_url_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    urls = [
        "https://example.test/forecast-0.grib2",
        "https://example.test/forecast-1.grib2",
    ]
    url_source = object()

    get_asset_urls = MagicMock(return_value=urls)
    get_source = MagicMock(return_value=url_source)

    monkeypatch.setattr(
        source,
        "get_asset_urls",
        get_asset_urls,
    )
    monkeypatch.setattr(
        source,
        "get_source",
        get_source,
    )

    plugin_source = source.MeteoSwissOpenDataSource(
        collection="ogd-forecasting-icon-ch2",
        variable="TOT_PREC",
        perturbed=False,
        ref_time="latest",
        lead_time=["PT0H", "PT1H"],
    )

    result = plugin_source.mutate()

    get_asset_urls.assert_called_once_with(
        plugin_source.request
    )
    get_source.assert_called_once_with("url", urls)
    assert result is url_source
