from __future__ import annotations

import dataclasses
from typing import Callable

from xarray import DataArray

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.registry import Registry


def _reach_err(_, __):
    # can't raise error in lambda
    raise InvalidIcclimArgumentError(
        "Reach operator can't be called. Try to fill threshold with an operand"
        " (e.g. '>=' in '>= 22 degC')."
    )


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


class OperatorRegistry(Registry[Operator]):
    _item_class = Operator

    @staticmethod
    def get_item_aliases(op) -> list[str]:
        return list(map(str.upper, op.aliases))

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
    # A None operand means the threshold is reached and a reducer specific computation
    # is done. Case of excess and deficit (a.k.a gd4, hd17)
    REACH = Operator(
        short_name="reach",
        long_name="",  # nothing
        standard_name="reaching",
        aliases=["r"],
        operand="reach",
        compute=_reach_err,
    )
