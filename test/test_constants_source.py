"""Tests for the MeteoSwiss constants source."""

from unittest.mock import MagicMock, call

import pytest
from earthkit.data.sources import Source

from earthkit_data_meteoswiss_opendata import (
    constants_source,
)


@pytest.mark.parametrize(
    ("asset", "asset_id"),
    [
        (
            "horizontal",
            "horizontal_constants_icon-ch2-eps.grib2",
        ),
        (
            "vertical",
            "vertical_constants_icon-ch2-eps.grib2",
        ),
    ],
)
def test_constants_source_mutate(
    monkeypatch: pytest.MonkeyPatch,
    asset: str,
    asset_id: str,
) -> None:
    url = f"https://example.test/{asset_id}"

    get_collection_asset_url = MagicMock(return_value=url)
    monkeypatch.setattr(
        constants_source,
        "get_collection_asset_url",
        get_collection_asset_url,
    )

    url_source = MagicMock(spec=Source)
    get_source = MagicMock(return_value=url_source)
    monkeypatch.setattr(
        constants_source,
        "get_source",
        get_source,
    )

    source = constants_source.MeteoSwissConstantsSource(
        collection="ogd-forecasting-icon-ch2",
        asset=asset,
    )

    result = source.mutate()

    assert result is url_source

    get_collection_asset_url.assert_called_once_with(
        collection_id=("ch.meteoschweiz.ogd-forecasting-icon-ch2"),
        asset_id=asset_id,
    )

    assert get_source.call_args == call(
        "url",
        url,
    )


def test_constants_source_rejects_invalid_asset() -> None:
    with pytest.raises(ValueError):
        constants_source.MeteoSwissConstantsSource(
            collection="ogd-forecasting-icon-ch2",
            asset="invalid",
        )
