"""
Earthkit source for MeteoSwiss Open Data.

Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS

Distributed under the terms of the BSD 3-Clause License.

SPDX-License-Identifier: BSD-3-Clause
"""

import datetime as dt

from earthkit.data.sources import Source, get_source

from .api import get_asset_urls
from .request import Collection, Request



class MeteoSwissOpenDataSource(Source):
    """Earthkit source for MeteoSwiss Open Data."""

    def __init__(
        self,
        *,
        collection: Collection | str,
        variable: str,
        perturbed: bool,
        ref_time: str | dt.datetime,
        lead_time: (
            str
            | dt.timedelta
            | list[str | dt.timedelta]
        ),
    ) -> None:
        super().__init__()

        # Pydantic validators accept and normalize the input types in request.py.
        # Mypy only sees the final dataclass field types, thus the `ignore`.`
        self.request = Request(
            collection=collection,  # type: ignore[arg-type]
            variable=variable,
            perturbed=perturbed,
            reference_datetime=ref_time,  # type: ignore[arg-type]
            horizon=lead_time,  # type: ignore[arg-type]
        )

    def mutate(self) -> Source:
        """Convert the request into Earthkit's URL source."""
        urls = get_asset_urls(self.request)
        return get_source("url", urls)
