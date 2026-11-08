"""
Dimension order of the longest-run indices (issue #542).

CDD, CWD, CFD, CSU and ``max_consecutive_occurrence`` return their dimensions in the
order of the input. With ``date_event=True`` the dates are computed per period and
``time`` stays the first dimension, whatever the order of the input.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim

# name, variable, units, value outside the event, value inside the event
INDICES = [
    ("cdd", "pr", "mm/day", 5.0, 0.0),
    ("cwd", "pr", "mm/day", 0.0, 5.0),
    ("cfd", "tn", "degC", 1.0, -1.0),
    ("csu", "tx", "degC", 0.0, 30.0),
]


def _cube(variable: str, units: str, normal: float, event: float) -> xr.DataArray:
    """Daily 2001-2002, event from 2001-10-01 to 2002-04-30, time first."""
    time = pd.date_range("2001-01-01", "2002-12-31")
    is_event = (time >= "2001-10-01") & (time <= "2002-04-30")
    values = np.where(is_event, event, normal)[:, None, None] * np.ones(
        (len(time), 2, 3)
    )
    return xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [0.0, 1.0], "lon": [0.0, 1.0, 2.0]},
        name=variable,
        attrs={"units": units},
    )


@pytest.mark.parametrize("split", [False, True], ids=["default", "split"])
@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("time_last", [False, True], ids=["time-first", "time-last"])
@pytest.mark.parametrize(("name", "variable", "units", "normal", "event"), INDICES)
def test_results_keep_the_dimension_order_of_the_input(
    name: str,
    variable: str,
    units: str,
    normal: float,
    event: float,
    time_last: bool,
    chunked: bool,
    split: bool,
) -> None:
    cube = _cube(variable, units, normal, event)
    if time_last:
        cube = cube.transpose("lat", "lon", "time")
    if chunked:
        cube = cube.chunk({"lat": 1})
    result = getattr(icclim, name)(
        cube,
        out_file=None,
        completeness="none",
        split_runs_at_period_boundary=split,
    )[name.upper()].compute()
    assert result.dims == cube.dims
    # Only the layout is concerned: the values are those of the other tests.
    expected = [92, 120] if split else [212, 0]
    np.testing.assert_array_equal(result.isel(lat=0, lon=0).values, expected)


@pytest.mark.parametrize("split", [False, True], ids=["default", "split"])
@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("time_last", [False, True], ids=["time-first", "time-last"])
@pytest.mark.parametrize(("name", "variable", "units", "normal", "event"), INDICES)
def test_dated_results_keep_time_first_whatever_the_input_order(
    name: str,
    variable: str,
    units: str,
    normal: float,
    event: float,
    time_last: bool,
    chunked: bool,
    split: bool,
) -> None:
    cube = _cube(variable, units, normal, event)
    if time_last:
        cube = cube.transpose("lat", "lon", "time")
    if chunked:
        cube = cube.chunk({"lat": 1})
    result = getattr(icclim, name)(
        cube,
        out_file=None,
        completeness="none",
        date_event=True,
        split_runs_at_period_boundary=split,
    )
    assert result[name.upper()].dims[0] == "time"
    assert result.event_date_start.dims[0] == "time"
    assert result.event_date_end.dims[0] == "time"
