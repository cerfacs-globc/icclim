from typing import List

import numpy as np
import pandas as pd
import xarray

from icclim.models.frequency import Frequency
from icclim.models.indice_config import CfVariable
from icclim.models.user_indice_config import UserIndiceConfig

VALUE_COUNT = 365 * 5 + 1
COORDS = dict(
    lat=[42],
    lon=[42],
    time=pd.date_range("2042-01-01", periods=VALUE_COUNT, freq=pd.DateOffset(days=1)),
)


def stub_user_indice(cf_vars: List[CfVariable]):
    return UserIndiceConfig(
        indice_name="Yolo", calc_operation="noop", freq=Frequency.MONTH, cf_vars=cf_vars
    )


def stub_tas(value: float = 1):
    return xarray.DataArray(
        data=(np.full(VALUE_COUNT, value).reshape((VALUE_COUNT, 1, 1))),
        dims=["time", "lat", "lon"],
        coords=COORDS,
        attrs={"units": "K"},
    )


def stub_pr(value: float):
    return xarray.DataArray(
        data=(np.full(VALUE_COUNT, value).reshape((VALUE_COUNT, 1, 1))),
        coords=COORDS,
        dims=["time", "lat", "lon"],
        name="pr",
        attrs={"units": "kg m-2 d-1"},
    )
