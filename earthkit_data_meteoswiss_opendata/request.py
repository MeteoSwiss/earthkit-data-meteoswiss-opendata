"""
Request validation and STAC query creation.

Copyright (c) 2026 MeteoSwiss, contributors listed in AUTHORS

Distributed under the terms of the BSD 3-Clause License.

SPDX-License-Identifier: BSD-3-Clause
"""

import datetime as dt
import enum
import logging
from typing import Annotated, Any

from pydantic import (
    AliasChoices,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
)
from pydantic.dataclasses import dataclass


logger = logging.getLogger(__name__)
DurationAdapter = TypeAdapter(dt.timedelta)


class Collection(enum.StrEnum):
    """Supported MeteoSwiss Open Data NWP collections."""

    ICON_CH1 = "ogd-forecasting-icon-ch1"
    ICON_CH2 = "ogd-forecasting-icon-ch2"
    KENDA_CH1 = "ogd-analysis-kenda-ch1"

    @property
    def stac_id(self) -> str:
        """Return the full STAC collection identifier."""
        return f"ch.meteoschweiz.{self.value}"


def _normalise_datetime(value: str) -> str:
    """Convert an ISO 8601 datetime string to UTC."""

    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Invalid ISO 8601 datetime: {value!r}") from exc

    if parsed.tzinfo is None:
        raise ValueError(f"Datetime must include a timezone: {value!r}")

    parsed = parsed.astimezone(dt.timezone.utc).replace(microsecond=0)

    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalise_reference_datetime(value: str) -> str:
    """Validate and normalize a STAC reference-time filter."""

    if value == "latest":
        return value

    parts = value.split("/")

    if len(parts) == 1:
        return _normalise_datetime(parts[0])

    if len(parts) != 2:
        raise ValueError(f"Unable to parse reference_datetime: {value!r}")

    lower, upper = parts

    if lower == upper == "..":
        raise ValueError("At least one reference_datetime bound must be specified")

    normalised_lower = ".." if lower == ".." else _normalise_datetime(lower)
    normalised_upper = ".." if upper == ".." else _normalise_datetime(upper)

    if normalised_lower != ".." and normalised_upper != "..":
        lower_dt = dt.datetime.fromisoformat(normalised_lower.replace("Z", "+00:00"))
        upper_dt = dt.datetime.fromisoformat(normalised_upper.replace("Z", "+00:00"))

        if upper_dt < lower_dt:
            raise ValueError("reference_datetime bounds inverted")

    return f"{normalised_lower}/{normalised_upper}"


@dataclass(
    frozen=True,
    config=ConfigDict(extra="forbid"),
)
class Request:
    """Validated MeteoSwiss forecast request.

    ``ref_time`` is accepted as an alias for
    ``reference_datetime``.

    ``lead_time`` is accepted as an alias for ``horizon``.
    """

    collection: Collection

    variable: Annotated[
        str,
        Field(min_length=1),
    ]

    reference_datetime: Annotated[
        str,
        Field(
            validation_alias=AliasChoices(
                "reference_datetime",
                "ref_time",
            )
        ),
    ]

    perturbed: bool

    horizon: Annotated[
        dt.timedelta | list[dt.timedelta],
        Field(
            validation_alias=AliasChoices(
                "horizon",
                "lead_time",
            )
        ),
    ]

    @field_validator(
        "reference_datetime",
        mode="before",
    )
    @classmethod
    def validate_reference_datetime(
        cls,
        value: Any,
    ) -> str:
        """Validate and normalize the reference datetime."""

        if isinstance(value, dt.datetime):
            if value.tzinfo is None:
                logger.warning("Assuming UTC for a naive reference datetime")
                value = value.replace(tzinfo=dt.timezone.utc)

            value = value.astimezone(dt.timezone.utc).replace(microsecond=0)

            return value.strftime("%Y-%m-%dT%H:%M:%SZ")

        if not isinstance(value, str):
            raise ValueError("reference_datetime must be a string or datetime")

        return _normalise_reference_datetime(value)

    @field_validator("horizon")
    @classmethod
    def validate_horizon(
        cls,
        value: dt.timedelta | list[dt.timedelta],
    ) -> dt.timedelta | list[dt.timedelta]:
        """Validate one or more forecast horizons."""

        horizons = value if isinstance(value, list) else [value]

        if not horizons:
            raise ValueError("At least one horizon must be requested")

        if any(horizon < dt.timedelta(0) for horizon in horizons):
            raise ValueError("Forecast horizons cannot be negative")

        if len(set(horizons)) != len(horizons):
            raise ValueError("Forecast horizons must be unique")

        return value

    @property
    def lead_times(self) -> list[dt.timedelta]:
        """Return the requested horizons as a list."""

        if isinstance(self.horizon, list):
            return list(self.horizon)

        return [self.horizon]

    def to_stac_query(
        self,
        *,
        now: dt.datetime | None = None,
    ) -> dict[str, Any]:
        """Create the STAC search request body."""

        reference_datetime = self.reference_datetime

        if reference_datetime == "latest":
            now = now or dt.datetime.now(tz=dt.timezone.utc)

            if now.tzinfo is None:
                raise ValueError("now must include a timezone")

            cutoff = now.astimezone(dt.timezone.utc) - dt.timedelta(hours=48)

            reference_datetime = f"{cutoff:%Y-%m-%dT%H:%M:%SZ}/.."

        body: dict[str, Any] = {
            "collections": [self.collection.stac_id],
            "forecast:variable": self.variable,
            "forecast:reference_datetime": reference_datetime,
            "forecast:perturbed": self.perturbed,
        }

        # The STAC API accepts one horizon filter.
        # For multiple lead times, retrieve a broader result
        # and select the complete run client-side.
        if len(self.lead_times) == 1:
            body["forecast:horizon"] = DurationAdapter.dump_python(
                self.lead_times[0],
                mode="json",
            )

        return body

    def dump(self) -> dict[str, Any]:
        """Backward-compatible alias for the old API."""
        return self.to_stac_query()
