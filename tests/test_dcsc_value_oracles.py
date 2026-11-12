"""Independent value oracles for the Meteo-France DCSC indices."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim


@dataclass(frozen=True)
class TemperatureCase:
    name: str
    variables: tuple[str, ...]
    reducer: Literal["mean", "range", "count", "heating", "cooling"]
    threshold: float | None = None
    operator: Literal["<", ">"] | None = None


TEMPERATURE_CASES = (
    TemperatureCase("TAV", ("tas",), "mean"),
    TemperatureCase("TXAV", ("tasmax",), "mean"),
    pytest.param(
        TemperatureCase("TRAV", ("tasmin", "tasmax"), "range"),
        marks=pytest.mark.xfail(strict=True, reason="#668"),
    ),
    TemperatureCase("TNFD", ("tasmin",), "count", 0.0, "<"),
    TemperatureCase("TXFD", ("tasmax",), "count", 0.0, "<"),
    TemperatureCase("SD", ("tasmax",), "count", 25.0, ">"),
    TemperatureCase("TX35", ("tasmax",), "count", 35.0, ">"),
    TemperatureCase("TR", ("tasmin",), "count", 20.0, ">"),
    TemperatureCase("HDD", ("tas",), "heating", 17.0),
    TemperatureCase("CDD", ("tas",), "cooling", 18.0),
)


def _temperature_cube() -> xr.Dataset:
    """Build a deterministic three-year 2x2 daily temperature cube."""
    time = pd.date_range("2000-01-01", "2002-12-31", freq="D")
    rng = np.random.default_rng(20261112)
    phase = 2 * np.pi * (time.dayofyear.to_numpy() - 80) / 365.25
    tas = 12 + 11 * np.sin(phase)[:, None, None]
    tas = tas + np.array([[-2.0, 0.0], [1.5, 3.0]]) + rng.normal(
        0, 0.8, (len(time), 2, 2)
    )
    tasmin = tas - 5.0
    tasmax = tas + 5.0

    # The 2023-12-01 DRIAS table defines frost/ice days with < 0 C, while the
    # older DRIAS page and registry prose say <= 0 C. The table is followed
    # here; exact zero records the source ambiguity without hiding the edge.
    probe = time == pd.Timestamp("2001-01-15")
    tasmin[probe, 0, 0] = 0.0
    tasmax[probe, 0, 1] = 0.0
    tasmax[probe, 1, 0] = 25.0
    tasmax[probe, 1, 1] = 35.0
    tasmin[time == pd.Timestamp("2001-07-15"), 1, 1] = 20.0

    tas[time == pd.Timestamp("2000-04-10"), 0, 0] = np.nan
    tasmin[time == pd.Timestamp("2001-05-11"), 0, 1] = np.nan
    tasmax[time == pd.Timestamp("2002-06-12"), 1, 0] = np.nan
    coords = {"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]}
    return xr.Dataset(
        {
            "tas": xr.DataArray(tas, dims=("time", "lat", "lon"), attrs={"units": "degC"}),
            "tasmin": xr.DataArray(
                tasmin, dims=("time", "lat", "lon"), attrs={"units": "degC"}
            ),
            "tasmax": xr.DataArray(
                tasmax, dims=("time", "lat", "lon"), attrs={"units": "degC"}
            ),
        },
        coords=coords,
    )


def _annual_temperature_reference(source: xr.Dataset, case: TemperatureCase) -> np.ndarray:
    """Evaluate the DRIAS-2020 formula using only numpy and pandas."""
    years = pd.DatetimeIndex(source.time.values).year
    outputs = []
    for year in np.unique(years):
        selected = years == year
        values = source[case.variables[0]].values[selected]
        if case.reducer == "mean":
            output = np.nanmean(values, axis=0)
        elif case.reducer == "range":
            maximum = source[case.variables[1]].values[selected]
            output = np.nanmean(maximum - values, axis=0)
        elif case.reducer == "count":
            finite = np.isfinite(values)
            if case.operator == "<":
                events = finite & (values < case.threshold)
            else:
                events = finite & (values > case.threshold)
            output = events.sum(axis=0)
        elif case.reducer == "heating":
            output = np.nansum(np.maximum(case.threshold - values, 0.0), axis=0)
        else:
            output = np.nansum(np.maximum(values - case.threshold, 0.0), axis=0)
        all_missing = np.isnan(values).all(axis=0)
        outputs.append(np.where(all_missing, np.nan, output))
    return np.stack(outputs)


@pytest.mark.parametrize("chunk_size", [None, 1, 7, -1], ids=["eager", "time1", "time7", "full"])
@pytest.mark.parametrize("case", TEMPERATURE_CASES, ids=lambda case: case.name)
def test_basic_temperature_indices_match_drias_reference(
    case: TemperatureCase, chunk_size: int | None
) -> None:
    """Compare basic temperature indices with the written DRIAS formulas."""
    source = _temperature_cube()[list(case.variables)]
    if chunk_size is not None:
        size = source.sizes["time"] if chunk_size == -1 else chunk_size
        source = source.chunk({"time": size})
    function = getattr(icclim.dcsc, case.name.lower())
    actual = function(
        in_files=source,
        var_name=list(case.variables),
        slice_mode="year",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[case.name].compute()
    expected = _annual_temperature_reference(_temperature_cube(), case)
    np.testing.assert_allclose(actual.values, expected, equal_nan=True)
    assert actual.dims == ("time", "lat", "lon")
    assert actual.attrs.get("units")
    assert actual.attrs.get("long_name")


@dataclass(frozen=True)
class NormalCase:
    name: str
    variable: str
    direction: Literal["warm", "cold"]
    spell: bool = False


NORMAL_CASES = (
    NormalCase("TXND", "tasmax", "warm"),
    NormalCase("TNHT", "tasmin", "warm"),
    NormalCase("TNND", "tasmin", "cold"),
    NormalCase("TNCWD", "tasmin", "cold", True),
    NormalCase("TXHWD", "tasmax", "warm", True),
)


def _normal_cube(case: NormalCase, varying_normal: bool) -> tuple[xr.DataArray, xr.DataArray]:
    """Return study values and a user-supplied daily reference normal."""
    time = pd.date_range("2000-01-01", "2002-12-31", freq="D")
    normal_values = np.full((len(time), 2, 2), 10.0)
    if varying_normal:
        normal_values += np.array([[0.0, 1.0], [-1.0, 2.0]])[None, :, :]
    values = normal_values.copy()
    direction = 1.0 if case.direction == "warm" else -1.0
    internal = (time >= "2001-07-01") & (time <= "2001-07-08")
    crossing = ((time >= "2000-12-28") & (time <= "2001-01-06"))
    values[internal | crossing] += direction * 5.0
    values[time == pd.Timestamp("2002-05-05"), 0, 1] += direction * 5.0
    values[time == pd.Timestamp("2001-08-08"), 1, 0] = np.nan
    coords = {"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]}
    study = xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords=coords,
        name=case.variable,
        attrs={"units": "degC"},
    )
    normal = xr.DataArray(
        normal_values,
        dims=study.dims,
        coords=coords,
        name=case.variable,
        attrs={"units": "degC"},
    )
    return study, normal


def _runs(events: np.ndarray) -> list[tuple[int, int]]:
    """Return inclusive bounds of maximal true runs in a one-dimensional array."""
    runs: list[tuple[int, int]] = []
    start = None
    for position, event in enumerate(np.append(events, False)):
        if event and start is None:
            start = position
        elif not event and start is not None:
            runs.append((start, position - 1))
            start = None
    return runs


def _normal_reference(
    study: xr.DataArray,
    normal: xr.DataArray,
    case: NormalCase,
    run_index: str,
    split: bool,
) -> np.ndarray:
    """Apply the DRIAS normal departure and spell definitions directly."""
    time = pd.DatetimeIndex(study.time.values)
    years = np.unique(time.year)
    finite = np.isfinite(study.values) & np.isfinite(normal.values)
    if case.direction == "warm":
        events = finite & (study.values >= normal.values + 5.0)
    else:
        events = finite & (study.values <= normal.values - 5.0)
    if not case.spell:
        return np.stack([events[time.year == year].sum(axis=0) for year in years])

    result = np.zeros((len(years), *events.shape[1:]), dtype=float)
    for cell in np.ndindex(events.shape[1:]):
        for start, end in _runs(events[(slice(None), *cell)]):
            if split:
                for year_index, year in enumerate(years):
                    length = int(np.sum(time[start : end + 1].year == year))
                    if length >= 6:
                        result[(year_index, *cell)] += length
            elif end - start + 1 >= 6:
                anchor = start if run_index == "first" else end
                year_index = int(np.flatnonzero(years == time[anchor].year)[0])
                result[(year_index, *cell)] += end - start + 1
    return result


@pytest.mark.parametrize("chunk_size", [None, 1, 7, -1], ids=["eager", "time1", "time7", "full"])
@pytest.mark.parametrize("varying_normal", [False, True], ids=["constant", "array"])
@pytest.mark.parametrize("case", NORMAL_CASES, ids=lambda case: case.name)
def test_normal_based_indices_match_drias_reference(
    case: NormalCase, varying_normal: bool, chunk_size: int | None
) -> None:
    """Check user normals, inclusive thresholds and six-day spell filtering."""
    study, normal = _normal_cube(case, varying_normal)
    if chunk_size is not None:
        size = study.sizes["time"] if chunk_size == -1 else chunk_size
        study = study.chunk({"time": size})
    function = getattr(icclim.dcsc, case.name.lower())
    actual = function(
        study,
        normal=normal,
        slice_mode="year",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[case.name].compute()
    expected = _normal_reference(study.compute(), normal, case, "first", False)
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values, expected, equal_nan=True
    )


@pytest.mark.parametrize("run_index,split", [("first", False), ("last", False), ("last", True)])
@pytest.mark.parametrize("case", [case for case in NORMAL_CASES if case.spell], ids=lambda case: case.name)
def test_normal_spell_attribution_matches_reference(
    case: NormalCase, run_index: str, split: bool
) -> None:
    """Check a ten-day spell crossing 31 December under every attribution mode."""
    study, normal = _normal_cube(case, False)
    actual = getattr(icclim.dcsc, case.name.lower())(
        study.chunk({"time": 7}),
        normal=normal,
        slice_mode="year",
        run_index=run_index,
        split_runs_at_period_boundary=split,
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[case.name].compute()
    expected = _normal_reference(study, normal, case, run_index, split)
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values, expected, equal_nan=True
    )


@pytest.mark.xfail(strict=True, reason="#669")
@pytest.mark.parametrize("case", [case for case in NORMAL_CASES if case.spell], ids=lambda case: case.name)
def test_normal_spell_output_keeps_input_dimension_order(case: NormalCase) -> None:
    """Regular output follows the input order, with the resampled time first."""
    study, normal = _normal_cube(case, False)
    actual = getattr(icclim.dcsc, case.name.lower())(
        study,
        normal=normal,
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[case.name]
    assert actual.dims == study.dims


def test_normal_argument_errors_are_clear() -> None:
    """A required or dimensionally invalid normal must fail instead of being ignored."""
    study, normal = _normal_cube(NORMAL_CASES[0], False)
    with pytest.raises(TypeError, match="normal"):
        icclim.dcsc.txnd(study)
    wrong = normal.copy()
    wrong.attrs["units"] = "mm/day"
    with pytest.raises(Exception, match="convert|dimension|temperature"):
        icclim.dcsc.txnd(study, normal=wrong, out_file=None)
