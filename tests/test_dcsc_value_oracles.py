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

TEMPERATURE_UNITS = {
    "degC": lambda values: values,
    "K": lambda values: values + 273.15,
    "degF": lambda values: values * 9.0 / 5.0 + 32.0,
}


def _temperature_cube() -> xr.Dataset:
    """Build a deterministic three-year 2x2 daily temperature cube."""
    time = pd.date_range("2000-01-01", "2002-12-31", freq="D")
    rng = np.random.default_rng(20261112)
    phase = 2 * np.pi * (time.dayofyear.to_numpy() - 80) / 365.25
    tas = 12 + 11 * np.sin(phase)[:, None, None]
    tas = (
        tas
        + np.array([[-2.0, 0.0], [1.5, 3.0]])
        + rng.normal(0, 0.8, (len(time), 2, 2))
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
            "tas": xr.DataArray(
                tas, dims=("time", "lat", "lon"), attrs={"units": "degC"}
            ),
            "tasmin": xr.DataArray(
                tasmin, dims=("time", "lat", "lon"), attrs={"units": "degC"}
            ),
            "tasmax": xr.DataArray(
                tasmax, dims=("time", "lat", "lon"), attrs={"units": "degC"}
            ),
        },
        coords=coords,
    )


def _annual_temperature_reference(
    source: xr.Dataset, case: TemperatureCase
) -> np.ndarray:
    """Evaluate the DRIAS-2020 formula using only numpy and pandas."""
    years = np.asarray(source.time.dt.year.values)
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


def _temperature_in_unit(source: xr.Dataset | xr.DataArray, unit: str):
    """Represent the same physical temperatures in another declared unit."""
    converted = source.copy(deep=True)
    if isinstance(converted, xr.Dataset):
        for variable in converted.data_vars.values():
            variable.data = TEMPERATURE_UNITS[unit](variable.data)
            variable.attrs["units"] = unit
    else:
        converted.data = TEMPERATURE_UNITS[unit](converted.data)
        converted.attrs["units"] = unit
    return converted


@pytest.mark.parametrize(
    "chunk_size", [None, 1, 7, -1], ids=["eager", "time1", "time7", "full"]
)
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


