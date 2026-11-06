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
    pytest.param(
        "CFD",
        "tn",
        "max_run",
        0,
        "<",
        marks=pytest.mark.xfail(strict=True, reason="#543"),
    ),
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


@pytest.mark.xfail(strict=True, reason="#542")
@pytest.mark.parametrize(
    ("name", "variable"), [("CSU", "tx"), ("CFD", "tn"), ("CDD", "pr"), ("CWD", "pr")]
)
def test_consecutive_outputs_keep_time_first(name: str, variable: str) -> None:
    """ECAD outputs consistently order dimensions as time then spatial axes."""
    source = make_threshold_cubes()[variable]
    actual = getattr(icclim, name.lower())(source, out_file=None, completeness="none")[
        name
    ]
    assert actual.dims == ("time", "lat", "lon")


@pytest.mark.xfail(strict=True, reason="#543")
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
