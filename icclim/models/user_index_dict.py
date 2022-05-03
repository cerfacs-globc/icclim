from __future__ import annotations

import datetime
from typing import Literal, TypedDict

from icclim.models.user_index_config import LogicalOperationLiteral
from icclim.user_indices.calc_operation import CalcOperation, CalcOperationLiteral


class UserIndexDict(TypedDict, total=False):
    index_name: str
    calc_operation: CalcOperationLiteral | CalcOperation
    logical_operation: LogicalOperationLiteral | None
    thresh: str | float | None
    link_logical_operations: Literal["and", "or"] | None
    extreme_mode: Literal["min", "max"] | None
    window_width: int | None
    coef: float | None
    date_event: bool | None
    var_type: Literal["t", "p"] | None
    ref_time_range: list[datetime.datetime] | None  # length of 2
    # deprecated
    indice_name: str | None
