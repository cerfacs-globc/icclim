"""Type hints for icclim."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, Union

from xarray import DataArray, Dataset

from icclim._core.model.in_file_dictionary import InFileDictionary

InFileBaseType = Union[str, Sequence[str], Dataset, DataArray]
ThresholdedDict = dict[str, InFileDictionary]
InFileLike = Union[ThresholdedDict, InFileBaseType, dict[str, InFileBaseType]]

FrequencyLike = Union[str, list[str | tuple | int], tuple[str, list | tuple]]
# MonthsIndexer format: [12,1,2,3]
MonthsIndexer = dict[Literal["month"], Sequence[int]]
# DatesIndexer format: ("01-25", "02-28")
DatesIndexer = dict[Literal["date_bounds"], tuple[str, str]]
Indexer = Union[MonthsIndexer, DatesIndexer]

SamplingMethodLike = Literal["groupby", "resample", "groupby_ref_and_resample_study"]

ThresholdValueType = Union[
    str,
    float,
    int,
    Dataset,
    DataArray,
    Sequence[float | int | str],
    None,
]
