"""
icclim does not use the deprecated ``DatetimeIndex.dayofyear`` of pandas (#743).

pandas 3.1 deprecates ``DatetimeIndex.dayofyear`` (``Pandas4Warning``, removed in
pandas 4): ``day_of_year`` exists on every supported pandas. The warning was recorded
in the provenance and hidden from the user, so a regression is not seen by a call.
These tests watch the attribute itself, so that they do not depend on the version of
pandas that is installed.
"""

from __future__ import annotations

import json
import sys
import warnings

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim._core.generic.bootstrap_primitives import _day_of_year

BASE = ["2000-01-01", "2002-12-31"]


def _ds() -> xr.Dataset:
    time = pd.date_range("2000-01-01", "2005-12-31")
    rng = np.random.default_rng(1)
    values = (290 + rng.normal(0, 3, len(time))).astype("float32")
    da = xr.DataArray(
        values.reshape(-1, 1, 1),
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [1.0], "lon": [2.0]},
        attrs={"units": "K"},
    )
    return xr.Dataset({"tasmax": da}).chunk({"time": 365})


@pytest.fixture
def dayofyear_callers(monkeypatch) -> list[str]:
    """Record the file that reads ``DatetimeIndex.dayofyear``, then read it as usual."""
    callers: list[str] = []

    def getter(self):
        callers.append(sys._getframe(1).f_code.co_filename)
        return self.day_of_year

    monkeypatch.setattr(pd.DatetimeIndex, "dayofyear", property(getter))
    return callers


def _icclim_callers(callers: list[str]) -> list[str]:
    return [name for name in callers if "icclim" in name and "/tests/" not in name]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"index_name": "TX90p"},
        {"index_name": "TX90p", "doy_window_width": 7},
        {"index_name": "WSDI"},
    ],
    ids=["TX90p", "TX90p window 7", "WSDI"],
)
def test_percentile_bootstrap_does_not_read_dayofyear_of_a_pandas_index(
    dayofyear_callers, kwargs
):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        icclim.index(
            in_files=_ds(),
            var_name="tasmax",
            slice_mode="year",
            base_period_time_range=BASE,
            **kwargs,
        )
    assert _icclim_callers(dayofyear_callers) == []


def test_no_pandas_4_warning_is_recorded_in_the_provenance(tmp_path):
    out = tmp_path / "out.nc"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        icclim.index(
            index_name="TX90p",
            in_files=_ds(),
            var_name="tasmax",
            slice_mode="year",
            base_period_time_range=BASE,
            out_file=str(out),
        )
    prov = json.loads((tmp_path / "out.prov.json").read_text())
    assert [w for w in prov["warnings"] if w["category"] == "Pandas4Warning"] == []


def test_day_of_year_gives_the_values_that_dayofyear_gave():
    index = pd.date_range("2000-01-01", "2004-12-31")
    expected = np.concatenate(
        [np.arange(1, 367), *[np.arange(1, 366)] * 3, np.arange(1, 367)]
    )
    np.testing.assert_array_equal(index.day_of_year.to_numpy(), expected[: len(index)])


@pytest.mark.parametrize(
    ("index", "days_in_the_year"),
    [
        (pd.date_range("2000-01-01", "2000-12-31"), 366),
        (xr.date_range("2001-01-01", "2001-12-31", calendar="noleap"), 365),
        (xr.date_range("2001-01-01", "2001-12-30", calendar="360_day"), 360),
        (xr.date_range("2000-01-01", "2000-12-31", calendar="standard"), 366),
        (
            xr.date_range(
                "2000-01-01", "2000-12-31", calendar="standard", use_cftime=True
            ),
            366,
        ),
    ],
    ids=["pandas", "noleap", "360_day", "standard", "standard cftime"],
)
def test_day_of_year_helper_handles_pandas_and_cftime_indexes(index, days_in_the_year):
    # A CFTimeIndex has no ``day_of_year`` before xarray 2026.9: ``dayofyear`` is used.
    np.testing.assert_array_equal(
        np.asarray(_day_of_year(index)), np.arange(1, days_in_the_year + 1)
    )