@pytest.mark.parametrize("unit", ["K", "degF"])
@pytest.mark.parametrize("case", TEMPERATURE_CASES, ids=lambda case: case.name)
def test_basic_temperature_units_match_drias_reference(
    case: TemperatureCase, unit: str
) -> None:
    """K, degC and degF representations yield the same physical values."""
    if unit == "degF" and case.name in {"SD", "TX35", "TR"}:
        pytest.skip("covered by the strict #675 regression")
    original = _temperature_cube()
    source = _temperature_in_unit(original[list(case.variables)], unit)
    actual = getattr(icclim.dcsc, case.name.lower())(
        source,
        var_name=list(case.variables),
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[case.name].compute()
    expected = _annual_temperature_reference(original, case)
    np.testing.assert_allclose(actual.values, expected, rtol=1e-6, equal_nan=True)


@pytest.mark.xfail(strict=True, reason="#675")
@pytest.mark.parametrize(
    ("name", "variable", "value"),
    [("SD", "tasmax", 77.0), ("TX35", "tasmax", 95.0), ("TR", "tasmin", 68.0)],
)
def test_strict_temperature_threshold_equality_in_fahrenheit(
    name: str, variable: str, value: float
) -> None:
    """A Fahrenheit value equal to a strict Celsius threshold is not an event."""
    time = pd.date_range("2001-01-01", periods=3)
    source = xr.DataArray(
        [value] * 3,
        dims="time",
        coords={"time": time},
        name=variable,
        attrs={"units": "degF"},
    )
    actual = getattr(icclim.dcsc, name.lower())(
        source,
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[name]
    np.testing.assert_array_equal(actual.values, [0])


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


def _normal_cube(
    case: NormalCase, varying_normal: bool
) -> tuple[xr.DataArray, xr.DataArray]:
    """Return study values and a user-supplied daily reference normal."""
    time = pd.date_range("2000-01-01", "2002-12-31", freq="D")
    normal_values = np.full((len(time), 2, 2), 10.0)
    if varying_normal:
        normal_values += np.array([[0.0, 1.0], [-1.0, 2.0]])[None, :, :]
    values = normal_values.copy()
    direction = 1.0 if case.direction == "warm" else -1.0
    internal = (time >= "2001-07-01") & (time <= "2001-07-08")
    crossing = (time >= "2000-12-28") & (time <= "2001-01-06")
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
    time_years = np.asarray(study.time.dt.year.values)
    years = np.unique(time_years)
    finite = np.isfinite(study.values) & np.isfinite(normal.values)
    if case.direction == "warm":
        events = finite & (study.values >= normal.values + 5.0)
    else:
        events = finite & (study.values <= normal.values - 5.0)
    if not case.spell:
        return np.stack([events[time_years == year].sum(axis=0) for year in years])

    result = np.zeros((len(years), *events.shape[1:]), dtype=float)
    for cell in np.ndindex(events.shape[1:]):
        for start, end in _runs(events[(slice(None), *cell)]):
            if split:
                for year_index, year in enumerate(years):
                    length = int(np.sum(time_years[start : end + 1] == year))
                    if length >= 6:
                        result[(year_index, *cell)] += length
            elif end - start + 1 >= 6:
                anchor = start if run_index == "first" else end
                year_index = int(np.flatnonzero(years == time_years[anchor])[0])
                result[(year_index, *cell)] += end - start + 1
    return result


@pytest.mark.parametrize(
    "chunk_size", [None, 1, 7, -1], ids=["eager", "time1", "time7", "full"]
)
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


@pytest.mark.parametrize("unit", ["K", "degF"])
@pytest.mark.parametrize("case", NORMAL_CASES, ids=lambda case: case.name)
def test_normal_based_temperature_units_match_reference(
    case: NormalCase, unit: str
) -> None:
    """The five-degree normal offset is invariant across temperature units."""
    study, normal = _normal_cube(case, True)
    actual = getattr(icclim.dcsc, case.name.lower())(
        _temperature_in_unit(study, unit),
        normal=_temperature_in_unit(normal, unit),
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[case.name].compute()
    expected = _normal_reference(study, normal, case, "first", False)
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values, expected, equal_nan=True
    )


@pytest.mark.parametrize(
    ("run_index", "split"), [("first", False), ("last", False), ("last", True)]
)
@pytest.mark.parametrize(
    "case", [case for case in NORMAL_CASES if case.spell], ids=lambda case: case.name
)
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
@pytest.mark.parametrize(
    "case", [case for case in NORMAL_CASES if case.spell], ids=lambda case: case.name
)
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
    with pytest.raises(Exception, match=r"convert|dimension|temperature"):
        icclim.dcsc.txnd(study, normal=wrong, out_file=None)


@dataclass(frozen=True)
class PrecipitationCase:
    name: str
    reducer: Literal["mean", "wet_mean", "sum", "count", "run"]
    threshold: float | None = None
    operator: Literal["<", ">="] | None = None


PRECIPITATION_CASES = (
    PrecipitationCase("PAV", "mean"),
    PrecipitationCase("PINT", "wet_mean", 1.0, ">="),
    PrecipitationCase("RR", "sum"),
    PrecipitationCase("RR1MM", "count", 1.0, ">="),
    PrecipitationCase("PN20MM", "count", 20.0, ">="),
    PrecipitationCase("PXCDD", "run", 1.0, "<"),
    PrecipitationCase("PXCWD", "run", 1.0, ">="),
)


def _precipitation_cube(case: PrecipitationCase, unit: str) -> xr.DataArray:
    """Build deterministic precipitation with equality and boundary runs."""
    time = pd.date_range("2000-01-01", "2002-12-31", freq="D")
    rng = np.random.default_rng(20261113)
    values = rng.gamma(1.6, 3.0, (len(time), 2, 2))
    values[np.arange(len(time)) % 11 == 0] = 0.2
    values[time == pd.Timestamp("2001-03-03"), 0, 0] = 1.0
    values[time == pd.Timestamp("2001-04-04"), 0, 1] = 20.0
    values[time == pd.Timestamp("2002-05-05"), 1, 0] = np.nan
    if case.reducer == "run":
        event = 0.2 if case.operator == "<" else 2.0
        non_event = 2.0 if case.operator == "<" else 0.2
        values[:] = non_event
        crossing = (time >= "2000-12-28") & (time <= "2001-01-06")
        internal = (time >= "2002-06-01") & (time <= "2002-06-08")
        values[crossing | internal] = event
        values[time == pd.Timestamp("2001-08-08"), 1, 0] = np.nan
        values[time == pd.Timestamp("2001-09-09"), 0, 1] = 1.0
    data = values / 86400.0 if unit == "kg m-2 s-1" else values
    return xr.DataArray(
        data,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]},
        name="pr",
        attrs={"units": unit},
    )


