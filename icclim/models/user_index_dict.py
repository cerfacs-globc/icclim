from __future__ import annotations

import datetime
from typing import Literal, TypedDict

from icclim.user_indices.calc_operation import CalcOperation, CalcOperationLiteral


class UserIndexDict(TypedDict, total=False):
    index_name: str
    calc_operation: CalcOperationLiteral | CalcOperation
    logical_operation: str | None  # >= | <= | ...| ==
    thresh: str | float | None
    extreme_mode: Literal["min", "max"] | None

    link_logical_operations: Literal[
        "and", "or"
    ] | None  # todo what do we do with that ?
    coef: float | None  # todo what do we do with that ?
    date_event: bool | None  # todo what do we do with that ?

    # -- deprecated
    indice_name: str | None
    # var_type is ignored in the new API
    # -> use a proper Threshold instead
    var_type: Literal["t", "p"] | None
    # window_width is ignored in the new API
    # -> we use the icclim::index window_width
    window_width: int | None
    # ref_time_range is ignored in the new API
    # -> we use the icclim::index base_period_time_range
    ref_time_range: list[datetime] | list[str] | tuple[str, str] | None
