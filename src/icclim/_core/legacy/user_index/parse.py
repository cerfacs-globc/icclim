"""Contain the parsing operations to create a user indices."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from icclim._core.constants import (
    PERCENTILE_THRESHOLD_STAMP,
    USER_INDEX_PRECIPITATION_STAMP,
    USER_INDEX_TEMPERATURE_STAMP,
)
from icclim._core.legacy.user_index.calc_operation import CalcOperationRegistry
from icclim._core.model.logical_link import LogicalLink, LogicalLinkRegistry
from icclim._core.model.operator import Operator, OperatorRegistry
from icclim._core.model.threshold import Threshold
from icclim.exception import InvalidIcclimArgumentError
from icclim.generic.registry import GenericIndicatorRegistry
from icclim.threshold.factory import build_threshold

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import Sequence

    from icclim._core.generic.indicator import GenericIndicator
    from icclim._core.legacy.user_index.model import UserIndexDict
    from icclim._core.model.quantile_interpolation import QuantileInterpolation


def read_indicator(user_index: UserIndexDict) -> GenericIndicator:
    """
    Read the user index and return the corresponding generic indicator.

    Parameters
    ----------
    user_index : UserIndexDict
        The user index dictionary containing the calculation operation and extreme mode.

    Returns
    -------
    GenericIndicator
        The corresponding generic indicator based on the user index.

    Raises
    ------
    InvalidIcclimArgumentError
        If the user index does not contain a calculation operation.
        If the user index's calculation operation is unknown.
    NotImplementedError
        If the calculation operation or extreme mode is not implemented.

    Notes
    -----
    This function reads the user index dictionary and maps the calculation operation and
    extreme mode to the corresponding generic indicator.
    It raises errors if the required information is missing or if the operation is not
    implemented.
    """
    calc_op = user_index.get("calc_operation", None)
    if calc_op is None:
        err = "user_index needs a calc_operation"
        raise InvalidIcclimArgumentError(err)
    calc_op = CalcOperationRegistry.lookup(calc_op)
    user_index_map = {
        CalcOperationRegistry.MAX: GenericIndicatorRegistry.Maximum.clone(),
        CalcOperationRegistry.MIN: GenericIndicatorRegistry.Minimum.clone(),
        CalcOperationRegistry.SUM: GenericIndicatorRegistry.Sum.clone(),
        CalcOperationRegistry.MEAN: GenericIndicatorRegistry.Average.clone(),
        CalcOperationRegistry.EVENT_COUNT: GenericIndicatorRegistry.CountOccurrences.clone(),  # noqa: E501
        CalcOperationRegistry.MAX_NUMBER_OF_CONSECUTIVE_EVENTS: GenericIndicatorRegistry.MaxConsecutiveOccurrence.clone(),  # noqa: E501
        CalcOperationRegistry.ANOMALY: GenericIndicatorRegistry.DifferenceOfMeans.clone(),  # noqa: E501
    }
    extrem_mode = user_index.get("extreme_mode", None)
    if calc_op == CalcOperationRegistry.RUN_SUM:
        if extrem_mode == "max":
            indicator = GenericIndicatorRegistry.MaxOfRollingSum.clone()
        elif extrem_mode == "min":
            indicator = GenericIndicatorRegistry.MinOfRollingSum.clone()
        else:
            raise NotImplementedError
    elif calc_op == CalcOperationRegistry.RUN_MEAN:
        if extrem_mode == "max":
            indicator = GenericIndicatorRegistry.MaxOfRollingAverage.clone()
        elif extrem_mode == "min":
            indicator = GenericIndicatorRegistry.MinOfRollingAverage.clone()
        else:
            raise NotImplementedError
    else:
        indicator = user_index_map.get(calc_op)
    if indicator is None:
        msg = (
            "Unknown user_index's calc_operation:"
            f" '{user_index.get('calc_operation', None)}'"
        )
        raise InvalidIcclimArgumentError(msg)
    return indicator


def read_logical_link(user_index: UserIndexDict) -> LogicalLink:
    """
    Read the logical link from the user index dictionary.

    Parameters
    ----------
    user_index : UserIndexDict
        The user index dictionary containing the logical link information.

    Returns
    -------
    LogicalLink
        The corresponding LogicalLink based on the logical link information in the user
        index dictionary.

    Notes
    -----
    If the logical link is not specified in the user index dictionary, the default
    logical link is LogicalLinkRegistry.LOGICAL_AND.
    """
    logical_link = user_index.get("link_logical_operations", None)
    if logical_link is None:
        return LogicalLinkRegistry.LOGICAL_AND
    return LogicalLinkRegistry.lookup(logical_link)


def read_coef(user_index: UserIndexDict) -> float | None:
    """
    Read the coefficient value from the user index dictionary.

    Parameters
    ----------
    user_index : UserIndexDict
        The user index dictionary containing the coefficient value.

    Returns
    -------
    float or None
        The coefficient value if it exists in the user index dictionary, otherwise None.
    """
    return user_index.get("coef", None)


def read_date_event(user_index: UserIndexDict) -> bool:
    """
    Read the 'date_event' key from the given UserIndexDict.

    Parameters
    ----------
    user_index : UserIndexDict
        The dictionary containing user index information.

    Returns
    -------
    bool
        The value associated with the 'date_event' key in the UserIndexDict,
        if missing returns False.
    """
    return user_index.get("date_event", False)


def read_thresholds(
    user_index: UserIndexDict,
    doy_window_width: int,
    reference_period: Sequence[dt.datetime | str] | None,
    only_leap_years: bool,
    interpolation: QuantileInterpolation,
) -> Threshold | None | list[Threshold]:
    """
    Read the thresholds from the user index dictionary.

    Parameters
    ----------
    user_index : UserIndexDict
        The user index dictionary containing the threshold information.
    doy_window_width : int
        The width of the day of year window for calculating the threshold.
    reference_period : Sequence[dt.datetime | str] | None
        The reference period for calculating the threshold.
    only_leap_years : bool
        Whether to consider only leap years when calculating the threshold.
    interpolation : QuantileInterpolation
        The interpolation method to use for calculating the threshold.

    Returns
    -------
    Threshold or None or list[Threshold]
        The corresponding Threshold object(s) based on the threshold information in the
        user index dictionary.

    Notes
    -----
    This function reads the threshold information from the user index dictionary and
    maps it to the corresponding Threshold object(s).
    If the threshold is already a Threshold object, it is returned as is.
    If the threshold is a tuple or list, multiple Threshold objects are created based
    on the logical operation and link specified in the user index dictionary.
    If the threshold is a single value, a single Threshold object is created.
    """
    thresh = user_index.get("thresh", None)
    var_type = user_index.get("var_type", None)
    if thresh is None or isinstance(thresh, Threshold):
        return thresh
    logical_operation = user_index.get("logical_operation", None)
    if isinstance(thresh, (tuple, list)):
        if logical_operation is None:
            logical_operations = [OperatorRegistry.REACH for _ in thresh]
        else:
            logical_operations = [
                OperatorRegistry.lookup(lo) for lo in logical_operation
            ]
        link = user_index.get(
            "link_logical_operations", LogicalLinkRegistry.LOGICAL_AND
        )
        link = LogicalLinkRegistry.LOGICAL_AND if link is None else link
        link = LogicalLinkRegistry.lookup(link)
        thresholds = (
            _build_thresh_query(t, var_type, logical_operations[i])
            for i, t in enumerate(thresh)
        )
        return [
            build_threshold(
                t,
                doy_window_width=doy_window_width,
                reference_period=reference_period,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
            )
            for t in thresholds
        ]
    if logical_operation is None:
        logical_operation = OperatorRegistry.REACH
    elif isinstance(logical_operation, str):
        logical_operation = OperatorRegistry.lookup(logical_operation)
    elif isinstance(logical_operation, Operator):
        pass
    else:
        err = "Invalid user_index: logical_operation must be None or a string."
        raise InvalidIcclimArgumentError(err)
    thresh_query = _build_thresh_query(thresh, var_type, logical_operation)
    return build_threshold(
        thresh_query,
        doy_window_width=doy_window_width,
        reference_period=reference_period,
        only_leap_years=only_leap_years,
        interpolation=interpolation,
    )


def _build_thresh_query(
    query: str | float,
    var_type: Literal["t", "p"] | None,
    operator: Operator,
) -> str:
    if isinstance(query, str) and query.endswith(PERCENTILE_THRESHOLD_STAMP):
        if var_type == USER_INDEX_TEMPERATURE_STAMP:
            replace_unit = "doy_per"
        elif var_type == USER_INDEX_PRECIPITATION_STAMP:
            replace_unit = "period_per"
        else:
            replace_unit = "period_per"  # default to period percentiles ?
        t = query.replace(PERCENTILE_THRESHOLD_STAMP, " " + replace_unit)
    else:
        t = str(query)
    return f"{operator.operand} {t}"
