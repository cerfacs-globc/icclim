from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, List, Optional, Union

from xarray.core.dataarray import DataArray

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.frequency import Frequency
from icclim.models.index_config import CfVariable


class LinkLogicalOperation(Enum):
    OR_STAMP = "or"
    AND_STAMP = "and"

    @staticmethod
    def lookup(s: str) -> Any:
        for mode in LinkLogicalOperation:
            if s.upper == mode.value.upper():
                return mode
        raise InvalidIcclimArgumentError(
            f"Unknown link_logical_operation mode {s}."
            f"Use one of {[linkOp.value for linkOp in LinkLogicalOperation]}."
        )


class ExtremeMode(Enum):
    MIN = "min"
    MAX = "max"

    @staticmethod
    def lookup(s: str) -> Any:
        for mode in ExtremeMode:
            if s.upper == mode.value.upper():
                return mode
        raise InvalidIcclimArgumentError(
            f"Unknown extreme mode {s}."
            f"Use one of {[mode.value for mode in ExtremeMode]}."
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
        compute: Callable[[DataArray, Union[DataArray, float, int]], DataArray],
    ) -> None:
        super().__init__()
        self.aliases = aliases
        self.operator = operator
        self.compute = compute

    @staticmethod
    def lookup(s: str) -> Any:
        for op in LogicalOperation:
            if s.upper() in map(str.upper, op.aliases):
                return op
        raise InvalidIcclimArgumentError(
            f"Unknown logical operator {s}."
            f"Use one of {[op.aliases for op in LogicalOperation]}."
        )


@dataclass
class NbEventConfig:
    logical_operation: List[LogicalOperation]
    thresholds: List[Union[float, str]]
    link_logical_operations: Optional[LinkLogicalOperation] = None
    data_arrays: Optional[List[CfVariable]] = None


@dataclass
class UserIndexConfig:
    index_name: str
    calc_operation: str
    cf_vars: List[CfVariable]
    freq: Frequency
    date_event: bool
    is_percent: bool
    logical_operation: Optional[LogicalOperation] = None
    thresh: Optional[Union[float, int, str, List[Union[float, int, str]]]] = None
    link_logical_operations: Optional[LinkLogicalOperation] = None
    extreme_mode: Optional[ExtremeMode] = None
    window_width: Optional[int] = None
    coef: Optional[float] = None
    var_type: Optional[str] = None
    da_ref: Optional[DataArray] = None
    nb_event_config: Optional[NbEventConfig] = None
    save_percentile: bool = False

    def __init__(
        self,
        index_name,
        # Any should be CalcOperation but it causes circular import
        calc_operation: Union[str, Any],
        freq: Frequency,
        cf_vars: List[CfVariable],
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
        self.da_ref = cf_vars[0].in_base_da
        self.cf_vars = cf_vars
        if thresh is not None and logical_operation is not None:
            self.nb_event_config = get_nb_event_conf(
                logical_operation, link_logical_operations, thresh, cf_vars
            )
        self.save_percentile = save_percentile


def get_nb_event_conf(
    logical_operation: Union[List[str], str],
    link_logical_operations: Optional[str],
    thresholds: Union[List[Union[str, float]], float, str],
    cfvars: List[CfVariable],
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
