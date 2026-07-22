"""Earthkit source for MeteoSwiss Open Data."""

import datetime as dt

from earthkit.data.core import get_source
from earthkit.data.sources import Source
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
