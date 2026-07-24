"""
MeteoSwiss Open Data STAC API helpers.

Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS

Distributed under the terms of the BSD 3-Clause License.

SPDX-License-Identifier: BSD-3-Clause
"""

import datetime as dt
import re
from typing import Any
from urllib.parse import urlparse

import requests

from .request import Request


API_URL = "https://data.geo.admin.ch/api/stac/v1"
TIMEOUT = 30

session = requests.Session()

def _search(
    url: str,
    body: dict[str, Any],
) -> list[str]:
    """Execute a STAC search and collect asset URLs from all result pages.

    The STAC response contains matching items in ``features``. Each item
    contains an ``assets`` mapping whose ``href`` values point to the
    downloadable files.

    When more results are available, the response contains a link with
    ``rel="next"`` in ``links``. Its request parameters are merged with
    the current search body and used to retrieve the next page.

    Args:
        url: STAC search endpoint or next-page URL.
        body: JSON-compatible STAC search body.

    Returns:
        Asset URLs from the current page and any following pages.

    Raises:
        requests.HTTPError: If the STAC request fails.
        RuntimeError: If an unsupported pagination link is returned.
    """
    response = session.post(
        url,
        json=body,
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    payload = response.json()
    result: list[str] = []

    # Each feature is a matching STAC item. Its assets contain
    # the downloadable file URLs.
    for feature in payload.get("features", []):
        for asset in feature.get("assets", {}).values():
            result.append(asset["href"])

    # A link with rel="next" indicates another page of results.
    for link in payload.get("links", []):
        if link.get("rel") != "next":
            continue

        # The API describes the next page as another POST request
        # whose body must be merged with the current search body.
        if (
            link.get("method") != "POST"
            or not link.get("merge")
        ):
            raise RuntimeError(
                f"Unsupported STAC pagination link: {link}"
            )

        # Keep the search filters and add the next-page parameters.
        next_body = {
            **body,
            **link.get("body", {}),
        }

        # Retrieve the next page and append its asset URLs.
        result.extend(
            _search(
                link["href"],
                next_body,
            )
        )

    return result


def get_asset_urls(request: Request) -> list[str]:
    """Return assets matching a MeteoSwiss request.

    For requests with several lead times, only complete
    forecast runs are returned.
    """

    # Convert the validated request into a STAC search.
    urls = _search(
        f"{API_URL}/search",
        request.dump(),
    )

    if not urls:
        raise ValueError(
            "No assets matched the request"
        )

    # No run selection is needed for one requested and returned asset.
    if len(urls) == 1 and len(request.lead_times) == 1:
        return urls

    # Extract reference time and lead time from OGD asset filenames.
    pattern = re.compile(
        r"-(?P<ref_time>\d{12})-"
        r"(?P<lead_time>\d+)-"
    )

    def extract_key(
        url: str,
    ) -> tuple[dt.datetime, dt.timedelta]:
        """Return the forecast run and lead time encoded in a URL."""

        # Parse only the URL path, excluding query parameters.
        path = urlparse(url).path
        match = pattern.search(path)

        if match is None:
            raise ValueError(
                f"No valid forecast datetime found in URL: {url}"
            )

        # Convert YYYYMMDDHHMM into a timezone-aware UTC datetime.
        ref_time = dt.datetime.strptime(
            match.group("ref_time"),
            "%Y%m%d%H%M",
        ).replace(tzinfo=dt.timezone.utc)

        # Convert the encoded forecast hour into a timedelta.
        lead_time = dt.timedelta(
            hours=float(match.group("lead_time"))
        )

        return ref_time, lead_time

    # Index each asset by forecast run and lead time.
    asset_map = {
        extract_key(url): url
        for url in urls
    }

    # Record which lead times are available for each forecast run.
    available: dict[
        dt.datetime,
        set[dt.timedelta],
    ] = {}

    for ref_time, lead_time in asset_map:
        available.setdefault(
            ref_time,
            set(),
        ).add(lead_time)

    # Lead times requested by the user.
    required = set(request.lead_times)

    # Keep only runs containing every requested lead time.
    complete_runs = sorted(
        ref_time
        for ref_time, lead_times in available.items()
        if lead_times >= required
    )

    if not complete_runs:
        raise ValueError(
            "No complete forecast run contains all "
            "requested lead times"
        )

    if request.reference_datetime == "latest":
        # Select the newest complete forecast run.
        latest = complete_runs[-1]

        # Preserve the lead-time order requested by the user.
        return [
            asset_map[(latest, lead_time)]
            for lead_time in request.lead_times
        ]

    # For an explicit time range, return every complete run,
    # ordered first by requested lead time and then by run time.
    return [
        asset_map[(ref_time, lead_time)]
        for lead_time in request.lead_times
        for ref_time in complete_runs
    ]