def _precipitation_reference(
    source: xr.DataArray,
    case: PrecipitationCase,
    run_index: str = "first",
    split: bool = False,
) -> np.ndarray:
    """Evaluate DRIAS precipitation reductions in mm/day without library code."""
    time_years = np.asarray(source.time.dt.year.values)
    years = np.unique(time_years)
    values = source.values * (86400.0 if source.attrs["units"] == "kg m-2 s-1" else 1.0)
    finite = np.isfinite(values)
    if case.reducer == "run":
        events = finite & ((values < 1.0) if case.operator == "<" else (values >= 1.0))
        result = np.zeros((len(years), *events.shape[1:]), dtype=float)
        for cell in np.ndindex(events.shape[1:]):
            for start, end in _runs(events[(slice(None), *cell)]):
                if split:
                    for year_index, year in enumerate(years):
                        length = int(np.sum(time_years[start : end + 1] == year))
                        result[(year_index, *cell)] = max(
                            result[(year_index, *cell)], length
                        )
                else:
                    anchor = start if run_index == "first" else end
                    year_index = int(np.flatnonzero(years == time_years[anchor])[0])
                    result[(year_index, *cell)] = max(
                        result[(year_index, *cell)], end - start + 1
                    )
        return result

    outputs = []
    for year in years:
        selected = time_years == year
        period = values[selected]
        period_finite = finite[selected]
        if case.reducer == "mean":
            output = np.nanmean(period, axis=0)
        elif case.reducer == "wet_mean":
            output = np.nanmean(
                np.where(period_finite & (period >= 1.0), period, np.nan), axis=0
            )
        elif case.reducer == "sum":
            output = np.nansum(period, axis=0)
        else:
            output = np.sum(period_finite & (period >= case.threshold), axis=0)
        outputs.append(output)
    return np.stack(outputs)


@pytest.mark.parametrize(
    "chunk_size", [None, 1, 7, -1], ids=["eager", "time1", "time7", "full"]
)
@pytest.mark.parametrize("unit", ["mm/day", "kg m-2 s-1"])
@pytest.mark.parametrize("case", PRECIPITATION_CASES, ids=lambda case: case.name)
def test_basic_precipitation_indices_match_drias_reference(
    case: PrecipitationCase, unit: str, chunk_size: int | None
) -> None:
    """Check precipitation values, wet-day equality and hydro unit conversion."""
    source = _precipitation_cube(case, unit)
    if chunk_size is not None:
        size = source.sizes["time"] if chunk_size == -1 else chunk_size
        source = source.chunk({"time": size})
    actual = getattr(icclim.dcsc, case.name.lower())(
        source,
        slice_mode="year",
        run_index="first",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[case.name].compute()
    expected = _precipitation_reference(source.compute(), case)
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values, expected, equal_nan=True
    )
    assert actual.attrs.get("units")
    assert actual.attrs.get("long_name")


@pytest.mark.parametrize(
    ("run_index", "split"), [("first", False), ("last", False), ("last", True)]
)
@pytest.mark.parametrize(
    "case",
    [case for case in PRECIPITATION_CASES if case.reducer == "run"],
    ids=lambda case: case.name,
)
def test_precipitation_run_attribution_matches_reference(
    case: PrecipitationCase, run_index: str, split: bool
) -> None:
    """Check a ten-day wet or dry run crossing 31 December."""
    source = _precipitation_cube(case, "mm/day").chunk({"time": 7})
    actual = getattr(icclim.dcsc, case.name.lower())(
        source,
        slice_mode="year",
        run_index=run_index,
        split_runs_at_period_boundary=split,
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[case.name].compute()
    expected = _precipitation_reference(source.compute(), case, run_index, split)
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values, expected, equal_nan=True
    )


