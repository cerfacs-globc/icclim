from icclim.user_indice.user_indice import UserIndice
import xarray
import numpy as np
import pandas as pd
import copy

STUB_DA = xarray.DataArray(
    data=np.full(366 * 5, 1),
    dims=["time"],
    coords=dict(time=pd.date_range("2042-01-01", periods=366 * 5),),
)

STUB_USER_INDICE = UserIndice(indice_name="Yolo", calc_operation="noop")


def stub_user_indice():
    return copy.deepcopy(STUB_USER_INDICE)


def stub_da():
    return copy.deepcopy(STUB_DA)
