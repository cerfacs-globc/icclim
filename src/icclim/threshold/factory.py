"""Factory to build a `Threshold` from a query or from its components."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import TYPE_CHECKING

from pint.errors import UndefinedUnitError
from xarray import DataArray, Dataset
from xclim.core.units import units as xc_units

from icclim._core.constants import (
    DOY_PERCENTILE_UNIT,
    PERIOD_PERCENTILE_UNIT,
)
from icclim._core.generic.threshold.basic import BasicThreshold
from icclim._core.generic.threshold.bounded import BoundedThreshold
from icclim._core.generic.threshold.percentile import PercentileThreshold
from icclim._core.input_parsing import (
    PercentileDataArray,
    find_standard_vars,
    get_name_of_first_var,
    is_dataset_path,
    read_dataset,
)
from icclim._core.model.logical_link import LogicalLink, LogicalLinkRegistry
from icclim._core.model.operator import Operator, OperatorRegistry
from icclim._core.model.threshold import (
    Threshold,
    ThresholdBuilderInput,
    ThresholdValueType,
)
from icclim._core.utils import is_number_sequence
from icclim.exception import InvalidIcclimArgumentError

if TYPE_CHECKING:
    import pint

VALUE_REGEX = re.compile(r"-?\d+\.?\d*")
OPERAND_REGEX = re.compile(r"[<>=]")


def build_threshold(
    query: str | None = None,
    *,
    operator: Operator | str | None = None,
    value: ThresholdValueType = None,
    unit: str | None = None,
    threshold_min_value: str | float | pint.Quantity | None = None,
    thresholds: Sequence[Threshold | str] | None = None,
    logical_link: str | LogicalLink | None = None,
    offset: str | float | pint.Quantity | None = None,
    **kwargs,
) -> BoundedThreshold | PercentileThreshold | BasicThreshold:
    """
    Build a `Threshold`.

    This function is a factory for `Threshold` instances.
    It can build a `BasicThreshold`, a `PercentileThreshold` or a `BoundedThreshold`.
    See :ref:`generic_indices_recipes` for how to combine thresholds with generic
    indices.

    Parameters
    ----------
    query: str | None = None
        string query describing a threshold.
        It must include: an operator, a threshold value and optionally a unit
        such as "> 10 degC".
        It acts as a shorthand for ``operator``, ``value`` and ``unit`` parameters for
        simple threshold.
        Don't use ``query`` when value is a DataArray, a Dataset or a path to a
        netcdf/zarr storage, instead use ``operator``, ``value`` and ``unit``.
        ``query`` supersede `operator`, `value` and `unit` parameters.
    operator: Operator | str = None
        keyword argument only.
        The operator either as an instance of Operator or as a compatible string.
        See :py:class:`OperatorRegistry` for the list of all operators.
        When ``query`` is None and operator is None, the default ``Operator.REACH`` is
        used.
    value: str | float | int | Dataset | DataArray | Sequence[float | int | str] | None
        keyword argument only.
        The threshold value(s), default to None.
        It can be:
        * a simple scalar threshold
        * a percentile that will be computed per-grid cell (in combinaison with `unit`)
        * per-grid cell thresholds defined by a DataArray, a Dataset or a string path to
        a netcdf/zarr.
        * a sequence of scalars, the indicator will then be computed for each value and
        a specific dimension will be created (also work with percentiles).
    unit: str | None = None
        Keyword argument only.
        The threshold unit.
        When ``unit`` is None, if ``value`` is a dataset and a "units"
        can be read from its `attrs`, this unit will be used. If value is a scalar or
        a sequence of scalar, the exceedance will be computed by assuming threshold has
        the same unit as the studied value is it compared to.
        When unit is a string it must be a valid unit of our shared pint registry with
        xclim or a special percentile unit:
        * "doy_per" for day of year percentiles (in ECAD, used for temperature indices
        such as TX90p)
        * "period_per" for per period percentiles (in ECAD, used for rain indices such
        as R75p)
    threshold_min_value: str | float | pint.Quantity
        A minimum value used to pre-filter computed threshold values.
        This is particularly useful to compute a percentile threshold for rain where
        dry days are usually ignored. In that case threshold_min_value would be set to
        "1 mm/day".
        If threshold_min_value is a number, ``unit`` is used to quantify
        ``threshold_min_value``.
    offset: float | None
        Optional. An offset applied to the threshold. This is particularly useful when
        the threshold is an existing dataset (netcdf file or zarr store) and the data
        should be compared to this dataset + an offset
        (e.g. to compute days when T > 5 degC above normal)
    kwargs
        Additional arguments to build a PercentileThreshold.
        See :py:class:`PercentileThreshold` constructor for the complete list
        of possible arguments.

    Examples
    --------
    .. code-block:: python

        # -- Scalar threshold
        scalar_t = build_threshold(">= 30 degC")
        assert isinstance(scalar_t, BasicThreshold)

        # -- Daily percentile threshold
        doy_t = build_threshold(">= 30 doy_per")
        assert isinstance(doy_t, PercentileThreshold)

        # -- Per grid-cell threshold, with offset
        grided_t = build_threshold(
            operator=">=", value="path/to/tasmax_thresholds.nc", unit="K", offset=5
        )
        assert isinstance(grided_t, BasicThreshold)

        # -- Daily percentile threshold, from a file
        tasmax = xarray.open_dataset("path/to/tasmax_thresholds.nc").tasmax
        doys = xclim.core.calendar.percentile_doy(tasmax)
        doy_file_t = build_threshold(operator=">=", value=doys)
        assert isinstance(doy_file_t, PercentileThreshold)

        # -- Bounded threshold
        bounded_t = build_threshold(">= -20 degree AND <= 20 degree ")
        # equivalent to:
        x = build_threshold(">= -20 degree")
        y = build_threshold("<= 20 degree")
        bounded_t2 = x & y
        assert bounded_t == bounded_t2
        # equivalent to:
        bounded_t3 = build_threshold(thresholds=[x, y], logical_link="AND")
        assert bounded_t == bounded_t3
        assert isinstance(bounded_t, BoundedThreshold)

    """
    input_thresh = _read_input(
        query,
        operator,
        value,
        unit,
        threshold_min_value,
        thresholds,
        logical_link,
        offset,
        **kwargs,
    )
    if _must_build_per_threshold(input_thresh):
        return PercentileThreshold(**input_thresh)
    if _must_build_basic_threshold(input_thresh):
        return BasicThreshold(**input_thresh)
    if _must_build_bounded_threshold(input_thresh):
        return BoundedThreshold(**input_thresh)
    if _must_build_per_grid_cell_threshold(input_thresh):
        return BasicThreshold(**input_thresh)
    msg = f"Threshold cannot be built from a {type(value)}"
    raise NotImplementedError(msg)


def _get_operator(query: str) -> tuple[Operator | None, str]:
    operand = "".join(OPERAND_REGEX.findall(query))
    op = OperatorRegistry.lookup_no_error(operand)
    if op is not None:
        return op, query.replace(op.operand, "", 1)
    return None, query


def _read_string_threshold(query: str) -> tuple[str, str, float]:
    op, no_op_query = _get_operator(query)
    operand = op.operand if op else ""
    if DOY_PERCENTILE_UNIT in no_op_query:
        val = re.findall(VALUE_REGEX, no_op_query)[0]
        unit = DOY_PERCENTILE_UNIT
    elif PERIOD_PERCENTILE_UNIT in no_op_query:
        val = re.findall(VALUE_REGEX, no_op_query)[0]
        unit = PERIOD_PERCENTILE_UNIT
    else:
        try:
            quantity = xc_units.Quantity(no_op_query)
        except UndefinedUnitError as e:
            msg = f"Could not build threshold from {query}"
            raise InvalidIcclimArgumentError(msg) from e
        val = quantity.m
        unit = None if quantity.unitless else str(quantity.units)
    return operand, unit, val


def _build_quantity(
    quantity: None | str | float | pint.Quantity,
    default_unit: str | None,
) -> pint.Quantity | None:
    if quantity is None:
        return None
    if isinstance(quantity, xc_units.Quantity):
        return quantity
    if isinstance(quantity, (float, int)):
        if default_unit in (PERIOD_PERCENTILE_UNIT, DOY_PERCENTILE_UNIT):
            unit = None
        else:
            unit = default_unit
        return xc_units.Quantity(value=quantity, units=unit)
    if isinstance(quantity, str):
        operator, unit, value = _read_string_threshold(quantity)
        if operator is not None and operator != "":
            msg = (
                f"Cannot parse quantity '{quantity}'"
                f" The operator {operator} should be removed."
            )
            raise InvalidIcclimArgumentError(msg)
        return xc_units.Quantity(value=value, units=unit)
    msg = f"Unknown type '{type(quantity)}' for quantity {quantity}"
    raise NotImplementedError(msg)


def _read_input(
    query: str | None = None,
    operator: Operator | str | None = None,
    value: ThresholdValueType = None,
    unit: str | None = None,
    threshold_min_value: str | float | None = None,
    thresholds: tuple[Threshold, Threshold] | None = None,
    logical_link: str | LogicalLink | None = None,
    offset: str | float | pint.Quantity | None = None,
    **kwargs,
) -> ThresholdBuilderInput:
    if query is not None and _must_read_query(query, operator, value, unit):
        if _is_bounded_threshold_query(query):
            return _read_bounded_threshold_query(query)
        return _read_threshold_from_query(query, threshold_min_value, kwargs)
    if _must_read_bounded(operator, value, unit, thresholds, logical_link):
        return _read_bounded_threshold(thresholds, logical_link)
    if operator is not None:
        if (operator := OperatorRegistry.lookup_no_error(operator)) is None:
            operator = OperatorRegistry.REACH
        return {
            "operator": operator,
            "unit": unit,
            "value": value,
            "threshold_min_value": _build_quantity(threshold_min_value, unit),
            "offset": _build_quantity(offset, unit),
            **kwargs,
        }
    msg = "Could not read threshold"
    raise NotImplementedError(msg)


def _read_bounded_threshold(
    thresholds: tuple[Threshold, Threshold],
    logical_link: LogicalLink | str,
) -> ThresholdBuilderInput:
    acc = []
    for t in thresholds:
        if isinstance(t, str):
            acc.append(_read_input(t))
        elif isinstance(t, Threshold):
            acc.append(t)
        else:
            msg = f"Unknown type '{type(t)}'"
            raise NotImplementedError(msg)
    if len(acc) > 2:
        msg = "Can't build BoundedThreshold on more than 2 thresholds."
        raise NotImplementedError(msg)
    if isinstance(logical_link, str):
        logical_link = LogicalLinkRegistry.lookup(logical_link)
    return {
        "initial_query": None,
        "thresholds": tuple(acc),
        "logical_link": logical_link,
    }


def _read_threshold_from_query(
    query: str,
    threshold_min_value: None | str | float | pint.Quantity,
    kwargs: dict,
) -> ThresholdBuilderInput:
    operator, unit, value = _read_string_threshold(query)
    if (operator := OperatorRegistry.lookup_no_error(operator)) is None:
        operator = OperatorRegistry.REACH
    return {
        "operator": operator,
        "unit": unit,
        "value": value,
        "threshold_min_value": _build_quantity(threshold_min_value, unit),
        "initial_query": query,
        **kwargs,
    }


def _must_read_query(
    query: str,
    operator: Operator | str | None,
    value: ThresholdValueType | None,
    unit: str | None,
) -> bool:
    return (
        isinstance(query, str) and operator is None and value is None and unit is None
    )


def _must_read_bounded(
    operator: Operator | str | None,
    value: ThresholdValueType,
    unit: str | None,
    thresholds: tuple[Threshold, Threshold] | None,
    logical_link: str | LogicalLink | None,
) -> bool:
    return (
        operator is None
        and value is None
        and unit is None
        and thresholds is not None
        and logical_link is not None
    )


def _is_bounded_threshold_query(query: str) -> bool:
    return any(
        l_l.name.upper() in query.upper() for l_l in LogicalLinkRegistry.values()
    )


def _read_bounded_threshold_query(query: str) -> ThresholdBuilderInput:
    link = None
    split_word = None
    uppered = query.upper()
    for l_l in LogicalLinkRegistry.values():
        if l_l.name.upper() in uppered:
            link = l_l
            index_of_link = uppered.index(l_l.name.upper())
            split_word = query[index_of_link : index_of_link + len(l_l.name)]
            break
    if link is None:
        msg = f"No logical link found in {query}"
        raise InvalidIcclimArgumentError(msg)
    threshs = [t.strip() for t in query.split(split_word)]
    if len(threshs) != 2:
        msg = (
            "BoundedThreshold can only be built on 2"
            f" thresholds. We found {len(threshs)} here."
        )
        raise InvalidIcclimArgumentError(msg)
    return {
        "initial_query": query,
        "thresholds": (_read_input(threshs[0]), _read_input(threshs[1])),
        "logical_link": link,
    }


def _must_build_per_threshold(builder_input: ThresholdBuilderInput) -> bool:
    value = builder_input.get("value")
    unit = builder_input.get("unit", None)
    var_name = builder_input.get("threshold_var_name", None)
    return _has_per_unit(unit, value) or _is_per_dataset(var_name, value)


def _is_per_dataset(threshold_var_name: str, value: str | Dataset | DataArray) -> bool:
    if is_dataset_path(value) or isinstance(value, Dataset):
        thresh_da = _get_dataarray_from_dataset(threshold_var_name, value)
    else:
        thresh_da = value
    return PercentileDataArray.is_compatible(thresh_da)


def _has_per_unit(unit: str | None | Sequence[float], value: float) -> bool:
    return isinstance(value, (float, Sequence)) and (
        unit in (DOY_PERCENTILE_UNIT, PERIOD_PERCENTILE_UNIT)
    )


def _must_build_per_grid_cell_threshold(builder_input: ThresholdBuilderInput) -> bool:
    value = builder_input.get("value")
    threshold_var_name = builder_input.get("threshold_var_name", None)
    if value is None:
        # Case of comparison to normal like dcsc::TxND,
        # the threshold is setup but ::prepare must be called
        # to initialize the value
        return True
    if is_dataset_path(value) or isinstance(value, Dataset):
        thresh_da = _get_dataarray_from_dataset(threshold_var_name, value)
        return not PercentileDataArray.is_compatible(thresh_da)
    return False


def _must_build_basic_threshold(builder_input: ThresholdBuilderInput) -> bool:
    value = builder_input.get("value")
    return is_number_sequence(value) or isinstance(value, (DataArray, float, int))


def _must_build_bounded_threshold(builder_input: ThresholdBuilderInput) -> bool:
    logical_link = builder_input.get("logical_link")
    return logical_link is not None


def _get_dataarray_from_dataset(
    threshold_var_name: str | None,
    value: Dataset | str,
) -> DataArray:
    ds = value if isinstance(value, Dataset) else read_dataset(value, standard_var=None)
    if threshold_var_name is None:
        if len(ds.data_vars) == 1:
            threshold_var_name = get_name_of_first_var(ds)
        else:
            names = find_standard_vars(ds)
            if len(names) == 1:
                threshold_var_name = names[0]
            else:
                msg = (
                    f"Could not guess the variable to use as a threshold in {ds}."
                    f" Use `threshold_var_name` to specify which variable should be"
                    f" used."
                )
                raise InvalidIcclimArgumentError(msg)
    return ds[threshold_var_name]
