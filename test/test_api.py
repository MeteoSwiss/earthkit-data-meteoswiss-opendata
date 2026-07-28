"""Tests for STAC asset selection."""

from unittest.mock import MagicMock, call

import pytest

from earthkit_data_meteoswiss_opendata import api
from earthkit_data_meteoswiss_opendata.request import Request


def make_request(
    lead_time: str | list[str],
) -> Request:
    """Create a valid request for API tests."""
    return Request(
        collection="ogd-forecasting-icon-ch2",
        variable="TOT_PREC",
        perturbed=False,
        ref_time="latest",
        lead_time=lead_time,
    )


def test_search_collects_paginated_assets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Collect asset URLs from the current and next result pages."""
    first_response = MagicMock()
    first_response.json.return_value = {
        "features": [{"assets": {"forecast": {"href": ("https://example.test/first.grib2")}}}],
        "links": [
            {
                "rel": "next",
                "href": "https://example.test/search",
                "method": "POST",
                "merge": True,
                "body": {
                    "token": "next-page",
                },
            }
        ],
    }

    second_response = MagicMock()
    second_response.json.return_value = {
        "features": [{"assets": {"forecast": {"href": ("https://example.test/second.grib2")}}}],
        "links": [],
    }

    post = MagicMock(
        side_effect=[
            first_response,
            second_response,
        ]
    )

    monkeypatch.setattr(
        api.session,
        "post",
        post,
    )

    body = {
        "collections": [
            "example-collection",
        ],
    }

    result = api._search(
        "https://example.test/search",
        body,
    )

    assert result == [
        "https://example.test/first.grib2",
        "https://example.test/second.grib2",
    ]

    assert post.call_args_list == [
        call(
            "https://example.test/search",
            json=body,
            timeout=api.TIMEOUT,
        ),
        call(
            "https://example.test/search",
            json={
                "collections": [
                    "example-collection",
                ],
                "token": "next-page",
            },
            timeout=api.TIMEOUT,
        ),
    ]

    first_response.raise_for_status.assert_called_once_with()
    second_response.raise_for_status.assert_called_once_with()


def test_latest_selects_newest_complete_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Skip a newer incomplete run."""
    urls = [
        # Older complete run.
        ("https://example.test/icon-ch2-202607200000-0-TOT_PREC.grib2"),
        ("https://example.test/icon-ch2-202607200000-1-TOT_PREC.grib2"),
        # Newer incomplete run.
        ("https://example.test/icon-ch2-202607200600-0-TOT_PREC.grib2"),
    ]

    monkeypatch.setattr(
        api,
        "_search",
        lambda url, body: urls,
    )

    result = api.get_asset_urls(make_request(["PT0H", "PT1H"]))

    assert result == [
        ("https://example.test/icon-ch2-202607200000-0-TOT_PREC.grib2"),
        ("https://example.test/icon-ch2-202607200000-1-TOT_PREC.grib2"),
    ]


def test_no_assets_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raise an error when the STAC search returns no assets."""
    monkeypatch.setattr(
        api,
        "_search",
        lambda url, body: [],
    )

    with pytest.raises(
        ValueError,
        match="No assets matched",
    ):
        api.get_asset_urls(make_request("PT1H"))


def test_no_complete_run_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raise an error when no run has all requested lead times."""
    monkeypatch.setattr(
        api,
        "_search",
        lambda url, body: [
            ("https://example.test/icon-ch2-202607200000-0-TOT_PREC.grib2"),
        ],
    )

    with pytest.raises(
        ValueError,
        match="No complete forecast run",
    ):
        api.get_asset_urls(make_request(["PT0H", "PT1H"]))


def test_get_collection_asset_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = MagicMock()
    response.json.return_value = {
        "assets": [
            {
                "id": "horizontal_constants_icon-ch2-eps.grib2",
                "href": "https://example.test/horizontal.grib2",
            }
        ]
    }

    get = MagicMock(return_value=response)
    monkeypatch.setattr(api.session, "get", get)

    result = api.get_collection_asset_url(
        collection_id=("ch.meteoschweiz.ogd-forecasting-icon-ch2"),
        asset_id=("horizontal_constants_icon-ch2-eps.grib2"),
    )

    assert result == "https://example.test/horizontal.grib2"
    response.raise_for_status.assert_called_once_with()


def test_get_collection_asset_url_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = MagicMock()
    response.json.return_value = {
        "assets": [],
    }

    monkeypatch.setattr(
        api.session,
        "get",
        MagicMock(return_value=response),
    )

    with pytest.raises(
        KeyError,
        match="Asset .* was not found",
    ):
        api.get_collection_asset_url(
            collection_id=("ch.meteoschweiz.ogd-forecasting-icon-ch2"),
            asset_id=("horizontal_constants_icon-ch2-eps.grib2"),
        )
