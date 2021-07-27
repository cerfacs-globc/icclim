from icclim.models.frequency import Frequency
from icclim.user_indice.user_indice import UserIndiceConfig
import xarray
import numpy as np
import pandas as pd
import copy

COORDS = dict(time=pd.date_range("2042-01-01", periods=366 * 5),)


STUB_USER_INDICE = UserIndiceConfig(
    indice_name="Yolo", calc_operation="noop", freq=Frequency.MONTH
)


def stub_user_indice():
    return copy.deepcopy(STUB_USER_INDICE)


def stub_da():
    return xarray.DataArray(data=np.full(366 * 5, 1), dims=["time"], coords=COORDS)


def stub_pr(val):
    return xarray.DataArray(
        np.full(366 * 5, val),
        coords=COORDS,
        dims="time",
        name="pr",
        attrs={
            "standard_name": "precipitation_flux",
            "cell_methods": "time: mean within days",
            "units": "kg m-2 d-1",
        },
    )
