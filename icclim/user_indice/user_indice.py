from dataclasses import dataclass
from enum import Enum
from inspect import FrameInfo
from typing import Callable, List, Optional, Union

from xarray.core.dataarray import DataArray

from icclim.models.frequency import Frequency
from icclim.models.indice_config import CfVariable


class LinkLogicalOperation(Enum):
    OR_STAMP = "or"
    AND_STAMP = "and"


class ExtremeMode(Enum):
    MIN = "min"
    MAX = "max"


class LogicalOperation(Enum):
    GREATER_THAN = (["gt", ">"], ">", lambda da, th: da > th)
    LOWER_THAN = (["lt", "<"], "<", lambda da, th: da < th)
    GREATER_OR_EQUAL_THAN = (["get", ">=", "=>"], ">=", lambda da, th: da >= th)
    LOWER_OR_EQUAL_THAN = (["let", "<=", "=<"], "<=", lambda da, th: da <= th)
    EQUAL = (["e", "equal", "=", "=="], "==", lambda da, th: da == th)

    def __init__(
        self,
        accepted_input: str,
        operator: str,
        compute: Callable[[DataArray, Union[DataArray, float]], DataArray],
    ) -> None:
        super().__init__()
        self.accepted_input = accepted_input
        self.operator = operator
        self.compute = compute


PRECIPITATION = "p"
TEMPERATURE = "t"


@dataclass
class NbEventConfig:
    logical_operation: List[LogicalOperation]
    link_logical_operations: LinkLogicalOperation = None
    thresholds: Optional[List[float]] = None
    percentiles: Optional[List[DataArray]] = None
    data_arrays: List[CfVariable] = None


# TODO make a DTO ? it make the following independant LogicalOperation, base_period, thresh
class UserIndiceConfig:
    indice_name: str  # Name of custom indice.
    calc_operation: str  # Type of calculation. See below for more details.
    logical_operation: LogicalOperation
    thresh: Union[
        float,
        str,
        List[Union[float, str]],
    ]  # In case of percentile-based indice, it must be a string starting or ending with “p” (e.g. ‘p90’), then it will be mutated in a DataArray of the percentile of each day
    link_logical_operations: LinkLogicalOperation
    extreme_mode: ExtremeMode
    window_width: int  # Used for computing running mean/sum.
    coef: float  # Constant for multiplying input data array.
    date_event: bool  # To keep or not the date of event. See below for more details.
    var_type: Union[PRECIPITATION, TEMPERATURE]
    freq: Frequency
    da_ref: DataArray
    is_percent: bool
    nb_event_config: NbEventConfig

    def __init__(
        self,
        indice_name,
        calc_operation,
        freq: Frequency,
        logical_operation: str = None,
        thresh=None,
        link_logical_operations: str = None,
        extreme_mode: str = None,
        window_width=None,
        coef=None,
        date_event=None,
        var_type=None,
        is_percent=None,
    ) -> None:
        self.indice_name = indice_name
        self.calc_operation = calc_operation
        self.freq = freq
        self.logical_operation = get_logical_operation(logical_operation)
        self.thresh = thresh
        self.nb_event_config = get_nb_event_conf(
            logical_operation,
            link_logical_operations,
            thresh,
        )
        get_link_logical_operations(link_logical_operations)
        self.extreme_mode = get_extreme_mode(extreme_mode)
        self.window_width = window_width
        self.coef = coef
        self.date_event = date_event
        self.var_type = var_type
        self.is_percent = is_percent


def get_logical_operation(s: str) -> LogicalOperation:
    if s is None:
        return None
    for op in LogicalOperation:
        if s.upper() in map(str.upper, op.accepted_input):
            return op
    raise Exception(f"Unknown operator {s}")


def get_extreme_mode(s: str) -> ExtremeMode:
    if s is None:
        return None
    for mode in ExtremeMode:
        if s.upper == mode.value.upper():
            return mode
    raise Exception(f"Unknown extreme mode {s}")


def get_link_logical_operations(s: str) -> LinkLogicalOperation:
    if s is None:
        return None
    for mode in LinkLogicalOperation:
        if s.upper == mode.value.upper():
            return mode
    raise Exception(f"Unknown link_logical_operation mode {s}")


def get_nb_event_conf(
    logical_operation: Union[List[float], float],
    link_logical_operations: str,
    thresholds: Union[List[float], float],
) -> NbEventConfig:
    if logical_operation is None:
        return None
    if not isinstance(thresholds, list):
        thresholds = [thresholds]
    if isinstance(logical_operation, list):
        logical_operation = map(get_link_logical_operations, logical_operation)
    else:
        logical_operation = [get_link_logical_operations(logical_operation)]
    return NbEventConfig(
        logical_operation=get_link_logical_operations(logical_operation),
        link_logical_operations=get_link_logical_operations(link_logical_operations),
        thresholds=thresholds,
    )
