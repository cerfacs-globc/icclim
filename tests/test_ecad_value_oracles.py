"""Independent value oracles for ECA&D indices."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
import pytest
import xarray as xr

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
    seasonal = 11 + 12 * np.sin(2 * np.pi * (time.dayofyear.to_numpy() - 80) / 365.25)
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
