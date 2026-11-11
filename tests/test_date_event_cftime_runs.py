"""
Dated longest runs on non-standard calendars (issue #574).

``max_consecutive_occurrence`` with ``date_event=True`` used to fail on cftime
calendars (``TypeError: operand type(s) all returned NotImplemented from
__array_ufunc__``). The dates of the ``noleap`` calendar are checked against the
standard calendar (2001 has no leap day), the dates of the other calendars against
the expected values.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim

CALENDARS = ["noleap", "360_day", "all_leap"]


def _cube(calendar: str | None, chunked: bool) -> xr.DataArray:
    if calendar == "360_day":
        time = xr.date_range(
            "2001-01-01", "2001-12-30", calendar=calendar, use_cftime=True
        )
    elif calendar is None:
        time = pd.date_range("2001-01-01", "2001-12-31")
    else:
        time = xr.date_range(
            "2001-01-01", "2001-12-31", calendar=calendar, use_cftime=True
        )
    values = np.zeros((len(time), 2))
    values[9:19, 0] = 20.0  # 10 days from 10 to 19 January
    values[40:46, 0] = 20.0  # 6 days from 10 to 15 February
    values[:, 1] = 20.0  # every day: one run per month, from its first day
    da = xr.DataArray(
        values,
        dims=("time", "x"),
        coords={"time": time, "x": [0, 1]},
        name="tasmax",
        attrs={"units": "degC"},
    )
    return da.chunk({"x": 1}) if chunked else da


def _compute(calendar: str | None, chunked: bool, run_index: str) -> xr.Dataset:
    return icclim.index(
        index_name="max_consecutive_occurrence",
        in_files=_cube(calendar, chunked),
        threshold="> 15 degC",
        slice_mode="month",
        date_event=True,
        run_index=run_index,
        out_file=None,
        completeness="none",
    ).compute()


def _dates(da: xr.DataArray) -> list[str]:
    values = da.values.ravel()
    return [
        ""
        if pd.isna(v)
        else pd.Timestamp(v).isoformat()[:10]
        if isinstance(v, np.datetime64)
        else v.isoformat()[:10]
        for v in values
    ]


@pytest.mark.parametrize("run_index", ["first", "last"])
@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("calendar", ["noleap"])
def test_dated_runs_of_a_cftime_calendar_match_the_standard_calendar(
    calendar: str, chunked: bool, run_index: str
) -> None:
    expected = _compute(None, chunked, run_index)
    actual = _compute(calendar, chunked, run_index)
    name = "max_consecutive_occurrence"
    np.testing.assert_array_equal(actual[name].values, expected[name].values)
    assert _dates(actual.event_date_start) == _dates(expected.event_date_start)
    assert _dates(actual.event_date_end) == _dates(expected.event_date_end)


@pytest.mark.parametrize("calendar", CALENDARS)
def test_dated_runs_of_a_cftime_calendar_have_the_expected_dates(calendar: str) -> None:
    result = _compute(calendar, chunked=False, run_index="first")
    name = "max_consecutive_occurrence"
    column = result.isel(x=0)
    assert column[name].values[0] == 10  # January
    assert column[name].values[1] == 6  # February
    starts = _dates(column.event_date_start)
    assert starts[0] == "2001-01-10"
    # Day 41 of the year: February 10th, or February 11th with 30-day months.
    assert starts[1] == ("2001-02-11" if calendar == "360_day" else "2001-02-10")
    # A period without any run has no dates.
    assert starts[2] == ""
