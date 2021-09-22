from enum import Enum
from typing import Any, Callable, List, Union

from xarray.core.dataarray import DataArray

from icclim.models.indice_config import CfVariable
from icclim.models.user_indice_config import UserIndiceConfig
from icclim.user_indices import operators


def compute_user_indice(config: UserIndiceConfig) -> DataArray:
    operation = None
    if isinstance(config.calc_operation, CalcOperation):
        operation = config.calc_operation
    for calc_op in CalcOperation:
        if calc_op.input_name.upper() == config.calc_operation.upper():
            operation = calc_op
            break
    if operation is None:
        raise NotImplementedError(
            f"The calc_operation {config.calc_operation} is unknown."
        )
    else:
        return operation.compute_fun(config)


def anomaly(config: UserIndiceConfig):
    if config.da_ref is None:
        raise Exception(
            f"You must provide a in base to compute {CalcOperation.ANOMALY.value}."
        )
    return operators.anomaly(
        da=config.cf_vars[0].da,
        da_ref=config.da_ref,
        percent=config.is_percent,
    )


def run_sum(config: UserIndiceConfig):
    if config.extreme_mode is None or config.window_width is None:
        raise Exception("Please provide a extreme mode and a window width")
    return operators.run_sum(
        da=config.cf_vars[0].da,
        extreme_mode=config.extreme_mode,
        window_width=config.window_width,
        coef=config.coef,
        freq=config.freq.panda_freq,
        date_event=config.date_event,
    )


def run_mean(config: UserIndiceConfig):
    if config.extreme_mode is None or config.window_width is None:
        raise Exception("Please provide a extreme mode and a window width")
    return operators.run_mean(
        da=config.cf_vars[0].da,
        extreme_mode=config.extreme_mode,
        window_width=config.window_width,
        coef=config.coef,
        freq=config.freq.panda_freq,
        date_event=config.date_event,
    )


def max_consecutive_event_count(config: UserIndiceConfig):
    if config.logical_operation is None or config.thresh is None:
        raise Exception("Please provide a threshold and a logical operation")
    if isinstance(config.thresh, list):
        raise Exception(
            f"{CalcOperation.MAX_NUMBER_OF_CONSECUTIVE_EVENTS.value} does not support threshold list. Please provide a single threshold"
        )
    return operators.max_consecutive_event_count(
        da=config.cf_vars[0].da,
        in_base_da=config.cf_vars[0].in_base_da,
        logical_operation=config.logical_operation,
        threshold=config.thresh,
        coef=config.coef,
        freq=config.freq.panda_freq,
        date_event=config.date_event,
    )


def count_events(config: UserIndiceConfig):
    if config.nb_event_config is None:
        raise Exception(
            f"{CalcOperation.EVENT_COUNT.value} not properly configure. Please provide a threshold and a logical operation."
        )
    return operators.count_events(
        das=list(map(lambda x: x.da, config.cf_vars)),
        in_base_das=list(map(lambda x: x.in_base_da, config.cf_vars)),
        logical_operation=config.nb_event_config.logical_operation,
        link_logical_operations=config.nb_event_config.link_logical_operations,
        thresholds=config.nb_event_config.thresholds,
        coef=config.coef,
        freq=config.freq.panda_freq,
        date_event=config.date_event,
    )


def sum(config: UserIndiceConfig):
    return operators.sum(
        da=_check_and_get_da(config.cf_vars),
        in_base_da=_check_and_get_in_base_da(config.cf_vars),
        coef=config.coef,
        logical_operation=config.logical_operation,
        threshold=_check_and_get_simple_threshold(config.thresh),
        freq=config.freq.panda_freq,
    )


def mean(config: UserIndiceConfig):
    return operators.mean(
        da=_check_and_get_da(config.cf_vars),
        in_base_da=_check_and_get_in_base_da(config.cf_vars),
        coef=config.coef,
        logical_operation=config.logical_operation,
        threshold=_check_and_get_simple_threshold(config.thresh),
        freq=config.freq.panda_freq,
    )


def min(config: UserIndiceConfig):
    return operators.min(
        da=_check_and_get_da(config.cf_vars),
        in_base_da=_check_and_get_in_base_da(config.cf_vars),
        coef=config.coef,
        logical_operation=config.logical_operation,
        threshold=_check_and_get_simple_threshold(config.thresh),
        freq=config.freq.panda_freq,
        date_event=config.date_event,
    )


def max(config: UserIndiceConfig):
    return operators.max(
        da=_check_and_get_da(config.cf_vars),
        in_base_da=_check_and_get_in_base_da(config.cf_vars),
        coef=config.coef,
        logical_operation=config.logical_operation,
        threshold=_check_and_get_simple_threshold(config.thresh),
        freq=config.freq.panda_freq,
        date_event=config.date_event,
    )


def _check_and_get_simple_threshold(thresh: Any) -> Union[None, str, float, int]:
    if (
        thresh is None
        or isinstance(thresh, str)
        or isinstance(thresh, float)
        or isinstance(thresh, int)
    ):
        return thresh
    else:
        raise Exception(
            "threshold type must be either None, a string (for percentiles) or a number"
        )


def _check_and_get_da(cf_vars: List[CfVariable]) -> DataArray:
    if len(cf_vars) == 1:
        return cf_vars[0].da
    else:
        raise Exception("There must be exactly one variable for this indice.")


def _check_and_get_in_base_da(cf_vars: List[CfVariable]) -> Union[DataArray, None]:
    if len(cf_vars) == 1:
        return cf_vars[0].in_base_da
    else:
        raise Exception("There must be exactly one variable for this indice.")


class CalcOperation(Enum):
    MAX = ("max", max)
    MIN = ("min", min)
    SUM = ("sum", sum)
    MEAN = ("mean", mean)
    EVENT_COUNT = ("nb_events", count_events)
    MAX_NUMBER_OF_CONSECUTIVE_EVENTS = (
        "max_nb_consecutive_events",
        max_consecutive_event_count,
    )
    RUN_MEAN = ("run_mean", run_mean)
    RUN_SUM = ("run_sum", run_sum)
    ANOMALY = ("anomaly", anomaly)

    def __init__(
        self, input_name: str, compute_fun: Callable[[UserIndiceConfig], DataArray]
    ):
        self.input_name = input_name
        self.compute_fun = compute_fun
