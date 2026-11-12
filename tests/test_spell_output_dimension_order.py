"""
Dimension order of the spell indices that sum spell lengths (issue #669).

``TNCWD`` and ``TXHWD`` (DCSC) and ``WSDI`` and ``CSDI`` (ECA&D) give the dimensions in
the order of the input, with the resampled ``time`` where the input has it, as the
indices that use ``max_consecutive_occurrence`` do.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim

TIME = pd.date_range("2000-01-01", "2002-12-31", freq="D")
COORDS = {"time": TIME, "lat": [45.0, 46.0], "lon": [1.0, 2.0]}


def _normal_cube(direction: str, name: str) -> tuple[xr.DataArray, xr.DataArray]:
    """Study values and a daily normal, with an 8-day and a 3-day spell in 2001."""
    sign = 1.0 if direction == "warm" else -1.0
    normal_values = np.full((len(TIME), 2, 2), 10.0)
    values = normal_values.copy()
    values[(TIME >= "2001-07-01") & (TIME <= "2001-07-08")] += sign * 5.0
    values[(TIME >= "2001-08-01") & (TIME <= "2001-08-03"), 0, 1] += sign * 5.0
    study = xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords=COORDS,
        name=name,
        attrs={"units": "degC"},
    )
    normal = xr.DataArray(
        normal_values, dims=study.dims, coords=COORDS, name=name,
        attrs={"units": "degC"},
    )  # fmt: skip
    return study, normal


@pytest.mark.parametrize(
    ("name", "variable", "direction"),
    [("TXHWD", "tasmax", "warm"), ("TNCWD", "tasmin", "cold")],
)
def test_dcsc_normal_spells_follow_the_input_dimension_order(
    name: str, variable: str, direction: str
) -> None:
    study, normal = _normal_cube(direction, variable)
    function = getattr(icclim.dcsc, name.lower())
    actual = function(
        study,
        normal=normal,
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[name]
    assert actual.dims == study.dims
    # Only the 8-day spell is long enough (at least 6 days): 8 days in 2001.
    expected = np.zeros((3, 2, 2))
    expected[1] = 8.0
    np.testing.assert_array_equal(actual.values, expected)


@pytest.mark.parametrize(
    ("name", "variable", "direction"),
    [("TXHWD", "tasmax", "warm"), ("TNCWD", "tasmin", "cold")],
)
def test_dcsc_normal_spells_of_an_input_with_time_last(
    name: str, variable: str, direction: str
) -> None:
    study, normal = _normal_cube(direction, variable)
    function = getattr(icclim.dcsc, name.lower())
    first = function(
        study,
        normal=normal,
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[name]
    last = function(
        study.transpose("lat", "lon", "time"),
        normal=normal.transpose("lat", "lon", "time"),
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[name]
    assert last.dims == ("lat", "lon", "time")
    xr.testing.assert_allclose(last.transpose(*first.dims), first)


def _percentile_cube(variable: str, sign: float) -> xr.DataArray:
    """Random temperatures with a 9-day spell in 2002, outside the base period."""
    rng = np.random.default_rng(669)
    values = rng.normal(10.0, 2.0, (len(TIME), 2, 2))
    values[(TIME >= "2002-07-01") & (TIME <= "2002-07-09")] += sign * 15.0
    return xr.DataArray(
        values, dims=("time", "lat", "lon"), coords=COORDS, name=variable,
        attrs={"units": "degC"},
    )  # fmt: skip


@pytest.mark.parametrize(
    ("name", "variable", "sign"), [("WSDI", "tasmax", 1.0), ("CSDI", "tasmin", -1.0)]
)
def test_ecad_spell_durations_follow_the_input_dimension_order(
    name: str, variable: str, sign: float
) -> None:
    study = _percentile_cube(variable, sign)
    function = getattr(icclim, name.lower())
    options = {
        "base_period_time_range": ["2000-01-01", "2001-12-31"],
        "time_range": ["2002-01-01", "2002-12-31"],
        "bootstrap": False,
        "out_file": None,
        "completeness": "none",
        "logs_verbosity": "SILENT",
    }
    first = function(study, **options)[name]
    last = function(study.transpose("lat", "lon", "time"), **options)[name]
    assert first.dims == ("time", "lat", "lon")
    assert last.dims == ("lat", "lon", "time")
    assert (first.values >= 9).all()
    xr.testing.assert_allclose(last.transpose(*first.dims), first)
