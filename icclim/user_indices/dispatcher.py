from enum import Enum
from typing import Any, Callable, Union

from xarray.core.dataarray import DataArray

from icclim.icclim_exceptions import InvalidIcclimArgumentError, MissingIcclimInputError
from icclim.models.user_index_config import UserIndexConfig
from icclim.user_indices import operators


def compute_user_index(config: UserIndexConfig) -> DataArray:
    operation = CalcOperation.lookup(config)
    return operation.compute_fun(config)


def anomaly(config: UserIndexConfig):
    if config.da_ref is None:
        raise MissingIcclimInputError(
            f"You must provide a in base to compute {CalcOperation.ANOMALY.value}."
        )
    return operators.anomaly(
        da=config.cf_vars[0].da,
        da_ref=config.da_ref,
        percent=config.is_percent,
    )


def run_sum(config: UserIndexConfig):
    if config.extreme_mode is None or config.window_width is None:
        raise MissingIcclimInputError(
            "Please provide a extreme mode and a window width."
        )
    return operators.run_sum(
        da=config.cf_vars[0].da,
        extreme_mode=config.extreme_mode,
        window_width=config.window_width,
        coef=config.coef,
        freq=config.freq.panda_freq,
        date_event=config.date_event,
    )


def run_mean(config: UserIndexConfig):
    if config.extreme_mode is None or config.window_width is None:
        raise MissingIcclimInputError(
            "Please provide a extreme mode and a window width."
        )
    return operators.run_mean(
        da=config.cf_vars[0].da,
        extreme_mode=config.extreme_mode,
        window_width=config.window_width,
        coef=config.coef,
        freq=config.freq.panda_freq,
        date_event=config.date_event,
    )


def max_consecutive_event_count(config: UserIndexConfig):
    if config.logical_operation is None or config.thresh is None:
        raise MissingIcclimInputError(
            "Please provide a threshold and a logical operation."
        )
    if isinstance(config.thresh, list):
        raise InvalidIcclimArgumentError(
            f"{CalcOperation.MAX_NUMBER_OF_CONSECUTIVE_EVENTS.value} "
            f"does not support threshold list. Please provide a single threshold."
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


def count_events(config: UserIndexConfig):
    if config.nb_event_config is None:
        raise MissingIcclimInputError(
            f"{CalcOperation.EVENT_COUNT.value} not properly configure."
            f" Please provide a threshold and a logical operation."
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


def sum(config: UserIndexConfig):
    return operators.sum(
        da=_check_and_get_da(config),
        in_base_da=_check_and_get_in_base_da(config),
        coef=config.coef,
        logical_operation=config.logical_operation,
        threshold=_check_and_get_simple_threshold(config.thresh),
        freq=config.freq.panda_freq,
    )


def mean(config: UserIndexConfig):
    return operators.mean(
        da=_check_and_get_da(config),
        in_base_da=_check_and_get_in_base_da(config),
        coef=config.coef,
        logical_operation=config.logical_operation,
        threshold=_check_and_get_simple_threshold(config.thresh),
        freq=config.freq.panda_freq,
    )


def min(config: UserIndexConfig):
    return operators.min(
        da=_check_and_get_da(config),
        in_base_da=_check_and_get_in_base_da(config),
        coef=config.coef,
        logical_operation=config.logical_operation,
        threshold=_check_and_get_simple_threshold(config.thresh),
        freq=config.freq.panda_freq,
        date_event=config.date_event,
    )


def max(config: UserIndexConfig):
    return operators.max(
        da=_check_and_get_da(config),
        in_base_da=_check_and_get_in_base_da(config),
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
        raise InvalidIcclimArgumentError(
            "threshold type must be either None, "
            "a string (for percentile) or a number."
        )


def _check_and_get_da(config: UserIndexConfig) -> DataArray:
    if len(config.cf_vars) == 1:
        return config.cf_vars[0].da
    else:
        raise InvalidIcclimArgumentError(
            f"There must be exactly one variable for {config.calc_operation}."
        )


def _check_and_get_in_base_da(config: UserIndexConfig) -> Union[DataArray, None]:
    if len(config.cf_vars) == 1:
        return config.cf_vars[0].in_base_da
    else:
        raise InvalidIcclimArgumentError(
            f"There must be exactly one variable for {config.calc_operation}"
        )


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
        self, input_name: str, compute_fun: Callable[[UserIndexConfig], DataArray]
    ):
        self.input_name = input_name
        self.compute_fun = compute_fun

    @staticmethod
    def lookup(config: UserIndexConfig):
        if isinstance(config.calc_operation, CalcOperation):
            return config.calc_operation
        for calc_op in CalcOperation:
            if calc_op.input_name.upper() == config.calc_operation.upper():
                return calc_op
        raise InvalidIcclimArgumentError(
            f"The calc_operation {config.calc_operation} is unknown."
        )