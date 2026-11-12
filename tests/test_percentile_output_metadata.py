"""
Output metadata of the percentile indices (issue #676).

The metadata templates of the generic ``percentile`` and of
``difference_of_count_occurences`` were the placeholder ``"todo"``, which the DCSC
``PQ90`` and ``PQ99`` and the generic ``icclim.percentile`` exposed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim._core.generic.generic_templates import INDICATORS_TEMPLATES_EN
from icclim._core.generic.indicator import GenericIndicator


def _precipitation(unit: str = "mm/day") -> xr.DataArray:
    time = pd.date_range("2001-01-01", "2002-12-31", freq="D")
    rng = np.random.default_rng(20261113)
    values = rng.gamma(1.6, 3.0, (len(time), 2, 2))
    return xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]},
        name="pr",
        attrs={"units": unit},
    )


@pytest.mark.parametrize("name", ["PQ90", "PQ99"])
def test_precipitation_percentile_metadata_is_meaningful(name: str) -> None:
    """Published percentile outputs must not expose placeholder metadata."""
    actual = getattr(icclim.dcsc, name.lower())(
        _precipitation(),
        slice_mode="year",
        time_range=["2001-01-01", "2002-12-31"],
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[name]
    assert actual.attrs["long_name"] != "todo"
    assert actual.attrs["standard_name"] != "todo"
    assert actual.attrs["cell_methods"] != "todo"
    assert actual.attrs["long_name"] == (
        "Percentile of the daily precipitation for each year."
    )
    assert actual.attrs["standard_name"] == "precipitation_flux"
    assert actual.attrs["cell_methods"] == "time: percentile over days"


def test_generic_percentile_metadata_is_meaningful() -> None:
    actual = icclim.percentile(
        _precipitation(),
        threshold="> 90 doy_per",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    ).percentile
    assert "todo" not in {
        actual.attrs["standard_name"],
        actual.attrs["long_name"],
        actual.attrs["cell_methods"],
    }
    assert actual.attrs["long_name"].startswith("Percentile of the daily precipitation")


def test_no_template_is_a_placeholder() -> None:
    for name, template in INDICATORS_TEMPLATES_EN.items():
        for key, text in template.items():
            assert "todo" not in text.lower(), (name, key)


def test_difference_of_count_occurences_has_no_invented_standard_name() -> None:
    template = INDICATORS_TEMPLATES_EN["difference_of_count_occurences"]
    assert "standard_name" not in template
    assert template["long_name"].startswith("Difference of the number of")
    indicator = GenericIndicator(
        "difference_of_count_occurences",
        lambda **_: None,
        check_vars=lambda *_: None,
        definition="Difference of counts.",
    )
    assert indicator.standard_name == ""
