"""Earthkit source for MeteoSwiss Open Data."""

import datetime as dt

from earthkit.data import Source
from earthkit.data.sources import get_source

from .api import get_asset_urls
from .request import Collection, Request


class MeteoSwissOpenDataSource(Source):
    """Retrieve MeteoSwiss Open Data through Earthkit."""

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

        # Build and validate the MeteoSwiss request from Earthkit arguments.
        self.request = Request(
            collection=collection,
            variable=variable,
            perturbed=perturbed,
            ref_time=ref_time,
            lead_time=lead_time,
        )

    def mutate(self):
        """Resolve the STAC request into Earthkit URL data."""

        # Find the GRIB files matching the validated STAC request.
        urls = get_asset_urls(self.request)

        # Earthkit handles downloading, caching and reading the GRIB files.
        return get_source("url", urls)
