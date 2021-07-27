from enum import Enum
from icclim.models.frequency import Frequency
from inspect import FrameInfo
from typing import Callable, List, Union

from xarray.core.dataarray import DataArray


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

# TODO make a DTO ? it make the following independant LogicalOperation, base_period, thresh
class UserIndiceConfig:
    indice_name: str  # Name of custom indice.
    calc_operation: str  # Type of calculation. See below for more details.
    logical_operation: LogicalOperation  # 	“gt”, “lt”, “get”, “let” or “e”
    thresh: Union[
        float,
        str,
        DataArray,
        List[Union[float, str, DataArray]],  # TODO handle list in  the parsing
    ]  # In case of percentile-based indice, it must be a string starting or ending with “p” (e.g. ‘p90’), then it will be mutated in a DataArray of the percentile of each day
    link_logical_operations: str  #  	“and” or “or”
    extreme_mode: str  # 	“min” or “max” for computing min or max of running mean/sum.
    window_width: int  #     Used for computing running mean/sum.
    coef: float  # Constant for multiplying input data array.
    date_event: bool  #     To keep or not the date of event. See below for more details.
    var_type: Union[PRECIPITATION, TEMPERATURE]
    freq: Frequency

    def __init__(
        self,
        indice_name,
        calc_operation,
        freq: Frequency,
        logical_operation: str = None,
        thresh=None,
        link_logical_operations=None,
        extreme_mode=None,
        window_width=None,
        coef=None,
        date_event=None,
        var_type=None,
        ref_time_range=None,
    ) -> None:
        self.indice_name = indice_name
        self.calc_operation = calc_operation
        self.freq = freq
        self.logical_operation = get_logical_operation(logical_operation)
        self.thresh = thresh
        self.link_logical_operations = link_logical_operations
        self.extreme_mode = extreme_mode
        self.window_width = window_width
        self.coef = coef
        self.date_event = date_event
        self.var_type = var_type
        self.ref_time_range = ref_time_range


def get_logical_operation(s: str):
    if s is None:
        return None
    for op in LogicalOperation:
        if s.upper() in map(str.upper, op.accepted_input):
            return op
    raise Exception(f"Unknown operator {s}")
