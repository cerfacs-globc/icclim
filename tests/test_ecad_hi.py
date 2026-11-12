"""
Huglin Index (HI) against the ECA&D ATBD v11 definition (issue #637).

ATBD: HI = sum over 1 April to 30 September of ((TG - 10) + (TX - 10)) / 2 * K, TG
being the daily mean and TX the daily maximum temperature, K the daylength coefficient
of the latitude: 1.00 up to 40 N, 1.02 for 40-42 N, 1.03 for 42-44 N, 1.04 for
44-46 N, 1.05 for 46-48 N and 1.06 for 48-50 N (no value above 50 N). The oracle
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
from icclim.exception import InvalidIcclimArgumentError

LATITUDES = [35.0, 40.0, 41.0, 43.5, 45.0, 47.0, 49.0, 50.0, 52.0]
TIME = pd.date_range("2001-01-01", "2002-12-31")


ATBD_K_TABLE = [
    (40, 1.00),
    (42, 1.02),
    (44, 1.03),
    (46, 1.04),
    (48, 1.05),
    (50, 1.06),
]


def _atbd_k(latitude: float) -> float:
    for upper, k in ATBD_K_TABLE:
        if latitude <= upper:
            return k
    return float("nan")  # the ATBD gives no value above 50 degrees north


def _oracle(tg, tx, time, latitudes) -> np.ndarray:
    """HI per year and latitude, from the ATBD text; NaN days are not summed."""
    result = np.full((2, len(latitudes)), np.nan)
    for year_index, year in enumerate((2001, 2002)):
        for j, latitude in enumerate(latitudes):
            total, any_day = 0.0, False
            for i, day in enumerate(time):
                d = dt.date(day.year, day.month, day.day)
                if not dt.date(year, 4, 1) <= d <= dt.date(year, 9, 30):
                    continue
                if np.isnan(tg[i, j]) or np.isnan(tx[i, j]):
                    continue
                total += ((tg[i, j] - 10) + (tx[i, j] - 10)) / 2 * _atbd_k(latitude)
                any_day = True
            if any_day:
                result[year_index, j] = total
    return result


def _data(nan: bool = False):
    rng = np.random.default_rng(7)
    # Cold spring days make some daily terms negative: the ATBD sum has no clipping.
    seasonal = 10 + 12 * np.sin(2 * np.pi * (TIME.dayofyear.values - 100) / 365)
    tg = seasonal[:, None] + rng.uniform(-3, 3, (len(TIME), len(LATITUDES)))
    tx = tg + rng.uniform(2, 8, tg.shape)
    if nan:
        tg[(TIME >= "2002-06-01") & (TIME <= "2002-06-03"), 2] = np.nan
        tx[(TIME >= "2001-04-01") & (TIME <= "2001-09-30"), 3] = np.nan
    return tg, tx


def _dataset(tg, tx, unit: str, chunked: bool) -> xr.Dataset:
    offset = 273.15 if unit == "K" else 0.0
    coords = {"time": TIME, "lat": LATITUDES}
    ds = xr.Dataset(
        {
            "tas": xr.DataArray(
                tg + offset,
                dims=("time", "lat"),
                coords=coords,
                attrs={"units": unit},
            ),
            "tasmax": xr.DataArray(
                tx + offset,
                dims=("time", "lat"),
                coords=coords,
                attrs={"units": unit},
            ),
        }
    )
    return ds.chunk({"lat": 3}) if chunked else ds


def _hi(ds: xr.Dataset, **kwargs) -> xr.DataArray:
    kwargs.setdefault("completeness", "none")
    return icclim.index(
        index_name="HI", in_files=ds, out_file=None, **kwargs
    ).HI.compute()


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("unit", ["degC", "K"])
def test_hi_matches_the_atbd_oracle(unit: str, chunked: bool) -> None:
    tg, tx = _data()
    actual = _hi(_dataset(tg, tx, unit, chunked))
    expected = _oracle(tg, tx, TIME, LATITUDES)
    np.testing.assert_allclose(actual.values, expected, rtol=1e-9, equal_nan=True)
    # No value above 50 degrees north (ATBD table 2), including 52 N.
    assert np.isnan(actual.values[:, LATITUDES.index(52.0)]).all()
    assert not np.isnan(actual.values[:, LATITUDES.index(50.0)]).any()
    # The text of the units depends on the pint format: compare the dimensions.
    assert (
        units2pint(actual.attrs["units"]).dimensionality
        == units2pint("K d").dimensionality
    )


def test_hi_is_not_clipped_at_zero_like_xclim() -> None:
    # A cold spring: negative daily terms must lower the sum (ATBD formula).
    tg, tx = _data()
    actual = _hi(_dataset(tg, tx, "degC", chunked=False))
    clipped = np.zeros_like(actual.values)
    for year_index, year in enumerate((2001, 2002)):
        season = (f"{year}-04-01" <= TIME) & (f"{year}-09-30" >= TIME)
        daily = ((tg[season] - 10) + (tx[season] - 10)) / 2
        assert (daily < 0).any()
        clipped[year_index] = np.clip(daily, 0, None).sum(axis=0) * np.array(
            [_atbd_k(lat) for lat in LATITUDES]
        )
    assert not np.allclose(actual.values[:, :-1], clipped[:, :-1])


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("unit", ["degC", "K"])
def test_hi_nan_handling(unit: str, chunked: bool) -> None:
    tg, tx = _data(nan=True)
    actual = _hi(_dataset(tg, tx, unit, chunked))
    expected = _oracle(tg, tx, TIME, LATITUDES)
    np.testing.assert_allclose(actual.values, expected, rtol=1e-9, equal_nan=True)
    # 2001 is entirely missing from April to September at latitude 43.5.
    assert np.isnan(actual.values[0, LATITUDES.index(43.5)])
    assert not np.isnan(actual.values[1, LATITUDES.index(43.5)])


def test_hi_missing_data_with_the_default_completeness() -> None:
    tg, tx = _data(nan=True)
    ds = _dataset(tg, tx, "degC", chunked=False)
    result = icclim.index(index_name="HI", in_files=ds, out_file=None).HI.compute()
    # The year without any valid day in the season is masked by the default policy.
    assert np.isnan(result.values[0, LATITUDES.index(43.5)])


def test_hi_takes_the_latitude_from_the_data_coordinates() -> None:
    tg, tx = _data()
    ds = _dataset(tg, tx, "degC", chunked=False)
    reference = _hi(ds)
    # A coordinate that is not called lat, found through its units.
    renamed = ds.rename({"lat": "y"})
    renamed["y"].attrs["units"] = "degrees_north"
    np.testing.assert_allclose(
        _hi(renamed).values, reference.values, rtol=1e-12, equal_nan=True
    )
    # The same coordinate called latitude.
    np.testing.assert_allclose(
        _hi(ds.rename({"lat": "latitude"})).values,
        reference.values,
        rtol=1e-12,
        equal_nan=True,
    )
    # Another latitude gives another K.
    shifted = ds.assign_coords(lat=[lat - 5 for lat in LATITUDES])
    assert not np.allclose(_hi(shifted).values, reference.values, equal_nan=True)


def test_hi_without_a_latitude_gives_a_clear_error() -> None:
    tg, tx = _data()
    ds = _dataset(tg, tx, "degC", chunked=False).rename({"lat": "station"})
    with pytest.raises(InvalidIcclimArgumentError, match="latitude"):
        _hi(ds)