@pytest.mark.xfail(strict=True, reason="#670")
@pytest.mark.parametrize(
    "chunk_size", [None, 1, 7, -1], ids=["eager", "time1", "time7", "full"]
)
@pytest.mark.parametrize("unit", ["degC", "K", "degF"])
@pytest.mark.parametrize(
    ("name", "variable", "quantile"),
    [
        ("TX10", "tasmax", 0.10),
        ("TX90", "tasmax", 0.90),
        ("TN10", "tasmin", 0.10),
        ("TN90", "tasmin", 0.90),
    ],
)
def test_temperature_percentiles_are_values_in_degrees(
    name: str, variable: str, quantile: float, unit: str, chunk_size: int | None
) -> None:
    """DRIAS TXQ/TNQ indices are period percentiles, not occurrence counts."""
    original = _temperature_cube()[variable]
    source = _temperature_in_unit(original, unit)
    if chunk_size is not None:
        size = source.sizes["time"] if chunk_size == -1 else chunk_size
        source = source.chunk({"time": size})
    actual = getattr(icclim.dcsc, name.lower())(
        source,
        base_period_time_range=["2000-01-01", "2000-12-31"],
        time_range=["2001-01-01", "2002-12-31"],
        slice_mode="year",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[name].compute()
    values = original.sel(time=slice("2001-01-01", "2002-12-31"))
    years = pd.DatetimeIndex(values.time.values).year
    expected = np.stack(
        [
            np.nanquantile(
                values.values[years == year],
                quantile,
                axis=0,
                method="median_unbiased",
            )
            for year in np.unique(years)
        ]
    )
    np.testing.assert_allclose(actual.values, expected, equal_nan=True)
    assert actual.attrs["units"] in {"degC", "degree_Celsius", "°C"}


PERCENTILE_PRECIPITATION = (
    pytest.param("R99", 0.99, marks=pytest.mark.xfail(strict=True, reason="#672")),
    pytest.param("PFL90", 0.90, marks=pytest.mark.xfail(strict=True, reason="#671")),
    ("PQ90", 0.90),
    ("PQ99", 0.99),
)


def _period_precipitation_reference(
    source: xr.DataArray, name: str, quantile: float
) -> np.ndarray:
    """Apply the annual percentile formulas in the DRIAS 2023 table."""
    time_years = np.asarray(source.time.dt.year.values)
    values = source.values * (86400.0 if source.attrs["units"] == "kg m-2 s-1" else 1.0)
    outputs = []
    output_years = np.unique(time_years)
    reference_threshold = None
    if name == "R99":
        reference = values[time_years == output_years[0]]
        reference_threshold = np.nanquantile(
            reference, quantile, axis=0, method="median_unbiased"
        )
        output_years = output_years[1:]
    for year in output_years:
        period = values[time_years == year]
        threshold = (
            reference_threshold
            if reference_threshold is not None
            else np.nanquantile(period, quantile, axis=0, method="median_unbiased")
        )
        if name == "R99":
            output = np.sum(np.isfinite(period) & (period > threshold), axis=0)
        elif name == "PFL90":
            numerator = np.nansum(np.where(period > threshold, period, 0.0), axis=0)
            output = 100.0 * numerator / np.nansum(period, axis=0)
        else:
            output = threshold
        outputs.append(output)
    return np.stack(outputs)


@pytest.mark.parametrize(
    "chunk_size", [None, 1, 7, -1], ids=["eager", "time1", "time7", "full"]
)
@pytest.mark.parametrize("unit", ["mm/day", "kg m-2 s-1"])
@pytest.mark.parametrize(("name", "quantile"), PERCENTILE_PRECIPITATION)
def test_percentile_precipitation_indices_match_drias_reference(
    name: str, quantile: float, unit: str, chunk_size: int | None
) -> None:
    """Check annual precipitation percentiles, counts and fraction of total."""
    source = _precipitation_cube(PRECIPITATION_CASES[0], unit)
    if chunk_size is not None:
        size = source.sizes["time"] if chunk_size == -1 else chunk_size
        source = source.chunk({"time": size})
    kwargs = {}
    if name == "R99":
        kwargs = {
            "base_period_time_range": ["2000-01-01", "2000-12-31"],
            "time_range": ["2001-01-01", "2002-12-31"],
        }
    actual = getattr(icclim.dcsc, name.lower())(
        source,
        slice_mode="year",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
        **kwargs,
    )[name].compute()
    expected = _period_precipitation_reference(source.compute(), name, quantile)
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        expected,
        rtol=1e-6,
        equal_nan=True,
    )


