import numpy as np
import pandas as pd
import xarray

from icclim.models.frequency import Frequency
from icclim.user_indice.user_indice import UserIndiceConfig

COORDS = dict(
    time=pd.date_range("2042-01-01", periods=366 * 5),
)


def stub_user_indice():
    return UserIndiceConfig(
        indice_name="Yolo", calc_operation="noop", freq=Frequency.MONTH
    )


def stub_da(value=1):
    return xarray.DataArray(data=np.full(366 * 5, value), dims=["time"], coords=COORDS)


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
