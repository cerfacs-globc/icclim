from dataclasses import dataclass
from enum import Enum
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
        compute: Callable[[DataArray, Union[DataArray, float, int]], DataArray],
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
    link_logical_operations: Optional[LinkLogicalOperation] = None
    thresholds: Optional[List[Union[float, str]]] = None
    data_arrays: Optional[List[CfVariable]] = None


# TODO make a DTO ? it make the following independant LogicalOperation, base_period, thresh
class UserIndiceConfig:
    indice_name: str  # Name of custom indice.
    calc_operation: str  # Type of calculation. See below for more details.
    logical_operation: Optional[LogicalOperation] = None
    thresh: Union[
        float,
        str,
        List[Union[float, str]],
    ]  # In case of percentile-based indice, it must be a string starting or ending with “p” (e.g. ‘p90’), then it will be mutated in a DataArray of the percentile of each day
    link_logical_operations: Optional[LinkLogicalOperation]
    extreme_mode: Optional[ExtremeMode] = None
    window_width: Optional[int]  # Used for computing running mean/sum.
    coef: Optional[float]  # Constant for multiplying input data array.
    date_event: bool = False
    var_type: Optional[str]
    freq: Frequency
    da_ref: Optional[DataArray] = None
    is_percent: bool
    nb_event_config: Optional[NbEventConfig] = None
    cf_vars: List[CfVariable]

    def __init__(
        self,
        indice_name,
        calc_operation,
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
    ) -> None:
        self.indice_name = indice_name
        self.calc_operation = calc_operation
        self.freq = freq
        if logical_operation is not None:
            self.logical_operation = get_logical_operation(logical_operation)
        self.thresh = thresh
        self.extreme_mode = get_extreme_mode(extreme_mode)
        self.window_width = window_width
        self.coef = coef
        self.date_event = date_event
        self.var_type = var_type
        self.is_percent = is_percent
        self.da_ref = cf_vars[0].in_base_da
        self.cf_vars = cf_vars
        if isinstance(thresh, list) and logical_operation is not None:
            self.nb_event_config = get_nb_event_conf(
                logical_operation, link_logical_operations, thresh, cf_vars
            )


def get_logical_operation(s: str) -> LogicalOperation:
    for op in LogicalOperation:
        if s.upper() in map(str.upper, op.accepted_input):
            return op
    raise Exception(f"Unknown operator {s}")


def get_extreme_mode(s: Optional[str]) -> Optional[ExtremeMode]:
    if s is None:
        return None
    for mode in ExtremeMode:
        if s.upper == mode.value.upper():
            return mode
    raise Exception(f"Unknown extreme mode {s}")


def get_link_logical_operations(s: str) -> LinkLogicalOperation:
    for mode in LinkLogicalOperation:
        if s.upper == mode.value.upper():
            return mode
    raise Exception(f"Unknown link_logical_operation mode {s}")


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
        logical_operations = list(map(get_logical_operation, logical_operation))
    else:
        logical_operations = [get_logical_operation(logical_operation)]
    if link_logical_operations is not None:
        link_logical_operation_list = get_link_logical_operations(
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
