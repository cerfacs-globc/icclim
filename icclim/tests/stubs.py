import numpy as np
import pandas as pd
import xarray

from icclim.models.frequency import Frequency
from icclim.user_indice.user_indice import UserIndiceConfig

COORDS = dict(
    time=pd.date_range("2042-01-01", periods=365 * 5 + 1, freq=pd.DateOffset(days=1))
)


def stub_user_indice():
    return UserIndiceConfig(
        indice_name="Yolo", calc_operation="noop", freq=Frequency.MONTH
    )


def stub_tas(value=1):
    return xarray.DataArray(
        data=np.full(365 * 5 + 1, value),
        dims=["time"],
        coords=COORDS,
        attrs={
            "units": "K",
        },
    )


def stub_pr(val):
    return xarray.DataArray(
        np.full(365 * 5 + 1, val),
        coords=COORDS,
        dims="time",
        name="pr",
        attrs={
            "units": "kg m-2 d-1",
        },
    )
