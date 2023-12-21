from __future__ import annotations

import dataclasses
from functools import reduce
from typing import TYPE_CHECKING, Callable

import numpy as np

from icclim.models.registry import Registry

if TYPE_CHECKING:
    from xarray import DataArray


@dataclasses.dataclass
class LogicalLink:
    name: str
    standard_name: str
    long_name: str
    short_name: str
    compute: Callable[[list[DataArray]], DataArray]

    def __call__(self, *args, **kwargs) -> DataArray:
        return self.compute(*args, **kwargs)


class LogicalLinkRegistry(Registry[LogicalLink]):
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
