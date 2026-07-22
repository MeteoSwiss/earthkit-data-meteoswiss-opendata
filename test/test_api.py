"""Tests for STAC asset selection."""

import pytest

from earthkit_data_meteoswiss_opendata import api
from earthkit_data_meteoswiss_opendata.request import Request


def make_request(
    lead_time: str | list[str],
) -> Request:
    return Request(
        collection="ogd-forecasting-icon-ch2",
        variable="TOT_PREC",
        perturbed=False,
        ref_time="latest",
        lead_time=lead_time,
    )


def test_latest_selects_newest_complete_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    urls = [
        # Older complete run.
        "https://example.test/icon-ch2-202607200000-0-TOT_PREC.grib2",
        "https://example.test/icon-ch2-202607200000-1-TOT_PREC.grib2",

        # Newer incomplete run.
        "https://example.test/icon-ch2-202607200600-0-TOT_PREC.grib2",
    ]

    monkeypatch.setattr(
        api,
        "_search",
        lambda url, body: urls,
    )

    result = api.get_asset_urls(
        make_request(["PT0H", "PT1H"])
    )

    assert result == [
        "https://example.test/icon-ch2-202607200000-0-TOT_PREC.grib2",
        "https://example.test/icon-ch2-202607200000-1-TOT_PREC.grib2",
    ]


def test_no_assets_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        api,
        "_search",
        lambda url, body: [],
    )

    with pytest.raises(
        ValueError,
        match="No assets matched",
    ):
        api.get_asset_urls(
            make_request("PT1H")
        )


def test_no_complete_run_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        api,
        "_search",
        lambda url, body: [
            "https://example.test/icon-ch2-202607200000-0-TOT_PREC.grib2",
        ],
    )

    with pytest.raises(
        ValueError,
        match="No complete forecast run",
    ):
        api.get_asset_urls(
            make_request(["PT0H", "PT1H"])
        )