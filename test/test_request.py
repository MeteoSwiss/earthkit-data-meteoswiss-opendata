"""Tests for request validation and STAC query creation."""

import datetime as dt

import pytest
from pydantic import ValidationError

from earthkit_data_meteoswiss_opendata.request import Request


def test_single_lead_time_query() -> None:
    request = Request(
        collection="ogd-forecasting-icon-ch2",
        variable="TOT_PREC",
        perturbed=False,
        ref_time="2026-07-20T06:00:00Z",
        lead_time="PT1H",
    )

    assert request.dump() == {
        "collections": [
            "ch.meteoschweiz.ogd-forecasting-icon-ch2"
        ],
        "forecast:variable": "TOT_PREC",
        "forecast:reference_datetime":
            "2026-07-20T06:00:00Z",
        "forecast:perturbed": False,
        "forecast:horizon": "PT1H",
    }


def test_multiple_lead_times_omit_horizon_filter() -> None:
    request = Request(
        collection="ogd-forecasting-icon-ch2",
        variable="TOT_PREC",
        perturbed=False,
        ref_time="2026-07-20T06:00:00Z",
        lead_time=["PT0H", "PT1H", "PT2H"],
    )

    query = request.dump()

    # STAC can only request one `horizon` item
    # so if len(ref_time) != 1, 
    # it sends a broader query without the horizon filter
    assert "forecast:horizon" not in query
    assert request.lead_times == [
        dt.timedelta(),
        dt.timedelta(hours=1),
        dt.timedelta(hours=2),
    ]


def test_latest_uses_48_hour_search_window() -> None:
    request = Request(
        collection="ogd-forecasting-icon-ch2",
        variable="TOT_PREC",
        perturbed=False,
        ref_time="latest",
        lead_time="PT1H",
    )

    now = dt.datetime(
        2026,
        7,
        20,
        12,
        tzinfo=dt.timezone.utc,
    )

    assert request.to_stac_query(now=now)[
        "forecast:reference_datetime"
    ] == "2026-07-18T12:00:00Z/.."


def test_invalid_collection_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Request(
            collection="invalid-collection",
            variable="TOT_PREC",
            perturbed=False,
            ref_time="latest",
            lead_time="PT1H",
        )


def test_duplicate_lead_times_are_rejected() -> None:
    with pytest.raises(
        ValidationError,
        match="Forecast horizons must be unique",
    ):
        Request(
            collection="ogd-forecasting-icon-ch2",
            variable="TOT_PREC",
            perturbed=False,
            ref_time="latest",
            lead_time=["PT1H", "PT1H"],
        )
