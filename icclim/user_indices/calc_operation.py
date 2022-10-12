from __future__ import annotations

import dataclasses
from typing import Hashable, Literal

from icclim.models.registry import Registry

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
    name: str

    def __hash__(self):
        return hash(self.name)


class CalcOperationRegistry(Registry[CalcOperation]):
    # todo remove class once deprecation is finished (v6.1 ?)
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
