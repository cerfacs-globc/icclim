from __future__ import annotations

from typing import Dict, List, Union

from xarray import DataArray, Dataset

InFileBaseType = Union[str, List[str], Dataset, DataArray]
InFileType = Union[Dict[str, Union[Dict, InFileBaseType]], InFileBaseType]

# todo move here slice_mode and every type of the public API
