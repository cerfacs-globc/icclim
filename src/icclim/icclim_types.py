from __future__ import annotations

from typing import Dict, List, Literal, Sequence, Tuple, Union

from xarray import DataArray, Dataset

InFileBaseType = Union[str, Sequence[str], Dataset, DataArray]
ThresholdedDict = Dict[str, Union[Dict]]  # Dict === InFileDictionary
InFileLike = Union[ThresholdedDict, InFileBaseType, Dict[str, InFileBaseType]]

FrequencyLike = Union[str, List[Union[str, Tuple, int]], Tuple[str, Union[List, Tuple]]]
# MonthsIndexer format: [12,1,2,3]
MonthsIndexer = Dict[Literal["month"], Sequence[int]]
# DatesIndexer format: ("01-25", "02-28")
DatesIndexer = Dict[Literal["date_bounds"], Tuple[str, str]]
Indexer = Union[MonthsIndexer, DatesIndexer]

SamplingMethodLike = Literal["groupby", "resample", "groupby_ref_and_resample_study"]

ThresholdValueType = Union[
    str, float, int, Dataset, DataArray, Sequence[Union[float, int, str]], None
]
