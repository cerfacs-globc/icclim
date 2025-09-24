"""Contain the LogicalLink class and registry."""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from functools import reduce
from typing import TYPE_CHECKING

import numpy as np

from icclim._core.model.registry import Registry

if TYPE_CHECKING:
    from xarray import DataArray


@dataclasses.dataclass
class LogicalLink:
    """Logical link class to combine multiple threshold.

    This is meant to be used with the old user_indices API.
    It is now reccomended to use BoundedThreshold with generic indices instead.
    See :ref:`generic_indices_recipes` for how to combine thresholds with generic
    indices.
    """

    name: str
    standard_name: str
    long_name: str
    short_name: str
    compute: Callable[[list[DataArray]], DataArray]

    def __call__(self, *args, **kwargs) -> DataArray:
        """Compute the logical "and" or "or" of the input data."""
        return self.compute(*args, **kwargs)


class LogicalLinkRegistry(Registry[LogicalLink]):
    """Registry for LogicalLink objects."""

    _item_class = LogicalLink

    LOGICAL_OR = LogicalLink(
        name="or",
        standard_name="OR",
        long_name="OR",
        short_name="OR",
        compute=lambda data_list: reduce(np.logical_or, data_list),
    )
    LOGICAL_AND = LogicalLink(
        name="and",
        standard_name="AND",
        long_name="AND",
        short_name="AND",
        compute=lambda data_list: reduce(np.logical_and, data_list),
    )
