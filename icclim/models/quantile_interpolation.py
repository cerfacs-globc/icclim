from __future__ import annotations

import dataclasses

from icclim.models.registry import Registry


@dataclasses.dataclass
class QuantileInterpolation:
    name: str
    alpha: float
    beta: float


class QuantileInterpolationRegistry(Registry[QuantileInterpolation]):
    _item_class = QuantileInterpolation

    LINEAR = QuantileInterpolation("linear", 1, 1)
    MEDIAN_UNBIASED = QuantileInterpolation("median_unbiased", 1.0 / 3, 1.0 / 3)
