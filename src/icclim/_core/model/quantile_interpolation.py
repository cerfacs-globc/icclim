"""
Contain the classes for quantile interpolation.

QuantileInterpolation class and the QuantileInterpolationRegistry class
are defined here.
"""

from __future__ import annotations

import dataclasses

from icclim._core.model.registry import Registry


@dataclasses.dataclass
class QuantileInterpolation:
    """
    Class for performing quantile interpolation.

    Parameters
    ----------
    name : str
        The name of the interpolation method.
    alpha : float
        The alpha parameter for the interpolation.
    beta : float
        The beta parameter for the interpolation.
    """

    name: str
    alpha: float
    beta: float


class QuantileInterpolationRegistry(Registry[QuantileInterpolation]):
    """
    Registry of quantile interpolation methods.

    Only 2 methods are available: LINEAR and MEDIAN_UNBIASED.
    """

    _item_class = QuantileInterpolation

    LINEAR = QuantileInterpolation("linear", 1, 1)
    MEDIAN_UNBIASED = QuantileInterpolation("median_unbiased", 1.0 / 3, 1.0 / 3)
