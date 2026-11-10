"""Independent value oracles for ECA&D indices."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from scipy.stats import gamma, norm

import icclim

Reducer = Literal["mean", "max", "min", "fd", "su", "dtr"]


@dataclass(frozen=True)
class IndexCase:
    name: str
    variables: tuple[str, ...]
    reducer: Reducer


CASES = (
    IndexCase("TG", ("tas",), "mean"),
    IndexCase("TN", ("tasmin",), "mean"),
    IndexCase("TX", ("tasmax",), "mean"),
    IndexCase("TXx", ("tasmax",), "max"),
    IndexCase("TNn", ("tasmin",), "min"),
    IndexCase("DTR", ("tasmax", "tasmin"), "dtr"),
    IndexCase("FD", ("tasmin",), "fd"),
    IndexCase("SU", ("tasmax",), "su"),
)


def _temperature_cube() -> xr.Dataset:
    """Return three deterministic daily years with gaps and boundary probes."""
    time = pd.date_range("2001-01-01", "2003-12-31", freq="D")
    time = time[time != pd.Timestamp("2002-06-15")]
    rng = np.random.default_rng(20261109)
    seasonal = 11 + 12 * np.sin(2 * np.pi * (time.day_of_year.to_numpy() - 80) / 365.25)
    tas = seasonal[:, None, None] + rng.normal(0, 1.5, (len(time), 2, 2))
    tas += np.array([[-2.0, 0.0], [1.5, 3.0]])[None, :, :]
    tasmin = tas - 5 - rng.uniform(0, 2, tas.shape)
    tasmax = tas + 5 + rng.uniform(0, 2, tas.shape)

    # The warm/frost events cross year boundaries; later run-index batches use
    # the same edge case, while this batch independently checks annual counts.
    boundary = ((time.month == 12) & (time.day >= 29)) | (
        (time.month == 1) & (time.day <= 3)
    )
    tasmax[boundary, 0, 0] = 30
    tasmin[boundary, 1, 0] = -3

    # ATBD v11 section 5, SU and FD: SU is TX > 25 C and FD is TN < 0 C.
    # Values equal to either threshold must therefore not be counted.
    tasmax[(time.month == 7) & (time.day == 15), 0, 1] = 25
    tasmin[(time.month == 1) & (time.day == 15), 0, 1] = 0

    tas[(time.year == 2001) & (time.month == 4) & (time.day == 10), 1, 0] = np.nan
    tasmin[(time.year == 2002) & (time.month == 8) & (time.day == 20), 0, 0] = np.nan
    tasmax[(time.year == 2003) & (time.month == 9) & (time.day == 5), 1, 1] = np.nan

    coordinates = {"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]}
    return xr.Dataset(
        {
            name: xr.DataArray(
                values,
                dims=("time", "lat", "lon"),
                attrs={"units": "degC"},
            )
            for name, values in {"tas": tas, "tasmin": tasmin, "tasmax": tasmax}.items()
        },
        coords=coordinates,
    )


def _annual_oracle(source: xr.Dataset, case: IndexCase) -> np.ndarray:
    """Apply the ATBD annual reduction using only numpy and pandas."""
    years = pd.DatetimeIndex(source.time.values).year
    results = []
    for year in np.unique(years):
        selected = years == year
        values = source[case.variables[0]].values[selected]
        if case.reducer == "mean":
            result = np.nanmean(values, axis=0)
        elif case.reducer == "max":
            result = np.nanmax(values, axis=0)
        elif case.reducer == "min":
            result = np.nanmin(values, axis=0)
        elif case.reducer == "dtr":
            minimum = source[case.variables[1]].values[selected]
            result = np.nanmean(values - minimum, axis=0)
        elif case.reducer == "fd":
            result = np.sum(np.isfinite(values) & (values < 0), axis=0)
        else:
            result = np.sum(np.isfinite(values) & (values > 25), axis=0)
        results.append(result)
    return np.stack(results)


@pytest.mark.parametrize("chunk_size", [None, 7], ids=["eager", "chunked"])
@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_basic_temperature_indices_match_atbd_oracle(
    case: IndexCase,
    chunk_size: int | None,
) -> None:
    """Compare annual temperature basics with direct ATBD reductions."""
    source = _temperature_cube()
    expected = _annual_oracle(source, case)
    study = source[list(case.variables)]
    if chunk_size is not None:
        study = study.chunk({"time": chunk_size})

    actual = icclim.index(
        in_files=study,
        var_name=list(case.variables),
        index_name=case.name,
        slice_mode="year",
        out_file=None,
        completeness="none",
    )[case.name].compute()

    np.testing.assert_allclose(actual.values, expected, equal_nan=True)


@dataclass(frozen=True)
class Batch2Case:
    name: str
    variable: str
    reducer: Literal["count", "sdii", "run"]
    threshold: float
    operator: Literal[">", "<", ">="]
    units: str


BATCH2_CASES = (
    Batch2Case("TR", "tasmin", "count", 20, ">", "K"),
    Batch2Case("ID", "tasmax", "count", 0, "<", "K"),
    Batch2Case("CSU", "tasmax", "run", 25, ">", "degC"),
    Batch2Case("CFD", "tasmin", "run", 0, "<", "degC"),
    Batch2Case("CDD", "pr", "run", 1, "<", "mm/day"),
    Batch2Case("CWD", "pr", "run", 1, ">=", "mm/day"),
    Batch2Case("RR1", "pr", "count", 1, ">=", "kg m-2 s-1"),
    Batch2Case("SDII", "pr", "sdii", 1, ">=", "kg m-2 s-1"),
)

RUN_OPTIONS = (("first", False), ("last", False), ("first", True), ("last", True))


def _batch2_values(case: Batch2Case) -> xr.DataArray:
    """Create three daily years including leap day and exact thresholds."""
    time = pd.date_range("1999-01-01", "2001-12-31", freq="D")
    rng = np.random.default_rng(20261110)
    shape = (len(time), 2, 2)
    if case.reducer == "run":
        non_event = {"CSU": 20.0, "CFD": 5.0, "CDD": 2.0, "CWD": 0.0}
        event_value = {"CSU": 30.0, "CFD": -5.0, "CDD": 0.0, "CWD": 2.0}
        values = np.full(shape, non_event[case.name])
        crossing = ((time.year == 1999) & (time.day_of_year >= 362)) | (
            (time.year == 2000) & (time.day_of_year <= 4)
        )
        values[crossing] = event_value[case.name]
        values[(time.year == 2001) & (time.month == 6) & (time.day <= 3), 0, 1] = (
            event_value[case.name]
        )
        values[(time.year == 2000) & (time.month == 8) & (time.day == 8), 1, 1] = np.nan
    elif case.variable == "pr":
        values = rng.gamma(1.8, 2.2, shape)
        values[np.arange(len(time)) % 9 == 0] = 0.4
        values[(time.month == 2) & (time.day == 29)] = 1.0
        values[(time.year == 2001) & (time.month == 5) & (time.day == 5), 1, 0] = np.nan
        values /= 86400
    else:
        center = 18.0 if case.name == "TR" else 2.0
        values = rng.normal(center, 6.0, shape)
        exact = (time.month == 2) & (time.day == 29)
        values[exact] = case.threshold
        values[(time.year == 2001) & (time.month == 5) & (time.day == 5), 0, 1] = np.nan
        values += 273.15
    return xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]},
        name=case.variable,
        attrs={"units": case.units},
    )


def _compare(values: np.ndarray, operator: str, threshold: float) -> np.ndarray:
    finite = np.isfinite(values)
    if operator == ">":
        return finite & (values > threshold)
    if operator == "<":
        return finite & (values < threshold)
    return finite & (values >= threshold)


def _longest_run(events: np.ndarray) -> np.ndarray:
    longest = np.zeros(events.shape[1:], dtype=int)
    current = np.zeros(events.shape[1:], dtype=int)
    for daily in events:
        current = np.where(daily, current + 1, 0)
        longest = np.maximum(longest, current)
    return longest


def _run_oracle(
    time: pd.DatetimeIndex,
    events: np.ndarray,
    run_index: str,
    split: bool,
) -> np.ndarray:
    """Compute annual maxima, optionally splitting runs at year boundaries.

    ATBD v11 section 5.1 assigns an unsplit run to the period containing its
    ending day (``run_index="last"``). Both supported attribution choices are
    tested here without changing the library default.
    """
    years = np.unique(time.year)
    if split:
        return np.stack([_longest_run(events[time.year == year]) for year in years])

    result = np.zeros((len(years), *events.shape[1:]), dtype=int)
    for cell in np.ndindex(events.shape[1:]):
        start = None
        series = events[(slice(None), *cell)]
        for position, event in enumerate(np.append(series, False)):
            if event and start is None:
                start = position
            elif not event and start is not None:
                end = position - 1
                anchor = start if run_index == "first" else end
                year_index = int(np.flatnonzero(years == time[anchor].year)[0])
                result[(year_index, *cell)] = max(
                    result[(year_index, *cell)], position - start
                )
                start = None
    return result


def _batch2_oracle(
    source: xr.DataArray,
    case: Batch2Case,
    run_index: str,
    split: bool,
) -> np.ndarray:
    time = pd.DatetimeIndex(source.time.values)
    values = source.values.copy()
    if case.units == "K":
        values -= 273.15
    elif case.units == "kg m-2 s-1":
        values *= 86400
    events = _compare(values, case.operator, case.threshold)
    if case.reducer == "run":
        return _run_oracle(time, events, run_index, split)

    results = []
    for year in np.unique(time.year):
        annual = time.year == year
        if case.reducer == "count":
            results.append(np.sum(events[annual], axis=0))
        else:
            wet_amount = np.where(events[annual], values[annual], 0)
            results.append(np.sum(wet_amount, axis=0) / np.sum(events[annual], axis=0))
    return np.stack(results)


BATCH2_PARAMETERS = tuple(
    (case, run_index, split)
    for case in BATCH2_CASES
    for run_index, split in (
        RUN_OPTIONS if case.reducer == "run" else (("first", False),)
    )
)


@pytest.mark.parametrize("chunk_size", [None, 7], ids=["eager", "chunked"])
@pytest.mark.parametrize(
    ("case", "run_index", "split"),
    BATCH2_PARAMETERS,
    ids=lambda value: value.name if isinstance(value, Batch2Case) else str(value),
)
def test_batch2_indices_match_atbd_oracle(
    case: Batch2Case,
    run_index: str,
    split: bool,
    chunk_size: int | None,
) -> None:
    """Compare threshold counts, spell maxima, and SDII with ATBD oracles."""
    source = _batch2_values(case)
    assert pd.Timestamp("2000-02-29") in pd.DatetimeIndex(source.time.values)
    expected = _batch2_oracle(source, case, run_index, split)
    study = source if chunk_size is None else source.chunk({"time": chunk_size})

    kwargs = {}
    if case.reducer == "run":
        kwargs = {
            "run_index": run_index,
            "split_runs_at_period_boundary": split,
        }
    actual = getattr(icclim, case.name.lower())(
        study,
        out_file=None,
        completeness="none",
        **kwargs,
    )[case.name].compute()

    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        expected,
        equal_nan=True,
    )


@dataclass(frozen=True)
class Batch3Case:
    name: str
    variables: tuple[str, ...]
    reducer: Literal["max", "min", "etr", "vdtr", "gd4", "hd17", "r10", "rx1"]


BATCH3_CASES = (
    Batch3Case("TNx", ("tasmin",), "max"),
    Batch3Case("TXn", ("tasmax",), "min"),
    Batch3Case("ETR", ("tasmax", "tasmin"), "etr"),
    Batch3Case("vDTR", ("tasmax", "tasmin"), "vdtr"),
    Batch3Case("GD4", ("tas",), "gd4"),
    Batch3Case("HD17", ("tas",), "hd17"),
    Batch3Case("R10mm", ("pr",), "r10"),
    Batch3Case("RX1day", ("pr",), "rx1"),
)


def _batch3_cube() -> xr.Dataset:
    """Return three deterministic daily years in Kelvin and precipitation flux."""
    time = pd.date_range("1999-01-01", "2001-12-31", freq="D")
    rng = np.random.default_rng(20261111)
    shape = (len(time), 2, 2)
    seasonal = 10 + 11 * np.sin(2 * np.pi * (time.day_of_year.to_numpy() - 80) / 365.25)
    tas = seasonal[:, None, None] + rng.normal(0, 1.4, shape)
    tas += np.array([[-2.0, 0.0], [1.5, 3.0]])[None, :, :]
    tasmin = tas - 5 - rng.uniform(0, 1.5, shape)
    tasmax = tas + 5 + rng.uniform(0, 1.5, shape)
    precipitation = rng.gamma(1.7, 4.0, shape)

    # ATBD v11 sections 5.3.2 and 5.3.5: values at the GD4/HD17 bases
    # contribute zero; only TG > 4 C contributes to GD4 and only TG < 17 C
    # contributes to HD17.
    tas[time == "2000-02-27", 0, 0] = 4
    tas[time == "2000-02-28", 0, 0] = 5
    tas[time == "2000-02-29", 0, 0] = 3
    tas[time == "2000-03-01", 0, 1] = 17
    tas[time == "2000-03-02", 0, 1] = 18
    tas[time == "2000-03-03", 0, 1] = 16

    # ATBD v11 section 5.3.8 defines R10mm as RR >= 10 mm, so equality
    # counts. The second value makes the annual maximum independently visible.
    precipitation[time == "2000-07-01", 1, 0] = 10
    precipitation[time == "2000-07-02", 1, 0] = 23

    tas[time == "1999-05-10", 1, 1] = np.nan
    tasmin[time == "2000-08-20", 0, 0] = np.nan
    tasmax[time == "2001-09-05", 1, 0] = np.nan
    precipitation[time == "2001-04-12", 0, 1] = np.nan

    coords = {"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]}
    return xr.Dataset(
        {
            "tas": xr.DataArray(
                tas + 273.15,
                dims=("time", "lat", "lon"),
                attrs={"units": "K"},
            ),
            "tasmin": xr.DataArray(
                tasmin + 273.15,
                dims=("time", "lat", "lon"),
                attrs={"units": "K"},
            ),
            "tasmax": xr.DataArray(
                tasmax + 273.15,
                dims=("time", "lat", "lon"),
                attrs={"units": "K"},
            ),
            "pr": xr.DataArray(
                precipitation / 86400,
                dims=("time", "lat", "lon"),
                attrs={"units": "kg m-2 s-1"},
            ),
        },
        coords=coords,
    )


def _batch3_annual_reduce(
    selected: np.ndarray,
    second: np.ndarray | None,
    reducer: str,
) -> np.ndarray:
    if reducer == "max":
        result = np.nanmax(selected, axis=0)
    elif reducer == "min":
        result = np.nanmin(selected, axis=0)
    elif reducer == "etr":
        result = np.nanmax(selected, axis=0) - np.nanmin(second, axis=0)
    elif reducer == "vdtr":
        daily_range = selected - second
        result = np.nanmean(np.abs(np.diff(daily_range, axis=0)), axis=0)
    elif reducer == "gd4":
        result = np.nansum(np.where(selected > 4, selected - 4, 0), axis=0)
    elif reducer == "hd17":
        result = np.nansum(np.where(selected < 17, 17 - selected, 0), axis=0)
    elif reducer == "r10":
        result = np.sum(np.isfinite(selected) & (selected >= 10), axis=0)
    else:
        result = np.nanmax(selected, axis=0)
    return result


def _batch3_oracle(source: xr.Dataset, case: Batch3Case) -> np.ndarray:
    """Apply the ATBD v11 sections 5.3.2, 5.3.5, 5.3.8 and 5.3.11."""
    time = pd.DatetimeIndex(source.time.values)
    values = source[case.variables[0]].values.copy()
    if case.variables[0] == "pr":
        values *= 86400
    else:
        values -= 273.15
    second = None
    if len(case.variables) == 2:
        second = source[case.variables[1]].values - 273.15

    results = []
    for year in np.unique(time.year):
        annual = time.year == year
        annual_second = None if second is None else second[annual]
        results.append(
            _batch3_annual_reduce(values[annual], annual_second, case.reducer)
        )
    return np.stack(results)


@pytest.mark.parametrize("chunk_size", [None, 7], ids=["eager", "chunked"])
@pytest.mark.parametrize("case", BATCH3_CASES, ids=lambda case: case.name)
def test_batch3_indices_match_atbd_oracle(
    case: Batch3Case,
    chunk_size: int | None,
) -> None:
    """Compare Batch 3 temperature and precipitation indices with the ATBD."""
    source = _batch3_cube()
    expected = _batch3_oracle(source, case)
    study = source[list(case.variables)]
    if chunk_size is not None:
        study = study.chunk({"time": chunk_size})

    actual = icclim.index(
        in_files=study,
        var_name=list(case.variables),
        index_name=case.name,
        slice_mode="year",
        out_file=None,
        completeness="none",
    )[case.name].compute()

    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        expected,
        equal_nan=True,
    )


def _vdtr_period_oracle(source: xr.Dataset, period: str) -> np.ndarray:
    """Average valid DTR differences within each requested period."""
    time = pd.DatetimeIndex(source.time.values)
    daily_range = source.tasmax.values - source.tasmin.values
    if period == "month":
        labels = time.to_period("M")
        groups = [labels == label for label in labels.unique()]
    else:
        autumn = np.isin(time.month, [9, 10, 11])
        groups = [autumn & (time.year == year) for year in np.unique(time.year)]
    return np.stack(
        [
            np.nanmean(np.abs(np.diff(daily_range[group], axis=0)), axis=0)
            for group in groups
        ]
    )


@pytest.mark.parametrize("chunk_size", [None, 7], ids=["eager", "chunked"])
@pytest.mark.parametrize("slice_mode", ["month", "SON"])
def test_vdtr_excludes_monthly_and_seasonal_boundary_differences(
    slice_mode: str,
    chunk_size: int | None,
) -> None:
    """ATBD v11 section 5.3.11 starts each period's differences at i=2."""
    source = _batch3_cube()[["tasmax", "tasmin"]]
    expected = _vdtr_period_oracle(source, slice_mode.lower())
    study = source if chunk_size is None else source.chunk({"time": chunk_size})

    actual = icclim.vdtr(
        study,
        slice_mode=slice_mode,
        out_file=None,
        completeness="none",
    ).vDTR.compute()

    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        expected,
        equal_nan=True,
    )


