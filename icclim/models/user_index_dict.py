import datetime
from typing import List, Literal, TypedDict, Union

from icclim.models.user_index_config import LogicalOperationLiteral
from icclim.user_indices.dispatcher import CalcOperationLiteral


class UserIndexDict(TypedDict):
    index_name: str
    calc_operation: CalcOperationLiteral
    logical_operation: LogicalOperationLiteral
    thresh: Union[str, float]
    link_logical_operations: Literal["and", "or"]
    extreme_mode: Literal["min", "max"]
    window_width: int
    coef: float
    date_event: bool
    var_type: Literal["t", "p"]
    ref_time_range: List[datetime.datetime]  # length of 2 (todo should be a tuple)
