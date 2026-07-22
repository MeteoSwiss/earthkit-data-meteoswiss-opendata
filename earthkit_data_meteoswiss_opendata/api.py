"""MeteoSwiss Open Data STAC API helpers."""

import datetime as dt
import re
from typing import Any
from urllib.parse import urlparse

import requests

from .request import Request


API_URL = "https://data.geo.admin.ch/api/stac/v1"
SESSION = requests.Session()
TIMEOUT = 30


def _search(
    url: str,
    body: dict[str, Any],
) -> list[str]:
    """Execute a STAC search, following pagination links."""

    response = SESSION.post(
        url,
        json=body,
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    result: list[str] = []
    payload = response.json()

    for feature in payload.get("features", []):
        for asset in feature.get("assets", {}).values():
            result.append(asset["href"])

    for link in payload.get("links", []):
        if link.get("rel") != "next":
            continue

        if (
            link.get("method") != "POST"
            or not link.get("merge")
        ):
            raise RuntimeError(
                f"Unsupported STAC pagination link: {link}"
            )

        next_body = {
            **body,
            **link.get("body", {}),
        }

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

    urls = _search(
        f"{API_URL}/search",
        request.dump(),
    )

    if not urls:
        raise ValueError(
            "No assets matched the request"
        )

    # Preserve the behaviour of the original ogd_api.
    if len(urls) == 1:
        return urls

    pattern = re.compile(
        r"-(?P<ref_time>\d{12})-"
        r"(?P<lead_time>\d+)-"
    )

    def extract_key(
        url: str,
    ) -> tuple[dt.datetime, dt.timedelta]:
        path = urlparse(url).path
        match = pattern.search(path)

        if match is None:
            raise ValueError(
                f"No valid forecast datetime found in URL: {url}"
            )

        ref_time = dt.datetime.strptime(
            match.group("ref_time"),
            "%Y%m%d%H%M",
        ).replace(tzinfo=dt.timezone.utc)

        lead_time = dt.timedelta(
            hours=float(match.group("lead_time"))
        )

        return ref_time, lead_time

    asset_map = {
        extract_key(url): url
        for url in urls
    }

    available: dict[
        dt.datetime,
        set[dt.timedelta],
    ] = {}

    for ref_time, lead_time in asset_map:
        available.setdefault(
            ref_time,
            set(),
        ).add(lead_time)

    required = set(request.lead_times)

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
        latest = complete_runs[-1]

        return [
            asset_map[(latest, lead_time)]
            for lead_time in request.lead_times
        ]

    # Preserve the old lead-time-first ordering.
    return [
        asset_map[(ref_time, lead_time)]
        for lead_time in request.lead_times
        for ref_time in complete_runs
    ]