@pytest.mark.parametrize("chunk_size", [None, 7], ids=["eager", "chunked"])
def test_vdtr_keeps_minimum_valid_fraction_handling(
    chunk_size: int | None,
) -> None:
    """The existing minimum-valid-days mask still applies after reduction."""
    source = _batch3_cube()[["tasmax", "tasmin"]].sel(
        time=slice("2001-01-01", "2001-02-28")
    )
    source["tasmax"].loc[
        {"time": slice("2001-01-01", "2001-01-05"), "lat": 45.0, "lon": 1.0}
    ] = np.nan
    study = source if chunk_size is None else source.chunk({"time": chunk_size})

    actual = icclim.vdtr(
        study,
        slice_mode="month",
        out_file=None,
        completeness=0.9,
    ).vDTR.compute()

    assert np.isnan(actual.isel(time=0).sel(lat=45.0, lon=1.0))
    assert np.isfinite(actual.isel(time=1).sel(lat=45.0, lon=1.0))


@dataclass(frozen=True)
class Batch4Case:
    name: str
    variable: str
    reducer: Literal["rolling5", "wet_sum", "count", "mean", "sum"]
    threshold: float | None = None


BATCH4_CASES = (
    Batch4Case("RX5day", "pr", "rolling5"),
    Batch4Case("PRCPTOT", "pr", "wet_sum", 1),
    Batch4Case("R20mm", "pr", "count", 20),
    Batch4Case("SD", "snd", "mean"),
    Batch4Case("SD1", "snd", "count", 1),
    Batch4Case("SD5cm", "snd", "count", 5),
    Batch4Case("SD50cm", "snd", "count", 50),
    Batch4Case("RR", "pr", "sum"),
)