def _wind_cube(unit: str = "m s-1") -> xr.DataArray:
    """Return three years of deterministic daily wind speed."""
    time = pd.date_range("2000-01-01", "2002-12-31", freq="D")
    rng = np.random.default_rng(20261114)
    values = rng.weibull(2.2, (len(time), 2, 2)) * 7.0
    values[time.year == 2001] += 1.0
    values[time.year == 2002] -= 0.5
    values[time == pd.Timestamp("2002-05-05"), 1, 0] = np.nan
    data = values * 3.6 if unit == "km h-1" else values
    return xr.DataArray(
        data,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]},
        name="sfcWind",
        attrs={"units": unit},
    )


WIND_CASES = [
    pytest.param("FFAV", marks=pytest.mark.xfail(strict=True, reason="#673")),
    pytest.param("FF98", marks=pytest.mark.xfail(strict=True, reason="#674")),
]


@pytest.mark.parametrize(
    "chunk_size", [None, 1, 7, -1], ids=["eager", "time1", "time7", "full"]
)
@pytest.mark.parametrize("unit", ["m s-1", "km h-1"])
@pytest.mark.parametrize("name", WIND_CASES)
def test_wind_indices_match_drias_reference(
    name: str, unit: str, chunk_size: int | None
) -> None:
    """Check reference-mean difference and days above the reference q98."""
    source = _wind_cube(unit)
    if chunk_size is not None:
        size = source.sizes["time"] if chunk_size == -1 else chunk_size
        source = source.chunk({"time": size})
    actual = getattr(icclim.dcsc, name.lower())(
        source,
        base_period_time_range=["2000-01-01", "2000-12-31"],
        time_range=["2001-01-01", "2002-12-31"],
        slice_mode="year",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[name].compute()
    values = source.compute().values / (3.6 if unit == "km h-1" else 1.0)
    time = pd.DatetimeIndex(source.time.values)
    reference = values[time.year == 2000]
    if name == "FFAV":
        reference_value = np.nanmean(reference, axis=0)
        expected = np.stack(
            [
                np.nanmean(values[time.year == year], axis=0) - reference_value
                for year in (2001, 2002)
            ]
        )
    else:
        threshold = np.nanquantile(reference, 0.98, axis=0, method="median_unbiased")
        expected = np.stack(
            [
                np.sum(values[time.year == year] > threshold, axis=0)
                for year in (2001, 2002)
            ]
        )
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        expected,
        rtol=1e-6,
        equal_nan=True,
    )


CALENDARS = ("standard", "noleap", "360_day", "all_leap")


def _in_calendar(source: xr.Dataset | xr.DataArray, calendar: str):
    """Convert a deterministic cube without using climate-index code."""
    if calendar == "standard":
        return source
    return source.convert_calendar(calendar, align_on="date", missing=np.nan)


