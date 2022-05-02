from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Literal

from xarray.core.dataarray import DataArray

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.frequency import Frequency
from icclim.models.index_config import CfVariable

LogicalOperationLiteral = Literal[
    "gt",
    ">",
    "lt",
    "<",
    "get",
    "ge",
    ">=",
    "=>",
    "let",
    "le",
    "<=",
    "=<",
    "e",
    "equal",
    "eq",
    "=",
    "==",
]


class LinkLogicalOperation(Enum):
    OR_STAMP = "or"
    AND_STAMP = "and"

    @staticmethod
    def lookup(query: str) -> LinkLogicalOperation:
        for mode in LinkLogicalOperation:
            if query.upper == mode.value.upper():
                return mode
        raise InvalidIcclimArgumentError(
            f"Unknown link_logical_operation mode {query}."
            f"Use one of {[linkOp.value for linkOp in LinkLogicalOperation]}."
        )


class ExtremeMode(Enum):
    MIN = "min"
    MAX = "max"

    @staticmethod
    def lookup(query: str) -> ExtremeMode:
        for mode in ExtremeMode:
            if query.upper() == mode.value.upper():
                return mode
        raise InvalidIcclimArgumentError(
            f"Unknown extreme_mode {query}."
            f" Use one of {[mode.value for mode in ExtremeMode]}."
        )


class LogicalOperation(Enum):
    GREATER_THAN = (["gt", ">"], ">", lambda da, th: da > th)
    LOWER_THAN = (["lt", "<"], "<", lambda da, th: da < th)
    GREATER_OR_EQUAL_THAN = (["get", "ge", ">=", "=>"], ">=", lambda da, th: da >= th)
    LOWER_OR_EQUAL_THAN = (["let", "le", "<=", "=<"], "<=", lambda da, th: da <= th)
    EQUAL = (["e", "equal", "eq", "=", "=="], "==", lambda da, th: da == th)

    def __init__(
        self,
        aliases: str,
        operator: str,
        compute: Callable[[DataArray, DataArray | float | int], DataArray],
    ) -> None:
        super().__init__()
        self.aliases = aliases
        self.operator = operator
        self.compute = compute

    @staticmethod
    def lookup(query: str) -> LogicalOperation:
        for op in LogicalOperation:
            if query.upper() in map(str.upper, op.aliases):
                return op
        raise InvalidIcclimArgumentError(
            f"Unknown logical operator {query}."
            f"Use one of {[op.aliases for op in LogicalOperation]}."
        )


@dataclass
class NbEventConfig:
    logical_operation: list[LogicalOperation]
    thresholds: list[float | str]
    link_logical_operations: LinkLogicalOperation | None = None
    data_arrays: list[CfVariable] | None = None


@dataclass
class UserIndexConfig:
    index_name: str
    calc_operation: str
    cf_vars: list[CfVariable]
    freq: Frequency
    date_event: bool
    is_percent: bool
    logical_operation: LogicalOperation | None = None
    thresh: float | int | str | list[float | int | str] | None = None
    link_logical_operations: LinkLogicalOperation | None = None
    extreme_mode: ExtremeMode | None = None
    window_width: int | None = None
    coef: float | None = None
    var_type: str | None = None
    nb_event_config: NbEventConfig | None = None
    save_percentile: bool = False

    def __init__(
        self,
        index_name: str,
        # Any should be CalcOperation but it causes circular import
        calc_operation: str | Any,
        freq: Frequency,
        cf_vars: list[CfVariable],
        logical_operation: str = None,
        thresh=None,
        link_logical_operations: str = None,
        extreme_mode: str = None,
        window_width=None,
        coef=None,
        date_event=None,
        var_type=None,
        is_percent=False,
        save_percentile=False,
        ref_time_range: list[str] = None,
    ) -> None:
        self.index_name = index_name
        self.calc_operation = calc_operation
        self.freq = freq
        if logical_operation is not None:
            self.logical_operation = LogicalOperation.lookup(logical_operation)
        self.thresh = thresh
        if extreme_mode is not None:
            self.extreme_mode = ExtremeMode.lookup(extreme_mode)
        self.window_width = window_width
        self.coef = coef
        self.date_event = date_event
        self.var_type = var_type
        self.is_percent = is_percent
        self.da_ref = cf_vars[0].reference_da
        self.cf_vars = cf_vars
        if thresh is not None and logical_operation is not None:
            self.nb_event_config = get_nb_event_conf(
                logical_operation, link_logical_operations, thresh, cf_vars
            )
        self.save_percentile = save_percentile
        self.ref_time_range = ref_time_range
        if (rtr := ref_time_range) is not None:
            rtr = [x.strftime("%Y-%m-%d") for x in rtr]
            for cf_var in cf_vars:
                cf_var.reference_da = cf_var.study_da.sel(time=slice(rtr[0], rtr[1]))


def get_nb_event_conf(
    logical_operation: list[str] | str,
    link_logical_operations: str | None,
    thresholds: list[str | float] | float | str,
    cfvars: list[CfVariable],
) -> NbEventConfig:
    if not isinstance(thresholds, list):
        threshold_list = [thresholds]
    else:
        threshold_list = thresholds
    if isinstance(logical_operation, list):
        logical_operations = list(map(LogicalOperation.lookup, logical_operation))
    else:
        logical_operations = [LogicalOperation.lookup(logical_operation)]
    if link_logical_operations is not None:
        link_logical_operation_list = LinkLogicalOperation.lookup(
            link_logical_operations
        )
    else:
        link_logical_operation_list = None
    return NbEventConfig(
        logical_operation=logical_operations,
        link_logical_operations=link_logical_operation_list,
        thresholds=threshold_list,
        data_arrays=cfvars,
    )
