import dataclasses
from typing import List, Optional
from xarray import DataArray


@dataclasses.dataclass
class IndiceConfig:
    data_arrays: List[DataArray]
    freq: str
    data_arrays_in_base: Optional[List[DataArray]]
    window: Optional[int]
    threshold: Optional[int]
