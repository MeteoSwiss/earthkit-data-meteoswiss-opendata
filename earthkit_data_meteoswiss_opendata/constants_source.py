"""
Earthkit source for MeteoSwiss constant assets.

Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS

Distributed under the terms of the BSD 3-Clause License.

SPDX-License-Identifier: BSD-3-Clause
"""

from enum import StrEnum

from earthkit.data.sources import Source, get_source

from .api import get_collection_asset_url
from .request import Collection


class ConstantAsset(StrEnum):
    """Types of constant model data available from MeteoSwiss."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


# Collection names and constant-asset filenames use different model suffixes.
_MODEL_SUFFIXES = {
    Collection.ICON_CH1: "icon-ch1-eps",
    Collection.ICON_CH2: "icon-ch2-eps",
    Collection.KENDA_CH1: "kenda-ch1",
}


class MeteoSwissConstantsSource(Source):
    """Retrieve horizontal or vertical constants for a model collection."""

    def __init__(
        self,
        *,
        collection: Collection | str,
        asset: ConstantAsset | str,
    ) -> None:
        super().__init__()

        # Validate and normalise public string arguments.
        self.collection = Collection(collection)
        self.asset = ConstantAsset(asset)

    def mutate(self) -> Source:
        """Resolve the constant asset to an Earthkit URL source."""
        try:
            model_suffix = _MODEL_SUFFIXES[self.collection]
        except KeyError as exc:
            raise ValueError(f"Constants are not supported for collection {self.collection.value!r}") from exc

        # MeteoSwiss STAC collection IDs include this namespace.
        collection_id = f"ch.meteoschweiz.{self.collection.value}"

        # Static assets follow the MeteoSwiss naming convention.
        asset_id = f"{self.asset.value}_constants_{model_suffix}.grib2"

        url = get_collection_asset_url(
            collection_id=collection_id,
            asset_id=asset_id,
        )

        # Defer downloading and decoding to Earthkit.
        return get_source("url", url)
