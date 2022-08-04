from __future__ import annotations

import dataclasses
from typing import Callable

from xarray import DataArray

from icclim.models.registry import Registry


@dataclasses.dataclass
class Operator:
    short_name: str
    long_name: str
    standard_name: str
    operand: str
    compute: Callable[[DataArray, DataArray | int | float], DataArray]
    aliases: list[str]

    def __call__(self, *args, **kwargs):
        return self.compute(*args, **kwargs)


class OperatorRegistry(Registry):
    _item_class = Operator

    @staticmethod
    def get_item_aliases(op):
        return op.aliases

    GREATER = Operator(
        short_name="gt",
        long_name="greater than",
        standard_name="greater_than",
        aliases=["gt", ">"],
        operand=">",
        compute=lambda da, th: da > th,  # noqa
    )
    LOWER = Operator(
        short_name="lt",
        long_name="lower than",
        standard_name="lower_than",
        aliases=["lt", "<"],
        operand="<",
        compute=lambda da, th: da < th,  # noqa
    )
    GREATER_OR_EQUAL = Operator(
        short_name="get",
        long_name="greater or equal to",
        standard_name="greater_or_equal_to",
        aliases=["get", "ge", ">=", "=>"],
        operand=">=",
        compute=lambda da, th: da >= th,  # noqa
    )
    LOWER_OR_EQUAL = Operator(
        short_name="let",
        long_name="lower or equal to",
        standard_name="lower_or_equal_to",
        aliases=["let", "le", "<=", "=<"],
        operand="<=",
        compute=lambda da, th: da <= th,  # noqa
    )
    EQUAL = Operator(
        short_name="e",
        long_name="equal to",
        standard_name="equal_to",
        aliases=["e", "equal", "eq", "=", "=="],
        operand="==",
        compute=lambda da, th: da == th,  # noqa
    )