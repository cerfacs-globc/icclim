from enum import Enum
from typing import Callable, List
import datetime


class LogicalOperation(Enum):
    GT = (["gt", ">"], ">", lambda da, th: da > th)
    LT = (["lt", "<"], "<", lambda da, th: da < th)
    GET = (["get", ">=", "=>"], ">=", lambda da, th: da >= th)
    LET = (["let", "<=", "=<"], "<=", lambda da, th: da <= th)
    EQUAL = (["e", "equal", "=", "=="], "==", lambda da, th: da == th)

    def __init__(self, accepted_input: str, operator: str, compute: Callable) -> None:
        super().__init__()
        self.accepted_input = accepted_input
        self.operator = operator
        self.compute = compute


class UserIndice:
    indice_name: str  # Name of custom indice.
    calc_operation: str  # FIXME: Callable ?   # Type of calculation. See below for more details.
    logical_operation: LogicalOperation  # 	“gt”, “lt”, “get”, “let” or “e”
    thresh: float or str  # In case of percentile-based indice, must be string which starts with “p” (e.g. ‘p90’).
    link_logical_operations: str  #  	“and” or “or”
    extreme_mode: str  # 	“min” or “max” for computing min or max of running mean/sum.
    window_width: int  #     Used for computing running mean/sum.
    coef: float  # Constant for multiplying input data array.
    date_event: bool  #     To keep or not the date of event. See below for more details.
    var_type: str  # “t” or “p”. See below for more details.
    ref_time_range: List[
        datetime.datetime
    ]  # 	Time range of reference (baseline) period for computing anomalies.

    def __init__(
        self,
        indice_name,
        calc_operation,
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