def _batch4_cube() -> xr.Dataset:
    """Return precipitation flux and snow depth with ATBD boundary probes."""
    time = pd.date_range("1999-01-01", "2001-12-31", freq="D")
    rng = np.random.default_rng(20261112)
    shape = (len(time), 2, 2)
    precipitation = rng.uniform(0.0, 2.0, shape)
    snow_depth = rng.uniform(0.0, 60.0, shape)

    # ATBD v11 section 5.3.8 defines a five-day interval's period by its
    # final day. This 50 mm window ends on 2000-01-03 and belongs to 2000.
    crossing = (time >= "1999-12-30") & (time <= "2000-01-03")
    precipitation[crossing, 0, 0] = 10
    precipitation[time == "2000-06-10", 0, 1] = 1
    precipitation[time == "2000-06-11", 0, 1] = 20

    # ATBD v11 section 5.3.9 uses non-strict snow thresholds.
    snow_depth[time == "2000-02-27", 1, 0] = 1
    snow_depth[time == "2000-02-28", 1, 0] = 5
    snow_depth[time == "2000-02-29", 1, 0] = 50

    precipitation[time == "2001-04-12", 1, 1] = np.nan
    snow_depth[time == "1999-11-08", 0, 1] = np.nan
    coords = {"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]}
    return xr.Dataset(
        {
            "pr": xr.DataArray(
                precipitation / 86400,
                dims=("time", "lat", "lon"),
                attrs={"units": "kg m-2 s-1"},
            ),
            "snd": xr.DataArray(
                snow_depth / 100,
                dims=("time", "lat", "lon"),
                attrs={"units": "m"},
            ),
        },
        coords=coords,
    )


def _rolling_five_day_sum(values: np.ndarray) -> np.ndarray:
    rolling = np.full(values.shape, np.nan)
    for end in range(4, len(values)):
        window = values[end - 4 : end + 1]
        rolling[end] = np.where(
            np.all(np.isfinite(window), axis=0),
            np.sum(window, axis=0),
            np.nan,
        )
    return rolling


def _batch4_oracle(source: xr.Dataset, case: Batch4Case) -> np.ndarray:
    """Apply ATBD v11 sections 5.3.8 and 5.3.9 using numpy and pandas."""
    time = pd.DatetimeIndex(source.time.values)
    values = source[case.variable].values.copy()
    values *= 86400 if case.variable == "pr" else 100
    if case.reducer == "rolling5":
        values = _rolling_five_day_sum(values)

    results = []
    for year in np.unique(time.year):
        selected = values[time.year == year]
        if case.reducer == "mean":
            result = np.nanmean(selected, axis=0)
        elif case.reducer == "count":
            result = np.sum(
                np.isfinite(selected) & (selected >= case.threshold), axis=0
            )
        elif case.reducer == "wet_sum":
            result = np.nansum(np.where(selected >= 1, selected, 0), axis=0)
        elif case.reducer == "sum":
            result = np.nansum(selected, axis=0)
        else:
            result = np.nanmax(selected, axis=0)
        results.append(result)
    return np.stack(results)


@pytest.mark.parametrize("chunk_size", [None, 7], ids=["eager", "chunked"])
@pytest.mark.parametrize("case", BATCH4_CASES, ids=lambda case: case.name)
def test_batch4_indices_match_atbd_oracle(
    case: Batch4Case,
    chunk_size: int | None,
) -> None:
    """Compare precipitation and snow indices with direct ATBD reductions."""
    source = _batch4_cube()
    expected = _batch4_oracle(source, case)
    if case.name == "RX5day":
        assert expected[1, 0, 0] == 50
    study = source[[case.variable]]
    if chunk_size is not None:
        study = study.chunk({"time": chunk_size})

    actual = icclim.index(
        in_files=study,
        var_name=case.variable,
        index_name=case.name,
        slice_mode="year",
        out_file=None,
        completeness="none",
    )[case.name].compute()

    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        expected,
        equal_nan=True,
    )


