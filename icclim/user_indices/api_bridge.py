from enum import Enum
from typing import Any, Callable, List, Union

from xarray.core.dataarray import DataArray

from icclim.models.indice_config import CfVariable, IndiceConfig
from icclim.models.user_indice_config import UserIndiceConfig
from icclim.user_indices import operation


def compute_user_indice(config: UserIndiceConfig) -> DataArray:
    for calc_op in CalcOperation:
        if calc_op.input_name.upper() == config.calc_operation.upper():
            return calc_op.compute_fun(config)
    raise NotImplementedError(f"The calc_operation {config.calc_operation} is unknown.")


def anomaly(indice):
    if indice.da_ref is None:
        raise Exception(
            f"You must provide a in base to compute {CalcOperation.ANOMALY.value}."
        )
    return operation.anomaly(
        da=indice.cf_vars[0].da,
        da_ref=indice.da_ref,
        percent=indice.is_percent,
    )


def run_sum(indice):
    if indice.extreme_mode is None or indice.window_width is None:
        raise Exception("Please provide a extreme mode and a window width")
    return operation.run_sum(
        da=indice.cf_vars[0].da,
        extreme_mode=indice.extreme_mode,
        window_width=indice.window_width,
        coef=indice.coef,
        freq=indice.freq.panda_freq,
        date_event=indice.date_event,
    )


def run_mean(indice):
    if indice.extreme_mode is None or indice.window_width is None:
        raise Exception("Please provide a extreme mode and a window width")
    return operation.run_mean(
        da=indice.cf_vars[0].da,
        extreme_mode=indice.extreme_mode,
        window_width=indice.window_width,
        coef=indice.coef,
        freq=indice.freq.panda_freq,
        date_event=indice.date_event,
    )


def max_consecutive_event_count(indice):
    if indice.logical_operation is None or indice.thresh is None:
        raise Exception("Please provide a threshold and a logical operation")
    if isinstance(indice.thresh, list):
        raise Exception(
            f"{CalcOperation.MAX_NUMBER_OF_CONSECUTIVE_EVENTS.value} does not support threshold list. Please provide a single threshold"
        )
    return operation.max_consecutive_event_count(
        da=indice.cf_vars[0].da,
        in_base_da=indice.cf_vars[0].in_base_da,
        logical_operation=indice.logical_operation,
        threshold=indice.thresh,
        coef=indice.coef,
        freq=indice.freq.panda_freq,
        date_event=indice.date_event,
    )


def count_events(indice):
    if indice.nb_event_config is None:
        raise Exception(
            f"{CalcOperation.EVENT_COUNT.value} not properly configure. Please provide a threshold and a logical operation."
        )
    return operation.count_events(
        das=list(map(lambda x: x.da, indice.cf_vars)),
        in_base_das=list(map(lambda x: x.in_base_da, indice.cf_vars)),
        logical_operation=indice.nb_event_config.logical_operation,
        link_logical_operations=indice.nb_event_config.link_logical_operations,
        thresholds=indice.nb_event_config.thresholds,
        coef=indice.coef,
        freq=indice.freq.panda_freq,
        date_event=indice.date_event,
    )


def sum(indice):
    return operation.sum(
        da=_check_and_get_da(indice.cf_vars),
        in_base_da=_check_and_get_in_base_da(indice.cf_vars),
        coef=indice.coef,
        logical_operation=indice.logical_operation,
        threshold=_check_and_get_simple_threshold(indice.thresh),
        freq=indice.freq.panda_freq,
    )


def mean(indice):
    return operation.mean(
        da=_check_and_get_da(indice.cf_vars),
        in_base_da=_check_and_get_in_base_da(indice.cf_vars),
        coef=indice.coef,
        logical_operation=indice.logical_operation,
        threshold=_check_and_get_simple_threshold(indice.thresh),
        freq=indice.freq.panda_freq,
    )


def min(indice):
    return operation.min(
        da=_check_and_get_da(indice.cf_vars),
        in_base_da=_check_and_get_in_base_da(indice.cf_vars),
        coef=indice.coef,
        logical_operation=indice.logical_operation,
        threshold=_check_and_get_simple_threshold(indice.thresh),
        freq=indice.freq.panda_freq,
        date_event=indice.date_event,
    )


def max(indice):
    return operation.max(
        da=_check_and_get_da(indice.cf_vars),
        in_base_da=_check_and_get_in_base_da(indice.cf_vars),
        coef=indice.coef,
        logical_operation=indice.logical_operation,
        threshold=_check_and_get_simple_threshold(indice.thresh),
        freq=indice.freq.panda_freq,
        date_event=indice.date_event,
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
            "threshold must be either None, a string (for percentiles) or a number"
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
        self, input_name: str, compute_fun: Callable[[IndiceConfig], DataArray]
    ):
        self.input_name = input_name
        self.compute_fun = compute_fun
