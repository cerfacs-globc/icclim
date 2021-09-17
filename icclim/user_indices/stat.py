from typing import Sequence

import numpy as np
import xarray
from xarray import DataArray
from xclim.indices.run_length import rle_1d


def get_longest_run_start_index(
    arr: DataArray,
    window: int = 1,
    dim: str = "time",
) -> DataArray:
    return xarray.apply_ufunc(
        get_index_of_longest_run,
        arr,
        input_core_dims=[[dim]],
        kwargs={"window": window},
        vectorize=True,
        dask="parallelized",
        output_dtypes=[float],
        keep_attrs=True,
    )


def get_index_of_longest_run(arr: Sequence[bool], window: int = 1) -> int:
    values, rl, pos = rle_1d(arr)
    if not np.any(values) or np.all(values * rl < window):  # type:ignore
        return 0
    index_of_max = np.nanargmax(
        np.where(values * rl >= window, rl, np.NaN)  # type:ignore
    )
    return pos[index_of_max]  # type:ignore


def get_first_occurrence(da: DataArray) -> DataArray:
    """
    Return the first occurrence (index) of val in the 3D array along axis=0

    arr is a binary (0/1) 3D array

    """
    stacked = da.stack(latlon=("lat", "lon"))
    res = stacked.argmax("time")

    # TODO probably useless to set all False value to -1 instead of 0,
    #      because with -1 it puts the last date of the month instead of the first one for theses values,
    #      and we simply don't care what value they hold
    test_res = stacked.sum("time") + res
    res[test_res == 0] = -1

    return res.unstack()
