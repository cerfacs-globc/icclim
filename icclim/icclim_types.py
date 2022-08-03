from __future__ import annotations

from typing import Callable, Dict, List, Literal, Sequence, Tuple, Union

from xarray import DataArray, Dataset

InFileBaseType = Union[str, List[str], Dataset, DataArray]
InFileType = Union[Dict[str, Union[Dict, InFileBaseType]], InFileBaseType]

FrequencyLike = Union[str, List[Union[str, Tuple, int]], Tuple[str, Union[List, Tuple]]]
MonthsIndexer = Dict[Literal["month"], Sequence[int]]  # format [12,1,2,3]
DatesIndexer = Dict[
    Literal["date_bounds"], Tuple[str, str]
]  # format ("01-25", "02-28")
ClippedSeasonIndexer = Callable
Indexer = Union[MonthsIndexer, DatesIndexer, ClippedSeasonIndexer]


# todo Move other types here.
#      No import allowed to other icclim modules allowed !
