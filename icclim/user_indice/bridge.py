from enum import Enum
from typing import Any, List, Union

from xarray.core.dataarray import DataArray

from icclim.models.indice_config import CfVariable
from icclim.user_indice.operation import (
    anomaly,
    count_events,
    max,
    max_consecutive_event_count,
    mean,
    min,
    run_mean,
    run_sum,
    sum,
)
from icclim.user_indice.user_indice import UserIndiceConfig


class CalcOperation(Enum):
    MAX = "max"
    MIN = "min"
    SUM = "sum"
    MEAN = "mean"
    EVENT_COUNT = "nb_event"
    MAX_NUMBER_OF_CONSECUTIVE_EVENTS = "max_nb_consecutive_events"
    RUN_MEAN = "run_mean"
    RUN_SUM = "run_sum"
    ANOMALY = "anomaly"


def compute_user_indice(indice: UserIndiceConfig) -> DataArray:
    if indice.calc_operation == CalcOperation.MAX.value:
        return max(
            da=check_and_get_da(indice.cf_vars),
            in_base_da=check_and_get_in_base_da(indice.cf_vars),
            coef=indice.coef,
            logical_operation=indice.logical_operation,
            threshold=check_and_get_simple_thresold(indice.thresh),
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.MIN.value:
        return min(
            da=check_and_get_da(indice.cf_vars),
            in_base_da=check_and_get_in_base_da(indice.cf_vars),
            coef=indice.coef,
            logical_operation=indice.logical_operation,
            threshold=check_and_get_simple_thresold(indice.thresh),
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.MEAN.value:
        return mean(
            da=check_and_get_da(indice.cf_vars),
            in_base_da=check_and_get_in_base_da(indice.cf_vars),
            coef=indice.coef,
            logical_operation=indice.logical_operation,
            threshold=check_and_get_simple_thresold(indice.thresh),
            freq=indice.freq.panda_freq,
        )
    elif indice.calc_operation == CalcOperation.SUM.value:
        return sum(
            da=check_and_get_da(indice.cf_vars),
            in_base_da=check_and_get_in_base_da(indice.cf_vars),
            coef=indice.coef,
            logical_operation=indice.logical_operation,
            threshold=check_and_get_simple_thresold(indice.thresh),
            freq=indice.freq.panda_freq,
        )
    elif indice.calc_operation == CalcOperation.EVENT_COUNT.value:
        if indice.nb_event_config is None:
            raise Exception(
                f"{CalcOperation.EVENT_COUNT.value} not properly configure. Please provide a threshold and a logical operation."
            )
        return count_events(
            das=list(map(lambda x: x.da, indice.cf_vars)),
            in_base_das=list(map(lambda x: x.in_base_da, indice.cf_vars)),
            logical_operation=indice.nb_event_config.logical_operation,
            link_logical_operations=indice.nb_event_config.link_logical_operations,
            thresholds=indice.nb_event_config.thresholds,
            coef=indice.coef,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.MAX_NUMBER_OF_CONSECUTIVE_EVENTS.value:
        if indice.logical_operation is None or indice.thresh is None:
            raise Exception("Please provide a threshold and a logical operation")
        if isinstance(indice.thresh, list):
            raise Exception(
                f"{CalcOperation.MAX_NUMBER_OF_CONSECUTIVE_EVENTS.value} does not support threshold list. Please provide a single threshold"
            )
        return max_consecutive_event_count(
            da=indice.cf_vars[0].da,
            in_base_da=indice.cf_vars[0].in_base_da,
            logical_operation=indice.logical_operation,
            threshold=indice.thresh,
            coef=indice.coef,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.RUN_MEAN.value:
        if indice.extreme_mode is None or indice.window_width is None:
            raise Exception("Please provide a extreme mode and a window width")
        return run_mean(
            da=indice.cf_vars[0].da,
            extreme_mode=indice.extreme_mode,
            window_width=indice.window_width,
            coef=indice.coef,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.RUN_SUM.value:
        if indice.extreme_mode is None or indice.window_width is None:
            raise Exception("Please provide a extreme mode and a window width")
        return run_sum(
            da=indice.cf_vars[0].da,
            extreme_mode=indice.extreme_mode,
            window_width=indice.window_width,
            coef=indice.coef,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.ANOMALY.value:
        if indice.da_ref is None:
            raise Exception(
                f"You must provide a in base to compute {CalcOperation.ANOMALY.value}."
            )
        return anomaly(
            da=indice.cf_vars[0].da,
            da_ref=indice.da_ref,
            percent=indice.is_percent,
        )
    else:
        raise NotImplementedError(
            f"The calc_operation {indice.calc_operation} is unknown."
        )


def check_and_get_simple_thresold(thresh: Any) -> Union[None, str, float, int]:
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


def check_and_get_da(cf_vars: List[CfVariable]) -> DataArray:
    if len(cf_vars) == 1:
        return cf_vars[0].da
    else:
        raise Exception("There must be exactly one variable for this indice.")


def check_and_get_in_base_da(cf_vars: List[CfVariable]) -> Union[DataArray, None]:
    if len(cf_vars) == 1:
        return cf_vars[0].in_base_da
    else:
        raise Exception("There must be exactly one variable for this indice.")
