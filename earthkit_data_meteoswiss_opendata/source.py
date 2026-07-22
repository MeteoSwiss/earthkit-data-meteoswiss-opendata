"""
Earthkit source for MeteoSwiss Open Data.

Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS

Distributed under the terms of the BSD 3-Clause License.

SPDX-License-Identifier: BSD-3-Clause
"""

import datetime as dt

from earthkit.data.sources import Source, get_source
from pydantic import TypeAdapter

from .api import get_asset_urls
from .request import Collection, Request


_REQUEST_ADAPTER = TypeAdapter(Request)


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

        self.request = _REQUEST_ADAPTER.validate_python(
            {
                "collection": collection,
                "variable": variable,
                "perturbed": perturbed,
                "ref_time": ref_time,
                "lead_time": lead_time,
            }
        )

    def mutate(self) -> Source:
        """Convert the request into Earthkit's URL source."""
        urls = get_asset_urls(self.request)
        return get_source("url", urls)
