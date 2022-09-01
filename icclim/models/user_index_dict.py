from __future__ import annotations

import datetime
from typing import Literal, Sequence, TypedDict

from icclim.models.logical_link import LogicalLink
from icclim.user_indices.calc_operation import CalcOperation, CalcOperationLike


class UserIndexDict(TypedDict, total=False):
    index_name: str
    calc_operation: CalcOperationLike | CalcOperation
    logical_operation: str | None | Sequence[str]  # >= | <= | ...| ==
    thresh: str | float | int | Sequence[str] | Sequence[float] | Sequence[int] | None
    extreme_mode: Literal["min", "max"] | None

    link_logical_operations: Literal["and", "or"] | LogicalLink | None
    coef: float | None
    date_event: bool
    var_type: Literal["t", "p"] | None
    window_width: int | None
    ref_time_range: list[datetime] | list[str] | tuple[str, str] | None

    # -- deprecated
    indice_name: str | None