@pytest.mark.parametrize("calendar", CALENDARS)
@pytest.mark.parametrize("case", TEMPERATURE_CASES, ids=lambda case: case.name)
def test_basic_temperature_calendars_match_reference(
    case: TemperatureCase, calendar: str
) -> None:
    """Basic temperature formulas apply unchanged to all supported calendars."""
    source = _in_calendar(_temperature_cube(), calendar)
    actual = getattr(icclim.dcsc, case.name.lower())(
        source[list(case.variables)],
        var_name=list(case.variables),
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[case.name].compute()
    expected = _annual_temperature_reference(source, case)
    np.testing.assert_allclose(actual.values, expected, equal_nan=True)


@pytest.mark.parametrize("calendar", CALENDARS)
@pytest.mark.parametrize("case", NORMAL_CASES, ids=lambda case: case.name)
def test_normal_based_calendars_match_reference(
    case: NormalCase, calendar: str
) -> None:
    """Reference-normal comparisons and spells work on cftime calendars."""
    study, normal = _normal_cube(case, True)
    study = _in_calendar(study, calendar)
    normal = _in_calendar(normal, calendar)
    actual = getattr(icclim.dcsc, case.name.lower())(
        study,
        normal=normal,
        run_index="first",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[case.name].compute()
    expected = _normal_reference(study, normal, case, "first", False)
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values, expected, equal_nan=True
    )


@pytest.mark.parametrize("calendar", CALENDARS)
@pytest.mark.parametrize("case", PRECIPITATION_CASES, ids=lambda case: case.name)
def test_basic_precipitation_calendars_match_reference(
    case: PrecipitationCase, calendar: str
) -> None:
    """Precipitation reductions work on standard and cftime calendars."""
    source = _in_calendar(_precipitation_cube(case, "mm/day"), calendar)
    actual = getattr(icclim.dcsc, case.name.lower())(
        source,
        run_index="first",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[case.name].compute()
    expected = _precipitation_reference(source, case)
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values, expected, equal_nan=True
    )


@pytest.mark.parametrize("calendar", CALENDARS)
@pytest.mark.parametrize(("name", "quantile"), PERCENTILE_PRECIPITATION)
def test_percentile_precipitation_calendars_match_reference(
    name: str, quantile: float, calendar: str
) -> None:
    """Annual percentile formulas support standard and cftime calendars."""
    source = _in_calendar(
        _precipitation_cube(PRECIPITATION_CASES[0], "mm/day"), calendar
    )
    kwargs = {}
    if name == "R99":
        kwargs = {
            "base_period_time_range": ["2000-01-01", "2000-12-30"],
            "time_range": ["2001-01-01", "2002-12-30"],
        }
    actual = getattr(icclim.dcsc, name.lower())(
        source,
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
        **kwargs,
    )[name].compute()
    expected = _period_precipitation_reference(source, name, quantile)
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        expected,
        rtol=1e-6,
        equal_nan=True,
    )