def _first_six_day_run(mask: np.ndarray) -> int | None:
    run = 0
    for index, value in enumerate(mask):
        run = run + 1 if value else 0
        if run == 6:
            return index - 5
    return None


def _batch5_gsl_cube() -> xr.DataArray:
    """Create GSL seasons probing strict thresholds and the July 1 split."""
    time = pd.date_range("1999-01-01", "2001-12-31", freq="D")
    values = np.zeros((len(time), 2, 2), dtype=float)
    month, day = time.month.to_numpy(), time.day.to_numpy()
    march_to_october = ((month > 3) | ((month == 3) & (day >= 1))) & (
        (month < 10) | ((month == 10) & (day < 1))
    )
    values[march_to_october, 0, 0] = 10

    january_to_october = ((month > 1) | ((month == 1) & (day >= 10))) & (
        (month < 10) | ((month == 10) & (day < 1))
    )
    values[january_to_october, 0, 1] = 10
    values[(month == 7) & (day <= 6), 0, 1] = 0

    january_to_july = ((month > 1) | ((month == 1) & (day >= 10))) & (
        (month < 7) | ((month == 7) & (day <= 1))
    )
    values[january_to_july, 1, 0] = 10
    values[:, 1, 1] = np.nan
    values[(month == 1) & (day <= 6), 0, 0] = 5
    values[(time.year == 2000) & (month == 6) & (day == 15), 0, 0] = np.nan
    return xr.DataArray(
        values + 273.15,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]},
        name="tas",
        attrs={"units": "K"},
    )


