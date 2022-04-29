from typing import List

import numpy as np
import pandas as pd
import xarray

from icclim.models.frequency import Frequency
from icclim.models.index_config import CfVariable
from icclim.models.user_index_config import UserIndexConfig

VALUE_COUNT = 365 * 5 + 1
COORDS = dict(
    lat=[42],
    lon=[42],
    time=pd.date_range("2042-01-01", periods=VALUE_COUNT, freq="D"),
)
K2C = 273.15


def stub_user_index(cf_vars: List[CfVariable]):
    return UserIndexConfig(
        index_name="Yolo", calc_operation="noop", freq=Frequency.MONTH, cf_vars=cf_vars
    )


def stub_tas(tas_value: float = 1.0, use_dask=False):
    da = xarray.DataArray(
        data=(np.full(VALUE_COUNT, tas_value).reshape((VALUE_COUNT, 1, 1))),
        dims=["time", "lat", "lon"],
        coords=COORDS,
        attrs={"units": "K"},
    )
    if use_dask:
        da.chunk()
    return da


def stub_pr(value: float, use_dask=False):
    da = xarray.DataArray(
        data=np.full(VALUE_COUNT, value).reshape((VALUE_COUNT, 1, 1)),
        coords=COORDS,
        dims=["time", "lat", "lon"],
        name="pr",
        attrs={"units": "kg m-2 d-1"},
    )
    if use_dask:
        da.chunk()
    return da
