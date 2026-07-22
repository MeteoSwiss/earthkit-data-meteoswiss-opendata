"""Live integration test for MeteoSwiss Open Data."""

import os

import earthkit.data as ekd
import pytest


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION") != "1",
    reason="Set RUN_INTEGRATION=1 to run live tests",
)
def test_main_nwp_use_case() -> None:
    forecast = ekd.from_source(
        "meteoswiss-opendata",
        collection="ogd-forecasting-icon-ch2",
        variable="TOT_PREC",
        perturbed=False,
        ref_time="latest",
        lead_time=["PT0H", "PT1H", "PT2H"],
    )

    dataset = forecast.to_xarray(
        profile="grib"
    )

    assert dataset.sizes["step"] == 3
    assert len(dataset.data_vars) >= 1