def _gsl_oracle(source: xr.DataArray) -> np.ndarray:
    """Implement the ATBD v11 section 5.3.2 GSL definition directly."""
    time = pd.DatetimeIndex(source.time.values)
    values = source.values - 273.15
    years = np.unique(time.year)
    result = np.full((len(years), *values.shape[1:]), np.nan)
    for year_index, year in enumerate(years):
        annual = time.year == year
        # ATBD v11 says "after 1 July", which is ambiguous. climdex.pcic's
        # growing.season.length searches temp.data[ts.mid:ts.len], with ts.mid
        # equal to July 1, so the established convention is inclusive.
        on_or_after_july_1 = (time.month > 7) | ((time.month == 7) & (time.day >= 1))
        for cell in np.ndindex(values.shape[1:]):
            series = values[(annual, *cell)]
            start = _first_six_day_run(np.isfinite(series) & (series > 5))
            end = _first_six_day_run(
                np.isfinite(series) & (series < 5) & on_or_after_july_1[annual]
            )
            if start is not None and end is not None and end >= start:
                result[(year_index, *cell)] = end - start
    return result


@pytest.mark.parametrize("chunk_size", [None, 7], ids=["eager", "chunked"])
def test_gsl_matches_atbd_start_end_and_july_split(
    chunk_size: int | None,
) -> None:
    """GSL starts above 5 C and ends below 5 C from July 1 inclusively."""
    source = _batch5_gsl_cube()
    expected = _gsl_oracle(source)
    study = source if chunk_size is None else source.chunk({"time": chunk_size})

    actual = icclim.gsl(
        study,
        out_file=None,
        completeness="none",
    ).GSL.compute()

    np.testing.assert_allclose(actual.values, expected, equal_nan=True)


