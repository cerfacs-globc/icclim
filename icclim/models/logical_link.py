from __future__ import annotations

import dataclasses
from functools import reduce
from typing import Callable

import numpy as np
from xarray import DataArray

from icclim.models.registry import Registry


@dataclasses.dataclass
class LogicalLink:
    name: str
    compute: Callable[[list[DataArray]], DataArray]

    def __call__(self, *args, **kwargs) -> DataArray:
        return self.compute(*args, **kwargs)


class LogicalLinkRegistry(Registry[LogicalLink]):
    _item_class = LogicalLink

    LOGICAL_OR = LogicalLink(
        name="or",
        compute=lambda data_list: reduce(np.logical_or, data_list),  # type:ignore
    )
    LOGICAL_AND = LogicalLink(
        name="and",
        compute=lambda data_list: reduce(np.logical_and, data_list),  # type:ignore
    )
