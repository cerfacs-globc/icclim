"""Contain the CalcOperationLike and CalcOperation classes."""

from __future__ import annotations

import dataclasses
from collections.abc import Hashable
from typing import Literal

from icclim._core.model.registry import Registry

CalcOperationLike = Literal[
    "max",
    "min",
    "sum",
    "mean",
    "nb_events",
    "max_nb_consecutive_events",
    "run_mean",
    "run_sum",
    "anomaly",
]


@dataclasses.dataclass
class CalcOperation(Hashable):
    """Represent a calculation operation for a user index."""

    name: str

    def __hash__(self) -> int:
        """Return the hash of the CalcOperation using its name."""
        return hash(self.name)


class CalcOperationRegistry(Registry[CalcOperation]):
    """Registry for CalcOperation instances."""

    _item_class = CalcOperation

    MAX = CalcOperation("max")
    MIN = CalcOperation("min")
    SUM = CalcOperation("sum")
    MEAN = CalcOperation("mean")
    EVENT_COUNT = CalcOperation("nb_events")
    MAX_NUMBER_OF_CONSECUTIVE_EVENTS = CalcOperation(
        "max_nb_consecutive_events",
    )
    RUN_MEAN = CalcOperation("run_mean")
    RUN_SUM = CalcOperation("run_sum")
    ANOMALY = CalcOperation("anomaly")