def _batch5_spi_cube() -> xr.DataArray:
    """Create 40 deterministic years for stable month-wise gamma fits."""
    time = pd.date_range("1981-01-01", "2020-12-31", freq="D")
    rng = np.random.default_rng(20261113)
    values = rng.gamma(shape=2.5, scale=1.7, size=(len(time), 2, 2))
    day_of_year = time.strftime("%j").astype(int).to_numpy()
    seasonal = 1 + 0.35 * np.sin(2 * np.pi * (day_of_year - 20) / 365.25)
    values *= seasonal[:, None, None]
    values *= np.array([[0.7, 1.0], [1.3, 1.8]])[None, :, :]
    return xr.DataArray(
        values / 86400,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]},
        name="pr",
        attrs={"units": "kg m-2 s-1"},
    )


def _spi_gamma_oracle(source: xr.DataArray, window: int) -> np.ndarray:
    """Fit xclim's APP gamma parameters independently for each ending month."""
    daily = source.values * 86400
    daily_index = pd.DatetimeIndex(source.time.values)
    monthly_index = daily_index.to_period("M").to_timestamp()
    months = monthly_index.unique()
    calibration = (months >= "1981-01-01") & (months <= "2010-12-01")
    result = np.full((len(months), *daily.shape[1:]), np.nan)
    for cell in np.ndindex(daily.shape[1:]):
        series = pd.Series(daily[(slice(None), *cell)], index=daily_index)
        # xclim first forms monthly means and then rolling means. The rolling
        # value is attributed to its ending month.
        accumulated = series.resample("MS").mean().rolling(window).mean()
        for ending_month in range(1, 13):
            selected = months.month == ending_month
            sample = accumulated[calibration & selected].dropna().to_numpy()
            probability_of_zero = np.count_nonzero(sample == 0) / len(sample)
            positive = sample[sample > 0]
            mean = positive.mean()
            a = np.log(mean) - np.log(positive).mean()
            shape = (1 + np.sqrt(1 + 4 * a / 3)) / (4 * a)
            scale = mean / shape
            probability = gamma.cdf(accumulated[selected], shape, loc=0, scale=scale)
            probability = probability_of_zero + (1 - probability_of_zero) * probability
            result[(selected, *cell)] = norm.ppf(probability)
    return result


