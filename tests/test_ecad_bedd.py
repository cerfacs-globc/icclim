"""
Biologically Effective Degree Days (BEDD) against the ECA&D ATBD v11 (issue #638).

ATBD: BEDD = sum over 1 April to 30 September of min(max((TX + TN) / 2 - b, 0), 9),
with b = 10, TX and TN being the daily maximum and minimum temperature. The oracle
below is written from that text, day by day, and does not use icclim or xclim.
"""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from xclim.core.units import units2pint

import icclim
from icclim._core.xclim_compat import get_xclim_compute

TIME = pd.date_range("2001-01-01", "2002-12-31")
N_CELLS = 4


def _oracle(tn, tx, time) -> np.ndarray:
    """BEDD per year and cell, from the ATBD text; NaN days are not summed."""
    result = np.full((2, tn.shape[1]), np.nan)
    for year_index, year in enumerate((2001, 2002)):
        for j in range(tn.shape[1]):
            total, any_day = 0.0, False
            for i, day in enumerate(time):
                d = dt.date(day.year, day.month, day.day)
                if not dt.date(year, 4, 1) <= d <= dt.date(year, 9, 30):
                    continue
                if np.isnan(tn[i, j]) or np.isnan(tx[i, j]):
                    continue
                mean = (tx[i, j] + tn[i, j]) / 2
                total += min(max(mean - 10, 0), 9)
                any_day = True
            if any_day:
                result[year_index, j] = total
    return result


def _data(nan: bool = False):
    rng = np.random.default_rng(11)
    # Means below 10 (no contribution) and above 19 (capped at 9) both happen.
    seasonal = 12 + 14 * np.sin(2 * np.pi * (TIME.dayofyear.values - 100) / 365)
    tn = seasonal[:, None] - 4 + rng.uniform(-3, 3, (len(TIME), N_CELLS))
    tx = tn + rng.uniform(4, 12, tn.shape)
    if nan:
        tn[(TIME >= "2002-06-01") & (TIME <= "2002-06-03"), 1] = np.nan
        tx[(TIME >= "2001-04-01") & (TIME <= "2001-09-30"), 2] = np.nan
    return tn, tx


def _dataset(tn, tx, unit: str, chunked: bool) -> xr.Dataset:
    offset = 273.15 if unit == "K" else 0.0
    coords = {"time": TIME, "x": np.arange(N_CELLS)}
    ds = xr.Dataset(
        {
            "tasmin": xr.DataArray(
                tn + offset,
                dims=("time", "x"),
                coords=coords,
                attrs={"units": unit},
            ),
            "tasmax": xr.DataArray(
                tx + offset,
                dims=("time", "x"),
                coords=coords,
                attrs={"units": unit},
            ),
        }
    )
    return ds.chunk({"x": 2}) if chunked else ds


def _bedd(ds: xr.Dataset, **kwargs) -> xr.DataArray:
    kwargs.setdefault("completeness", "none")
    return icclim.index(
        index_name="BEDD", in_files=ds, out_file=None, **kwargs
    ).BEDD.compute()


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("unit", ["degC", "K"])
def test_bedd_matches_the_atbd_oracle(unit: str, chunked: bool) -> None:
    tn, tx = _data()
    actual = _bedd(_dataset(tn, tx, unit, chunked))
    np.testing.assert_allclose(actual.values, _oracle(tn, tx, TIME), rtol=1e-9)
    # The text of the units depends on the pint format: compare the dimensions.
    assert (
        units2pint(actual.attrs["units"]).dimensionality
        == units2pint("K d").dimensionality
    )


def test_bedd_floor_and_cap_are_both_reached() -> None:
    tn, tx = _data()
    mean = (tn + tx) / 2
    season = (TIME >= "2001-04-01") & (TIME <= "2001-09-30")
    assert (mean[season] < 10).any()
    assert (mean[season] - 10 > 9).any()


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("unit", ["degC", "K"])
def test_bedd_nan_handling(unit: str, chunked: bool) -> None:
    tn, tx = _data(nan=True)
    actual = _bedd(_dataset(tn, tx, unit, chunked))
    np.testing.assert_allclose(
        actual.values, _oracle(tn, tx, TIME), rtol=1e-9, equal_nan=True
    )
    # 2001 is entirely missing from April to September in the third cell.
    assert np.isnan(actual.values[0, 2])
    assert not np.isnan(actual.values[1, 2])


def test_bedd_missing_data_with_the_default_completeness() -> None:
    tn, tx = _data(nan=True)
    result = icclim.index(
        index_name="BEDD", in_files=_dataset(tn, tx, "degC", False), out_file=None
    ).BEDD.compute()
    assert np.isnan(result.values[0, 2])


def test_bedd_does_not_need_a_latitude() -> None:
    # The ATBD definition has no latitude coefficient: cells need no latitude.
    tn, tx = _data()
    result = _bedd(_dataset(tn, tx, "degC", chunked=False))
    assert result.dims == ("time", "x")
    assert not np.isnan(result.values).any()


def test_bedd_equals_the_xclim_icclim_method_without_missing_data() -> None:
    tn, tx = _data()
    ds = _dataset(tn, tx, "degC", chunked=False)
    expected = get_xclim_compute().biologically_effective_degree_days(
        tasmin=ds.tasmin,
        tasmax=ds.tasmax,
        method="icclim",
        start_date="04-01",
        end_date="10-01",
        freq="YS",
    )
    np.testing.assert_allclose(_bedd(ds).values, expected.values, rtol=1e-9)
