"""Contain the UserIndexDict TypedDict."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import Sequence

    from icclim._core.legacy.user_index.calc_operation import (
        CalcOperation,
        CalcOperationLike,
    )
    from icclim._core.model.logical_link import LogicalLink


class UserIndexDict(TypedDict, total=False):
    """
    User index dictionary.

    This dictionary is used to describe how a user index should be setup to compute a
    custom climate index.
    The reccomended way to create a custom indices is now to use the
    generic indices API.
    See :ref:`generic_indices_recipes` for how to combine thresholds with generic
    """

    index_name: str
    calc_operation: CalcOperationLike | CalcOperation
    logical_operation: str | None | Sequence[str]  # >= | <= | ...| ==
    thresh: str | int | Sequence[str | int] | None
    extreme_mode: Literal["min", "max"] | None

    link_logical_operations: Literal["and", "or"] | LogicalLink | None
    coef: float | None
    date_event: bool
    var_type: Literal["t", "p"] | None
    window_width: int | None
    ref_time_range: Sequence[dt.datetime] | Sequence[str] | tuple[str, str] | None

    # -- deprecated
    indice_name: str | None