@pytest.mark.parametrize("chunk_size", [None, 7], ids=["eager", "chunked"])
@pytest.mark.parametrize(("name", "window"), [("SPI3", 3), ("SPI6", 6)])
def test_spi_matches_independent_app_gamma_value_oracle(
    name: str,
    window: int,
    chunk_size: int | None,
) -> None:
    """Compare SPI values with an independent APP gamma and zero-mass fit."""
    source = _batch5_spi_cube()
    expected = _spi_gamma_oracle(source, window)
    study = source if chunk_size is None else source.chunk({"time": chunk_size})

    actual = getattr(icclim, name.lower())(
        study,
        base_period_time_range=["1981-01-01", "2010-12-31"],
        out_file=None,
    )[name].compute()

    assert np.isnan(actual.values[: window - 1]).all()
    assert np.isfinite(actual.values[window - 1]).all()
    np.testing.assert_allclose(
        actual.values, expected, atol=1e-10, rtol=0, equal_nan=True
    )


@dataclass(frozen=True)
class Batch5BasicCase:
    name: str
    variable: str
    reducer: Literal["max", "mean", "sum", "ge", "le"]
    threshold: float | None = None


BATCH5_BASIC_CASES = (
    Batch5BasicCase("FXx", "wind_gust", "max"),
    Batch5BasicCase("FG6Bft", "wind", "ge", 10.8),
    Batch5BasicCase("FGcalm", "wind", "le", 2),
    Batch5BasicCase("FG", "wind", "mean"),
    Batch5BasicCase("SS", "sunshine", "sum"),
)


def _batch5_basic_cube() -> xr.Dataset:
    """Create wind and sunshine inputs with conversion and equality probes."""
    time = pd.date_range("1999-01-01", "2001-12-31", freq="D")
    rng = np.random.default_rng(20261114)
    shape = (len(time), 2, 2)
    wind = rng.uniform(0, 15, shape)
    gust = wind + rng.uniform(2, 10, shape)
    sunshine = rng.uniform(0, 12, shape)
    wind[time == "2000-02-28", 0, 0] = 10.8
    wind[time == "2000-02-29", 0, 1] = 2
    wind[time == "2001-04-12", 1, 0] = np.nan
    sunshine[time == "1999-08-03", 1, 1] = np.nan
    coords = {"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]}
    return xr.Dataset(
        {
            "wind": xr.DataArray(
                wind * 3.6,
                dims=("time", "lat", "lon"),
                attrs={"units": "km h-1"},
            ),
            "wind_gust": xr.DataArray(
                gust * 3.6,
                dims=("time", "lat", "lon"),
                attrs={"units": "km h-1"},
            ),
            "sunshine": xr.DataArray(
                sunshine * 3600,
                dims=("time", "lat", "lon"),
                attrs={"units": "s"},
            ),
        },
        coords=coords,
    )


def _batch5_basic_oracle(source: xr.Dataset, case: Batch5BasicCase) -> np.ndarray:
    """Apply ATBD v11 sections 5.3.10 and 5.3.12 reductions."""
    time = pd.DatetimeIndex(source.time.values)
    values = source[case.variable].values.copy()
    values /= 3600 if case.variable == "sunshine" else 3.6
    results = []
    for year in np.unique(time.year):
        selected = values[time.year == year]
        if case.reducer == "max":
            result = np.nanmax(selected, axis=0)
        elif case.reducer == "mean":
            result = np.nanmean(selected, axis=0)
        elif case.reducer == "sum":
            result = np.nansum(selected, axis=0)
        elif case.reducer == "ge":
            result = np.sum(
                np.isfinite(selected) & (selected >= case.threshold), axis=0
            )
        else:
            result = np.sum(
                np.isfinite(selected) & (selected <= case.threshold), axis=0
            )
        results.append(result)
    return np.stack(results)


@pytest.mark.parametrize("chunk_size", [None, 7], ids=["eager", "chunked"])
@pytest.mark.parametrize("case", BATCH5_BASIC_CASES, ids=lambda case: case.name)
def test_batch5_basic_indices_match_atbd_oracle(
    case: Batch5BasicCase,
    chunk_size: int | None,
) -> None:
    """Compare wind and sunshine indices with direct ATBD reductions."""
    source = _batch5_basic_cube()
    expected = _batch5_basic_oracle(source, case)
    study = source[[case.variable]]
    if chunk_size is not None:
        study = study.chunk({"time": chunk_size})

    actual = icclim.index(
        in_files=study,
        var_name=case.variable,
        index_name=case.name,
        slice_mode="year",
        out_file=None,
        completeness="none",
    )[case.name].compute()

    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        expected,
        equal_nan=True,
    )


