import datetime
from icclim.models.frequency import Frequency
from typing import List, Tuple, Union


SliceMode = Union[Frequency, str, List[Union[str, Tuple, int]]]
