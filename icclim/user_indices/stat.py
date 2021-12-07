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
    )


def get_index_of_longest_run(arr: Sequence[bool], window: int = 1) -> int:
    values, rl, pos = rle_1d(arr)
    if not np.any(values) or np.all(values * rl < window):  # type:ignore
        return 0
    index_of_max = np.nanargmax(
        np.where(values * rl >= window, rl, np.NaN)  # type:ignore
    )
    return pos[index_of_max]  # type:ignore


def get_first_occurrence_index(da: DataArray) -> DataArray:
    """
    Return the index of the first True value in the 3D booleans array along
    time dimension.
    """
    stacked = da.stack(latlon=("lat", "lon"))
    res = stacked.argmax("time")
    return res.unstack()