@pytest.mark.parametrize("calendar", CALENDARS)
@pytest.mark.parametrize(
    "name",
    [pytest.param("FFAV", marks=pytest.mark.xfail(strict=True, reason="#673")), "FF98"],
)
def test_wind_calendars_match_reference(name: str, calendar: str) -> None:
    """Wind reference-period formulas support standard and cftime calendars."""
    source = _in_calendar(_wind_cube(), calendar)
    actual = getattr(icclim.dcsc, name.lower())(
        source,
        base_period_time_range=["2000-01-01", "2000-12-30"],
        time_range=["2001-01-01", "2002-12-30"],
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[name].compute()
    assert actual.sizes["time"] == 2


@pytest.mark.xfail(strict=True, reason="#670")
@pytest.mark.parametrize("calendar", CALENDARS)
@pytest.mark.parametrize(
    ("name", "variable", "quantile"),
    [
        ("TX10", "tasmax", 0.10),
        ("TX90", "tasmax", 0.90),
        ("TN10", "tasmin", 0.10),
        ("TN90", "tasmin", 0.90),
    ],
)
def test_temperature_percentile_calendars_match_reference(
    name: str, variable: str, quantile: float, calendar: str
) -> None:
    """Temperature percentile values support standard and cftime calendars."""
    source = _in_calendar(_temperature_cube()[variable], calendar)
    actual = getattr(icclim.dcsc, name.lower())(
        source,
        base_period_time_range=["2000-01-01", "2000-12-30"],
        time_range=["2001-01-01", "2002-12-30"],
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[name].compute()
    years = np.asarray(source.time.dt.year.values)
    expected = np.stack(
        [
            np.nanquantile(
                source.values[years == year],
                quantile,
                axis=0,
                method="median_unbiased",
            )
            for year in (2001, 2002)
        ]
    )
    np.testing.assert_allclose(actual.values, expected, equal_nan=True)


ALL_DCSC_NAMES = (
    "TAV",
    "TXAV",
    "TRAV",
    "TX10",
    "TX90",
    "TN10",
    "TN90",
    "TNFD",
    "TXFD",
    "SD",
    "TX35",
    "TR",
    "TXND",
    "TNHT",
    "TNND",
    "TNCWD",
    "TXHWD",
    "HDD",
    "CDD",
    "PAV",
    "PINT",
    "RR",
    "RR1MM",
    "PN20MM",
    "PXCDD",
    "PXCWD",
    "R99",
    "PFL90",
    "PQ90",
    "PQ99",
    "FFAV",
    "FF98",
)


def _parameter_value(item):
    """Return a dataclass value stored directly or in a pytest parameter."""
    return item.values[0] if hasattr(item, "values") else item


BASIC_TEMPERATURE_BY_NAME = {
    case.name: case for case in map(_parameter_value, TEMPERATURE_CASES)
}
NORMAL_BY_NAME = {case.name: case for case in NORMAL_CASES}
PRECIPITATION_BY_NAME = {case.name: case for case in PRECIPITATION_CASES}


def _edge_call(  # noqa: C901
    name: str,
    *,
    slice_mode: str,
    time_range: list[str],
    completeness: str = "none",
    whole_cell_missing: bool = False,
) -> xr.DataArray:
    """Call one DCSC entry point on its deterministic cube."""
    kwargs = {
        "slice_mode": slice_mode,
        "time_range": time_range,
        "out_file": None,
        "completeness": completeness,
        "logs_verbosity": "SILENT",
    }
    if slice_mode == "DJF":
        kwargs["allow_partial_seasons"] = True
    if name in BASIC_TEMPERATURE_BY_NAME:
        case = BASIC_TEMPERATURE_BY_NAME[name]
        source = _temperature_cube()[list(case.variables)]
        kwargs["var_name"] = list(case.variables)
    elif name in NORMAL_BY_NAME:
        case = NORMAL_BY_NAME[name]
        source, normal = _normal_cube(case, True)
        kwargs.update(normal=normal, run_index="first")
    elif name in {"TX10", "TX90", "TN10", "TN90"}:
        variable = "tasmax" if name.startswith("TX") else "tasmin"
        source = _temperature_cube()[variable]
        kwargs["base_period_time_range"] = ["2000-01-01", "2000-12-31"]
    elif name in PRECIPITATION_BY_NAME:
        case = PRECIPITATION_BY_NAME[name]
        source = _precipitation_cube(case, "mm/day")
        kwargs["run_index"] = "first"
    elif name in {"R99", "PFL90", "PQ90", "PQ99"}:
        source = _precipitation_cube(PRECIPITATION_CASES[0], "mm/day")
        if name == "R99":
            kwargs["base_period_time_range"] = ["2000-01-01", "2000-12-31"]
    else:
        source = _wind_cube()
        kwargs["base_period_time_range"] = ["2000-01-01", "2000-12-31"]
    if whole_cell_missing:
        source = source.copy(deep=True)
        if isinstance(source, xr.Dataset):
            for variable in source.data_vars.values():
                variable.loc[{"lat": 45.0, "lon": 1.0}] = np.nan
        else:
            source.loc[{"lat": 45.0, "lon": 1.0}] = np.nan
    return getattr(icclim.dcsc, name.lower())(source, **kwargs)[name].compute()


EDGE_NAMES = [
    pytest.param("FFAV", marks=pytest.mark.xfail(strict=True, reason="#673"))
    if name == "FFAV"
    else name
    for name in ALL_DCSC_NAMES
]


@pytest.mark.parametrize("slice_mode", ["month", "DJF"])
@pytest.mark.parametrize("name", EDGE_NAMES)
def test_monthly_and_seasonal_outputs_have_metadata(name: str, slice_mode: str) -> None:
    """Every DCSC entry point supports the documented monthly and seasonal output."""
    actual = _edge_call(
        name,
        slice_mode=slice_mode,
        time_range=["2001-01-01", "2002-12-31"],
    )
    assert "time" in actual.dims
    assert actual.attrs.get("units")
    assert actual.attrs.get("long_name")
    assert actual.attrs.get("standard_name")
    if name not in {"PQ90", "PQ99"}:
        assert actual.attrs["long_name"] != "todo"
        assert actual.attrs["standard_name"] != "todo"
    assert actual.time.size > 0


@pytest.mark.xfail(strict=True, reason="#676")
@pytest.mark.parametrize("name", ["PQ90", "PQ99"])
def test_precipitation_percentile_metadata_is_meaningful(name: str) -> None:
    """Published percentile outputs must not expose placeholder metadata."""
    actual = _edge_call(
        name, slice_mode="year", time_range=["2001-01-01", "2002-12-31"]
    )
    assert actual.attrs["long_name"] != "todo"
    assert actual.attrs["standard_name"] != "todo"


SUBSET_NAMES = [
    pytest.param("FFAV", marks=pytest.mark.xfail(strict=True, reason="#673"))
    if name == "FFAV"
    else name
    for name in ALL_DCSC_NAMES
]


@pytest.mark.parametrize("name", SUBSET_NAMES)
def test_time_range_subset_equals_full_result_slice(name: str) -> None:
    """A one-year request equals the same year selected from a two-year request."""
    full = _edge_call(name, slice_mode="year", time_range=["2001-01-01", "2002-12-31"])
    subset = _edge_call(
        name, slice_mode="year", time_range=["2002-01-01", "2002-12-31"]
    )
    selected = full.sel(time=slice("2002-01-01", "2002-12-31"))
    xr.testing.assert_allclose(subset, selected)


@pytest.mark.parametrize("name", EDGE_NAMES)
def test_strict_completeness_masks_a_whole_missing_grid_point(name: str) -> None:
    """Strict completeness never turns an entirely missing cell into a value."""
    actual = _edge_call(
        name,
        slice_mode="year",
        time_range=["2001-01-01", "2002-12-31"],
        completeness="strict",
        whole_cell_missing=True,
    )
    assert actual.sel(lat=45.0, lon=1.0).isnull().all()


@pytest.mark.parametrize(
    ("run_index", "split"), [("first", False), ("last", False), ("last", True)]
)
@pytest.mark.parametrize("name", ["TNCWD", "TXHWD", "PXCDD", "PXCWD"])
def test_run_crossing_a_whole_period_follows_attribution_convention(
    name: str, run_index: str, split: bool
) -> None:
    """One 2000-2002 run is attributed whole or split at year boundaries."""
    if name in NORMAL_BY_NAME:
        case = NORMAL_BY_NAME[name]
        study, normal = _normal_cube(case, False)
        direction = 1.0 if case.direction == "warm" else -1.0
        study.data = normal.values + direction * 5.0
        kwargs = {"normal": normal}
    else:
        case = PRECIPITATION_BY_NAME[name]
        study = _precipitation_cube(case, "mm/day")
        study.data[:] = 0.2 if case.operator == "<" else 2.0
        kwargs = {}
    actual = getattr(icclim.dcsc, name.lower())(
        study,
        run_index=run_index,
        split_runs_at_period_boundary=split,
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
        **kwargs,
    )[name].compute()
    if split:
        expected = np.array([366.0, 365.0, 365.0])
    elif run_index == "first":
        expected = (
            np.array([1096.0, 0.0, 0.0])
            if name in NORMAL_BY_NAME
            else np.array([1096.0, np.nan, np.nan])
        )
    else:
        expected = (
            np.array([0.0, 0.0, 1096.0])
            if name in NORMAL_BY_NAME
            else np.array([np.nan, np.nan, 1096.0])
        )
    for cell in np.ndindex(actual.sizes["lat"], actual.sizes["lon"]):
        np.testing.assert_allclose(
            actual.transpose("time", "lat", "lon").values[(slice(None), *cell)],
            expected,
            equal_nan=True,
        )
