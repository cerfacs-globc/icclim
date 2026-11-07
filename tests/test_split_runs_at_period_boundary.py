"""
Runs of consecutive days that cross the boundary of an output period (issue #543).

By default a run is attributed whole to one period (``run_index``: where it starts
or where it ends). With ``split_runs_at_period_boundary=True`` the runs are cut at
the boundary of every output period.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim


@dataclass(frozen=True)
class RunIndex:
    """One of the four ECA&D indices built on max_consecutive_occurrence."""

    name: str
    variable: str
    units: str
    normal: float
    event: float
    threshold: str
    is_event: str  # how to flag the event days again, written independently


INDICES = [
    RunIndex("CDD", "pr", "mm/day", 5.0, 0.0, "< 1 mm/day", "lt1"),
    RunIndex("CWD", "pr", "mm/day", 0.0, 5.0, ">= 1 mm/day", "ge1"),
    RunIndex("CFD", "tn", "degC", 1.0, -1.0, "< 0 degC", "lt0"),
    RunIndex("CSU", "tx", "degC", 0.0, 30.0, "> 25 degC", "gt25"),
]
INDEX_IDS = [i.name for i in INDICES]

FLAGGERS = {
    "lt1": lambda v: v < 1,
    "ge1": lambda v: v >= 1,
    "lt0": lambda v: v < 0,
    "gt25": lambda v: v > 25,
}


def _longest_run(flags: np.ndarray) -> int:
    """Longest run of consecutive True values, in plain Python."""
    best = current = 0
    for flag in flags:
        current = current + 1 if flag else 0
        best = max(best, current)
    return best


def _series(index: RunIndex, start: str, end: str, event: tuple[str, str]):
    """1D daily series, with a single event window."""
    time = pd.date_range(start, end)
    values = np.where(
        (time >= event[0]) & (time <= event[1]), index.event, index.normal
    )
    return xr.DataArray(
        values,
        dims="time",
        coords={"time": time},
        name=index.variable,
        attrs={"units": index.units},
    )


def _boundary_example(index: RunIndex) -> xr.DataArray:
    """Daily 2001-2002, event from 2001-10-01 to 2002-04-30 (212 days)."""
    return _series(index, "2001-01-01", "2002-12-31", ("2001-10-01", "2002-04-30"))


def _compute(index: RunIndex, source: xr.DataArray, **kwargs) -> xr.DataArray:
    return getattr(icclim, index.name.lower())(
        source, out_file=None, completeness="none", **kwargs
    )[index.name].compute()


@pytest.mark.parametrize("index", INDICES, ids=INDEX_IDS)
class TestBoundaryExample:
    def test_default_attributes_the_run_to_the_period_where_it_starts(
        self, index: RunIndex
    ) -> None:
        source = _boundary_example(index)
        # Same values as before the option existed.
        np.testing.assert_array_equal(_compute(index, source).values, [212, 0])
        np.testing.assert_array_equal(
            _compute(index, source, split_runs_at_period_boundary=False).values,
            [212, 0],
        )

    def test_run_index_last_attributes_the_run_to_the_period_where_it_ends(
        self, index: RunIndex
    ) -> None:
        source = _boundary_example(index)
        actual = _compute(index, source, run_index="last")
        np.testing.assert_array_equal(actual.values, [0, 212])

    @pytest.mark.parametrize("run_index", ["first", "last"])
    def test_option_splits_the_run_whatever_the_run_index(
        self, index: RunIndex, run_index: str
    ) -> None:
        source = _boundary_example(index)
        actual = _compute(
            index, source, split_runs_at_period_boundary=True, run_index=run_index
        )
        # 2001-10-01 to 2001-12-31 is 92 days, 2002-01-01 to 2002-04-30 is 120 days.
        np.testing.assert_array_equal(actual.values, [92, 120])

    def test_option_matches_an_independent_computation(self, index: RunIndex) -> None:
        source = _boundary_example(index)
        flags = FLAGGERS[index.is_event](source.values)
        years = source.time.dt.year.values
        expected = [_longest_run(flags[years == year]) for year in (2001, 2002)]
        actual = _compute(index, source, split_runs_at_period_boundary=True)
        np.testing.assert_array_equal(actual.values, expected)
        assert not np.isnan(actual.values).any()


@pytest.mark.parametrize("chunk", [None, 30])
@pytest.mark.parametrize("slice_mode", ["year", "month"])
@pytest.mark.parametrize("index", INDICES, ids=INDEX_IDS)
def test_option_on_a_grid_with_runs_crossing_several_boundaries(
    index: RunIndex, slice_mode: str, chunk: int | None
) -> None:
    """
    Compare with an independent computation that splits the periods first.

    No period is NaN because a run started in the previous one.
    """
    time = pd.date_range("2000-01-01", "2003-12-31")
    windows = {
        (0, 0): [("2000-11-15", "2001-02-10"), ("2002-12-01", "2003-03-15")],
        (0, 1): [("2001-12-31", "2002-01-01")],
        (1, 0): [("2001-07-01", "2003-02-28")],  # crosses two year boundaries
        (1, 1): [],  # no event at all
    }
    values = np.full((len(time), 2, 2), index.normal)
    for (ilat, ilon), spans in windows.items():
        for start, end in spans:
            values[(time >= start) & (time <= end), ilat, ilon] = index.event
    source = xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [0.0, 1.0], "lon": [0.0, 1.0]},
        name=index.variable,
        attrs={"units": index.units},
    )
    if chunk is not None:
        source = source.chunk({"time": chunk})
    actual = _compute(
        index, source, slice_mode=slice_mode, split_runs_at_period_boundary=True
    ).transpose("time", "lat", "lon")

    flags = FLAGGERS[index.is_event](values)
    if slice_mode == "year":
        keys = time.year
        periods = sorted(set(keys))
    else:
        keys = time.year * 100 + time.month
        periods = sorted(set(keys))
    expected = np.array(
        [
            [
                [_longest_run(flags[keys == p, ilat, ilon]) for ilon in range(2)]
                for ilat in range(2)
            ]
            for p in periods
        ],
        dtype=float,
    )
    assert actual.shape == expected.shape
    assert not np.isnan(actual.values).any()
    np.testing.assert_array_equal(actual.values, expected)
    if slice_mode == "year":
        assert actual.values[1, 1, 0] == 184  # 2001-07-01 to 2001-12-31
        assert actual.values[2, 1, 0] == 365  # the whole of 2002 is inside the run
        assert actual.values[:, 1, 1].tolist() == [0, 0, 0, 0]


@pytest.mark.parametrize("split", [False, True])
@pytest.mark.parametrize("index", INDICES, ids=INDEX_IDS)
def test_generic_function_and_ecad_index_give_the_same_values(
    index: RunIndex,
    split: bool,
) -> None:
    source = _boundary_example(index)
    ecad = _compute(index, source, split_runs_at_period_boundary=split)
    generic = icclim.max_consecutive_occurrence(
        in_files=source,
        var_name=index.variable,
        threshold=index.threshold,
        slice_mode="year",
        out_file=None,
        completeness="none",
        split_runs_at_period_boundary=split,
    ).max_consecutive_occurrence.compute()
    np.testing.assert_array_equal(generic.values, ecad.values)
    np.testing.assert_array_equal(ecad.values, [92, 120] if split else [212, 0])


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("time_last", [False, True], ids=["time-first", "time-last"])
def test_dimension_order_does_not_depend_on_the_index_or_the_option(
    time_last: bool,
    chunked: bool,
) -> None:
    """
    The four indices return the same dimension order, with or without the option.

    The order itself (time is not the first dimension) is tracked in issue #542;
    this test only checks that the option does not change it.
    """
    dims_seen = {}
    for index in INDICES:
        series = _boundary_example(index)
        cube = series.expand_dims(lat=[0.0, 1.0], lon=[0.0, 1.0, 2.0], axis=(1, 2))
        cube = cube.transpose("lat", "lon", "time") if time_last else cube
        if chunked:
            cube = cube.chunk({"lat": 1})
        for split in (False, True):
            result = _compute(index, cube, split_runs_at_period_boundary=split)
            dims_seen[index.name, split] = result.dims
            expected = [92, 120] if split else [212, 0]
            np.testing.assert_array_equal(result.isel(lat=0, lon=0).values, expected)
    assert len(set(dims_seen.values())) == 1, dims_seen


@pytest.mark.parametrize("index", INDICES, ids=INDEX_IDS)
def test_date_event_with_the_option_dates_the_run_inside_each_period(
    index: RunIndex,
) -> None:
    """``event_date_end`` is the day after the last day of the run."""
    source = _boundary_example(index)
    kwargs = {"out_file": None, "completeness": "none", "date_event": True}
    default = getattr(icclim, index.name.lower())(source, **kwargs).compute()
    split = getattr(icclim, index.name.lower())(
        source, split_runs_at_period_boundary=True, **kwargs
    ).compute()

    def as_days(da: xr.DataArray) -> list[str]:
        return [str(v)[:10] for v in da.values.astype("datetime64[D]")]

    # Default: the whole run belongs to 2001, 2002 has no run.
    assert as_days(default.event_date_start)[0] == "2001-10-01"
    assert as_days(default.event_date_end)[0] == "2002-05-01"
    # With the option each period dates its own part of the run.
    assert as_days(split.event_date_start) == ["2001-10-01", "2002-01-01"]
    assert as_days(split.event_date_end) == ["2002-01-01", "2002-05-01"]
