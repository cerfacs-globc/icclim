from typing import Sequence, Tuple, Union

import numpy as np
import xarray
from xarray import DataArray
from xclim.indices.run_length import rle_1d


def get_longest_run_start_index(
    arr: Union[DataArray, Sequence[bool]],
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
    if not np.any(values) or np.all(values * rl < window):
        return 0
    index_of_max = np.nanargmax(np.where(values * rl >= window, rl, np.NaN))
    return pos[index_of_max]
