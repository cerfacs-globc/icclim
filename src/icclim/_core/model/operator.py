"""Module for the Operator class and OperatorRegistry."""

from __future__ import annotations

import dataclasses
import operator
from collections.abc import Callable
from typing import TYPE_CHECKING, NoReturn

from icclim._core.model.registry import Registry
from icclim.exception import InvalidIcclimArgumentError

if TYPE_CHECKING:
    from xarray import DataArray


def _reach_err(_: object, __: object) -> NoReturn:
    # can't raise error in lambda
    msg = (
        "Reach operator can't be called. Try to fill threshold with an operand"
        " (e.g. '>=' in '>= 22 degC')."
    )
    raise InvalidIcclimArgumentError(msg)


@dataclasses.dataclass
class Operator:
    """
    Represents an operator used in computations.

    Parameters
    ----------
    short_name : str
        The short name of the operator,
        used when templating the output metadata.
    long_name : str
        The long name of the operator,
        used when templating the output metadata.
    standard_name : str
        The standard name of the operator,
        used when templating the output metadata.
    operand : str
        The operand symbol of the operator.
    compute : Callable[[DataArray, DataArray | int | float], DataArray]
        The computation function of the operator.
    aliases : list[str]
        The list of aliases for the operator.
    """

    short_name: str
    long_name: str
    standard_name: str
    operand: str
    compute: Callable[[DataArray, DataArray | int | float], DataArray]
    aliases: list[str]

    def __call__(self, *args, **kwargs) -> DataArray:
        """
        Call the computation function of the operator.

        Parameters
        ----------
        *args : tuple
            Positional arguments passed to the computation function.
        **kwargs : dict
            Keyword arguments passed to the computation function.

        Returns
        -------
        DataArray
            The result of the computation.

        """
        return self.compute(*args, **kwargs)


class OperatorRegistry(Registry[Operator]):
    """
    Registry of operators.

    Contains the predefined operators used to build ``Threshold``.
    """

    _item_class = Operator

    @staticmethod
    def get_item_aliases(op: Operator) -> list[str]:
        """
        Get the aliases of an operator.

        Parameters
        ----------
        op : Operator
            The operator.

        Returns
        -------
        list[str]
            The list of aliases for the operator.
        """
        return list(map(str.upper, op.aliases))

    GREATER = Operator(
        short_name="gt",
        long_name="greater than",
        standard_name="greater_than",
        aliases=["gt", ">"],
        operand=">",
        compute=operator.gt,
    )
    LOWER = Operator(
        short_name="lt",
        long_name="lower than",
        standard_name="lower_than",
        aliases=["lt", "<"],
        operand="<",
        compute=operator.lt,
    )
    GREATER_OR_EQUAL = Operator(
        short_name="get",
        long_name="greater or equal to",
        standard_name="greater_or_equal_to",
        aliases=["get", "ge", ">=", "=>"],
        operand=">=",
        compute=operator.ge,
    )
    LOWER_OR_EQUAL = Operator(
        short_name="let",
        long_name="lower or equal to",
        standard_name="lower_or_equal_to",
        aliases=["let", "le", "<=", "=<"],
        operand="<=",
        compute=operator.le,
    )
    EQUAL = Operator(
        short_name="e",
        long_name="equal to",
        standard_name="equal_to",
        aliases=["e", "equal", "eq", "=", "=="],
        operand="==",
        compute=operator.eq,
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