@dataclass(frozen=True)
class Batch6Case:
    name: str
    variable: str
    reducer: Literal[
        "mean_pressure", "mean_humidity", "north", "east", "south", "west"
    ]


BATCH6_CASES = (
    Batch6Case("PP", "psl", "mean_pressure"),
    Batch6Case("DDnorth", "dd", "north"),
    Batch6Case("DDeast", "dd", "east"),
    Batch6Case("DDsouth", "dd", "south"),
    Batch6Case("DDwest", "dd", "west"),
    Batch6Case("RH", "hurs", "mean_humidity"),
)


def _batch6_cube() -> xr.Dataset:
    """Return pressure, humidity, and wind direction with boundary probes."""
    time = pd.date_range("1999-01-01", "2001-12-31", freq="D")
    rng = np.random.default_rng(20261110)
    shape = (len(time), 2, 2)
    pressure_hpa = rng.uniform(970, 1040, shape)
    humidity_percent = rng.uniform(15, 100, shape)
    direction = rng.uniform(0, 360, shape)

    # ATBD v11 section 5.3.12 assigns each shared edge to the clockwise
    # sector: north is -45 < DD <= 45, east 45 < DD <= 135, south
    # 135 < DD <= 225, and west 225 < DD <= 315. For 0..360 degree input,
    # north therefore wraps around as DD > 315 or DD <= 45.
    probes = np.array([0, 45, 45.01, 135, 135.01, 225, 225.01, 315, 315.01, 360])
    direction[: len(probes), 0, 0] = probes

    pressure_hpa[time == "2000-02-29", 0, 1] = 1000
    humidity_percent[time == "2000-02-29", 1, 0] = 100
    pressure_hpa[time == "2001-05-04", 1, 1] = np.nan
    humidity_percent[time == "1999-08-12", 0, 1] = np.nan
    direction[time == "2000-09-23", 1, 0] = np.nan

    coords = {"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]}
    return xr.Dataset(
        {
            "psl": xr.DataArray(
                pressure_hpa * 100,
                dims=("time", "lat", "lon"),
                attrs={"units": "Pa"},
            ),
            "hurs": xr.DataArray(
                humidity_percent / 100,
                dims=("time", "lat", "lon"),
                attrs={"units": "1"},
            ),
            "dd": xr.DataArray(
                direction,
                dims=("time", "lat", "lon"),
                attrs={"units": "degree"},
            ),
        },
        coords=coords,
    )


def _batch6_oracle(source: xr.Dataset, case: Batch6Case) -> np.ndarray:
    """Apply ATBD v11 sections 5.3.6, 5.3.7, and 5.3.12 directly."""
    time = pd.DatetimeIndex(source.time.values)
    values = source[case.variable].values
    results = []
    for year in np.unique(time.year):
        selected = values[time.year == year]
        if case.reducer == "mean_pressure":
            result = np.nanmean(selected / 100, axis=0)
        elif case.reducer == "mean_humidity":
            result = np.nanmean(selected * 100, axis=0)
        elif case.reducer == "north":
            result = np.sum(
                np.isfinite(selected) & ((selected > 315) | (selected <= 45)),
                axis=0,
            )
        elif case.reducer == "east":
            result = np.sum(
                np.isfinite(selected) & (selected > 45) & (selected <= 135), axis=0
            )
        elif case.reducer == "south":
            result = np.sum(
                np.isfinite(selected) & (selected > 135) & (selected <= 225),
                axis=0,
            )
        else:
            result = np.sum(
                np.isfinite(selected) & (selected > 225) & (selected <= 315),
                axis=0,
            )
        results.append(result)
    return np.stack(results)


@pytest.mark.parametrize("chunk_size", [None, 7], ids=["eager", "chunked"])
@pytest.mark.parametrize("case", BATCH6_CASES, ids=lambda case: case.name)
def test_batch6_indices_match_atbd_oracle(
    case: Batch6Case,
    chunk_size: int | None,
) -> None:
    """Compare pressure, humidity, and wind sectors with ATBD reductions."""
    source = _batch6_cube()
    expected = _batch6_oracle(source, case)
    study = source[[case.variable]]
    if chunk_size is not None:
        study = study.chunk({"time": chunk_size})

    actual = icclim.index(
        in_files=study,
        var_name=case.variable,
        index_name=case.name,
        slice_mode="year",
        out_file=None,
        completeness="none",
    )[case.name].compute()

    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        expected,
        equal_nan=True,
    )
