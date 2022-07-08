from typing import Union

from xarray import DataArray

ThresholdType = Union[str, float, int, DataArray, None, tuple]

# todo move her eslice_mode and all the type of the public API
