from icclim.models.frequency import Frequency
from typing import List, Optional
from xarray import DataArray
from xarray.core.dataset import Dataset


class CfVariable:
    da: DataArray
    in_base_da: Optional[DataArray]

    def __init__(self, da: DataArray, in_base_da: DataArray = None) -> None:
        self.da = da
        self.in_base_da = in_base_da


class IndiceConfig:
    freq: Frequency
    window: Optional[int]
    threshold: Optional[int]
    cfvariables: List[CfVariable]
    ds: Dataset
