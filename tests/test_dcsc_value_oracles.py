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
