from __future__ import annotations

import datetime
from typing import Literal, TypedDict

from icclim.models.user_index_config import LogicalOperationLiteral
from icclim.user_indices.dispatcher import CalcOperationLiteral


class UserIndexDict(TypedDict):
    index_name: str
    calc_operation: CalcOperationLiteral
    logical_operation: LogicalOperationLiteral
    thresh: str | float
    link_logical_operations: Literal["and", "or"]
    extreme_mode: Literal["min", "max"]
    window_width: int
    coef: float
    date_event: bool
    var_type: Literal["t", "p"]
    ref_time_range: list[datetime.datetime]  # length of 2
