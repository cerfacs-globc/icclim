"""Independent value oracles for ECAD count and fixed-threshold indices."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from tests.ecad_oracles._helpers import (
    annual_reduce,
    compound_oracle,
    make_compound_cube,
    make_threshold_cubes,
)

SIMPLE_INDICES = (
    ("SU", "tx", "count", 25, ">"),
    ("TR", "tn", "count", 20, ">"),
    ("FD", "tn", "count", 0, "<"),
    ("ID", "tx", "count", 0, "<"),
    ("CSU", "tx", "max_run", 25, ">"),
    ("CFD", "tn", "max_run", 0, "<"),
    ("GD4", "tg", "above_sum", 4, ">"),
    ("HD17", "tg", "below_sum", 17, "<"),
    ("RR1", "pr", "count", 1, ">="),
    ("R10mm", "pr", "count", 10, ">="),
    ("R20mm", "pr", "count", 20, ">="),
    ("CDD", "pr", "max_run", 1, "<"),
    ("CWD", "pr", "max_run", 1, ">="),
    ("SD", "snd", "mean", 0, "mean"),
    ("SD1", "snd", "count", 1, ">="),
    ("SD5cm", "snd", "count", 5, ">="),
    ("SD50cm", "snd", "count", 50, ">="),
)


def _simple_expected(
    source, variable: str, reducer: str, threshold: float, operator: str
):
    values = source[variable].values.copy()
    units = source[variable].attrs["units"]
    if units == "K":
        values -= 273.15
    elif units == "kg m-2 s-1":
        values *= 86400
    elif variable == "snd" and units == "m":
        values *= 100
    if reducer == "mean":
        return annual_reduce(source.time, values, "mean")
    if reducer == "above_sum":
        return annual_reduce(
            source.time, np.where(values > threshold, values - threshold, 0), "sum"
        )
    if reducer == "below_sum":
        return annual_reduce(
            source.time, np.where(values < threshold, threshold - values, 0), "sum"
        )
    comparisons = {">": np.greater, "<": np.less, ">=": np.greater_equal}
    event = comparisons[operator](values, threshold)
    return annual_reduce(
        source.time, event, "max_run" if reducer == "max_run" else "sum"
    )


@pytest.mark.parametrize("chunk", [None, 1, 7])
@pytest.mark.parametrize(
    ("name", "variable", "reducer", "threshold", "operator"), SIMPLE_INDICES
)
def test_fixed_threshold_indices(
    name: str,
    variable: str,
    reducer: str,
    threshold: float,
    operator: str,
    chunk: int | None,
) -> None:
    """Fixed thresholds use the ATBD strict/inclusive comparisons and reductions."""
    source = make_threshold_cubes(
        temperature_units="K" if chunk == 7 else "degC",
        precipitation_units="kg m-2 s-1" if chunk == 7 else "mm/day",
        snow_units="m" if chunk == 7 else "cm",
    )
    expected = _simple_expected(source, variable, reducer, threshold, operator)
    study = source[variable]
    if chunk is not None:
        study = study.chunk({"time": chunk})

    actual = getattr(icclim, name.lower())(
        study,
        out_file=None,
        completeness="none",
    )[name].compute()

    values = (
        actual.transpose("time", "lat", "lon").values
        if reducer == "max_run"
        else actual.values
    )
    np.testing.assert_allclose(values, expected, rtol=1e-10, atol=1e-10, equal_nan=True)
    if reducer != "max_run":
        assert actual.dims == ("time", "lat", "lon")
    assert actual.attrs["units"]
    assert actual.attrs["long_name"]
    assert actual.attrs["standard_name"]


@pytest.mark.parametrize("chunk", [None, 1, 7])
@pytest.mark.parametrize(
    "name",
    [
        "CD",
        "CW",
        "WD",
        "WW",
    ],
)
def test_compound_percentile_counts(name: str, chunk: int | None) -> None:
    """Compound days combine strict DOY-temperature and wet-day-rain percentiles."""
    source = make_compound_cube()
    expected = compound_oracle(source, name)
    study = source if chunk is None else source.chunk({"time": chunk})

    actual = getattr(icclim, name.lower())(
        study,
        var_name=["tg", "pr"],
        base_period_time_range=["2001-01-01", "2003-12-31"],
        bootstrap=False,
        out_file=None,
        completeness="none",
    )[name].compute()

    np.testing.assert_allclose(actual.values, expected, equal_nan=True)


@pytest.mark.parametrize(
    ("name", "variable"),
    [
        ("CSU", "tx"),
        ("CFD", "tn"),
        pytest.param("CDD", "pr", marks=pytest.mark.xfail(strict=True, reason="#542")),
        pytest.param("CWD", "pr", marks=pytest.mark.xfail(strict=True, reason="#542")),
    ],
)
def test_consecutive_outputs_keep_time_first(name: str, variable: str) -> None:
    """ECAD outputs consistently order dimensions as time then spatial axes."""
    source = make_threshold_cubes()[variable]
    actual = getattr(icclim, name.lower())(source, out_file=None, completeness="none")[
        name
    ]
    assert actual.dims == ("time", "lat", "lon")


@pytest.mark.parametrize(
    ("name", "variable", "normal", "event"),
    [("CFD", "tn", 1.0, -1.0), ("CSU", "tx", 0.0, 30.0)],
)
def test_temperature_runs_do_not_merge_across_years(
    name: str,
    variable: str,
    normal: float,
    event: float,
) -> None:
    """CFD/CSU maxima are defined within each period, unlike CDD/CWD."""
    time = pd.date_range("2001-01-01", "2002-12-31")
    values = np.full(len(time), normal)
    values[(time >= "2001-10-01") & (time <= "2002-04-30")] = event
    source = xr.DataArray(
        values,
        dims="time",
        coords={"time": time},
        name=variable,
        attrs={"units": "degC"},
    )
    actual = getattr(icclim, name.lower())(source, out_file=None, completeness="none")[
        name
    ].compute()
    np.testing.assert_array_equal(actual.values, [92, 120])


def _longest_run(flags: np.ndarray) -> int:
    """Longest run of consecutive True values, in plain Python."""
    best = current = 0
    for flag in flags:
        current = current + 1 if flag else 0
        best = max(best, current)
    return best


@pytest.mark.parametrize("chunk", [None, 30])
@pytest.mark.parametrize(
    ("name", "variable", "normal", "event", "operator_is_less"),
    [("CFD", "tn", 1.0, -1.0, True), ("CSU", "tx", 0.0, 30.0, False)],
)
def test_runs_crossing_a_year_boundary_are_split_at_the_boundary(
    name: str,
    variable: str,
    normal: float,
    event: float,
    operator_is_less: bool,
    chunk: int | None,
) -> None:
    """
    Issue #543: CFD/CSU are the longest run within each year.

    A run that crosses 31 December is cut at the boundary: each year keeps its own
    part of the run, and no year is NaN or 0 because the run started in the
    previous year.
    """
    time = pd.date_range("2000-01-01", "2003-12-31")
    # One event window (start, end) per cell, written from the definition.
    windows = {
        (0, 0): [("2000-11-15", "2001-02-10"), ("2002-12-01", "2003-03-15")],
        (0, 1): [("2001-12-31", "2002-01-01")],
        (1, 0): [("2001-07-01", "2003-02-28")],  # crosses two boundaries
        (1, 1): [],  # no event at all
    }
    values = np.full((len(time), 2, 2), normal)
    for (ilat, ilon), spans in windows.items():
        for start, end in spans:
            values[(time >= start) & (time <= end), ilat, ilon] = event
    source = xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [0.0, 1.0], "lon": [0.0, 1.0]},
        name=variable,
        attrs={"units": "degC"},
    )
    if chunk is not None:
        source = source.chunk({"time": chunk})
    actual = (
        getattr(icclim, name.lower())(source, out_file=None, completeness="none")[name]
        .transpose("time", "lat", "lon")
        .compute()
    )
    # Independent computation: split every year first, then take the longest run.
    flags = values < 0 if operator_is_less else values > 25
    years = time.year
    expected = np.array(
        [
            [
                [_longest_run(flags[years == year, ilat, ilon]) for ilon in range(2)]
                for ilat in range(2)
            ]
            for year in range(2000, 2004)
        ],
        dtype=float,
    )
    assert actual.shape == expected.shape
    assert not np.isnan(actual.values).any()
    np.testing.assert_array_equal(actual.values, expected)
    # Sanity checks on the hand-written scenario (leap years 2000 and 2004 aside).
    assert actual.values[1, 1, 0] == 184  # 2001-07-01 to 2001-12-31
    assert actual.values[2, 1, 0] == 365  # the whole of 2002 is inside the run
    assert actual.values[:, 1, 1].tolist() == [0, 0, 0, 0]
