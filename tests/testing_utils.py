from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr
from icclim._core.constants import UNITS_KEY

VALUE_COUNT = 365 * 5 + 1  # 5 years of data (with 1 leap year)
K2C = 273.15

CF_TIME_RANGE = xr.cftime_range("2042-01-01", periods=VALUE_COUNT, freq="D")


def _get_coords(lat_lengh: int, lon_length: int, time_length: int):
    return {
        "lat": np.arange(lat_lengh),
        "lon": np.arange(lon_length),
        "time": pd.date_range("2042-01-01", periods=time_length, freq="D"),
    }


def stub_tas(
    tas_value: float = 1.0,
    use_dask=False,
    use_cftime=False,
    lat_length: int = 1,
    lon_length: int = 1,
):
    da = xr.DataArray(
        data=(
            np.full((VALUE_COUNT, lat_length, lon_length), tas_value).reshape(
                (VALUE_COUNT, lat_length, lon_length)
            )
        ),
        dims=["time", "lat", "lon"],
        coords=_get_coords(
            lat_lengh=lat_length, lon_length=lon_length, time_length=VALUE_COUNT
        ),
        attrs={UNITS_KEY: "K"},
    )
    if use_cftime:
        da["time"] = CF_TIME_RANGE
    if use_dask:
        da.chunk()
    return da


def stub_pr(value: float, use_dask=False, lat=1, lon=1):
    da = xr.DataArray(
        data=np.full(VALUE_COUNT, value).reshape((VALUE_COUNT, 1, 1)),
        coords=_get_coords(lat_lengh=lat, lon_length=lon, time_length=VALUE_COUNT),
        dims=["time", "lat", "lon"],
        name="pr",
        attrs={UNITS_KEY: "kg m-2 s-1"},
    )
    if use_dask:
        da.chunk()
    return da
