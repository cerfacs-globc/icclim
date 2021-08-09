from typing import List, Optional

from xarray import DataArray

from icclim.models.frequency import Frequency


class CfVariable:
    da: DataArray
    in_base_da: Optional[DataArray] = None

    def __init__(self, da: DataArray, in_base_da: DataArray = None) -> None:
        self.da = da
        self.in_base_da = in_base_da


class IndiceConfig:
    freq: Frequency
    window: Optional[int]
    threshold: Optional[str]
    cf_variables: List[CfVariable]
    save_percentile: bool = False
    is_percent: bool = False
