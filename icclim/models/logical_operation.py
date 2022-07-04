from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Callable

from icclim_exceptions import InvalidIcclimArgumentError
from xarray import DataArray


@dataclasses.dataclass
class Operator:
    short_name: str
    long_name: str
    standard_name: str
    operand: str
    compute: Callable[[DataArray, DataArray], DataArray]
    aliases: list[str]

    def __call__(self, *args, **kwargs):
        return self.compute(*args, **kwargs)


class LogicalOperation(Enum):
    def __init__(self, operator: Operator) -> None:
        super().__init__()
        self._operator = operator

    GREATER = Operator(
        short_name="gt",
        long_name="greater",
        standard_name="greater",
        aliases=["gt", ">"],
        operand=">",
        compute=lambda da, th: da > th,  # noqa
    )
    LOWER = Operator(
        short_name="lt",
        long_name="lower",
        standard_name="lower",
        aliases=["lt", "<"],
        operand="<",
        compute=lambda da, th: da < th,  # noqa
    )
    GREATER_OR_EQUAL = Operator(
        short_name="get",
        long_name="greater_or_equal",
        standard_name="greater_or_equal",
        aliases=["get", "ge", ">=", "=>"],
        operand=">=",
        compute=lambda da, th: da >= th,  # noqa
    )
    LOWER_OR_EQUAL = Operator(
        short_name="let",
        long_name="lower_or_equal",
        standard_name="lower_or_equal",
        aliases=["let", "le", "<=", "=<"],
        operand="<=",
        compute=lambda da, th: da <= th,  # noqa
    )
    EQUAL = Operator(
        short_name="e",
        long_name="equal",
        standard_name="equal",
        aliases=["e", "equal", "eq", "=", "=="],
        operand="==",
        compute=lambda da, th: da == th,  # noqa
    )

    @property
    def short_name(self):
        return self._operator.short_name

    @property
    def long_name(self):
        return self._operator.long_name

    @property
    def standard_name(self):
        return self._operator.standard_name

    @property
    def aliases(self):
        return self._operator.aliases

    @property
    def operand(self):
        return self._operator.operand

    @property
    def compute(self):
        return self._operator.compute

    def __call__(self, *args, **kwargs):
        return self._operator(*args, **kwargs)

    @staticmethod
    def lookup(query: str) -> LogicalOperation:
        for op in LogicalOperation:
            if query.upper() in map(str.upper, op.aliases):
                return op
        raise InvalidIcclimArgumentError(
            f"Unknown logical operator {query}."
            f"Use one of {[op.aliases for op in LogicalOperation]}."
        )
