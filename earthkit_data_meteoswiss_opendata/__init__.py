"""
Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS

Distributed under the terms of the BSD 3-Clause License.

SPDX-License-Identifier: BSD-3-Clause
"""

from .api import API_URL, get_asset_urls
from .request import Collection, Request
from .source import MeteoSwissOpenDataSource

__all__ = [
    "API_URL",
    "Collection",
    "MeteoSwissOpenDataSource",
    "Request",
    "get_asset_urls",
]
