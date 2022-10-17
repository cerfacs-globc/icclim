from __future__ import annotations

import abc
import re
from datetime import datetime
from typing import Any, Callable, Sequence, TypedDict, Union

import jinja2
import numpy as np
import pint
import xarray as xr
from xarray import DataArray, Dataset
from xclim.core.bootstrapping import percentile_bootstrap
from xclim.core.calendar import build_climatology_bounds, percentile_doy, resample_doy
from xclim.core.units import convert_units_to, str2pint
from xclim.core.units import units as xc_units
from xclim.core.utils import PercentileDataArray, calc_perc

from icclim.generic_indices.threshold_templates import (
    EN_THRESHOLD_TEMPLATE,
    PercentileTemplateConfig,
    ThresholdMetadata,
)
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.constants import (
    DEFAULT_DOY_WINDOW,
    DOY_COORDINATE,
    DOY_PERCENTILE_UNIT,
    PERIOD_PERCENTILE_UNIT,
    UNITS_KEY,
)
from icclim.models.frequency import Frequency
from icclim.models.logical_link import LogicalLink, LogicalLinkRegistry
from icclim.models.operator import Operator, OperatorRegistry
from icclim.models.quantile_interpolation import (
    QuantileInterpolation,
    QuantileInterpolationRegistry,
)
from icclim.pre_processing.input_parsing import (
    build_reference_da,
    find_standard_vars,
    get_name_of_first_var,
    is_dataset_path,
    read_clim_bounds,
    read_dataset,
    standardize_percentile_dim_name,
)
from icclim.utils import is_number_sequence

ThresholdValueType = Union[
    str, float, int, Dataset, DataArray, Sequence[Union[float, int, str]], None
]


class ThresholdBuilderInput(TypedDict, total=False):
    """
    Data transfert object mapping all possible configuration to build any threshold.
    """

    operator: Operator
    value: ThresholdValueType
    unit: str | None
    threshold_var_name: str | None
    initial_query: str | None
    threshold_min_value: pint.Quantity | None
    # percentile conf:
    doy_window_width: int | None
    only_leap_years: bool | None
    interpolation: str | QuantileInterpolation | None
    reference_period: Sequence[datetime | str] | None
    # bounded conf:
    thresholds: tuple[
        ThresholdBuilderInput | Threshold, ThresholdBuilderInput | Threshold
    ] | None
    logical_link: LogicalLink


def build_threshold(
    query: str | None = None,
    *,
    operator: Operator | str = None,
    value: ThresholdValueType = None,
    unit: str | None = None,
    threshold_min_value: str | float | None | pint.Quantity = None,
    thresholds: tuple[Threshold, Threshold] | None = None,
    logical_link: str | LogicalLink | None = None,
    **kwargs,
) -> Threshold:
    """Factory for thresholds.

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
        query supersede `operator`, `value` and `unit` parameters.
    operator: Operator | str = None
        keyword argument only.
        The operator either as an instance of Operator or as a compatible string.
        See :py:class:`OperatorRegistry` for the list of all operators.
        When query is None and operator is None, the default ``Operator.REACH`` is used.
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
    kwargs
        Additional arguments to build a PercentileThreshold.
        See :py:class:`PercentileThreshold` constructor for the complete list
        of possible arguments.

    Examples
    --------
    .. code-block:: python

        # Scalar threshold
        scalar_t = build_threshold(">= 30 degC")
        assert isinstance(scalar_t, BasicThreshold)

        # Daily percentile threshold
        doy_t = build_threshold(">= 30 doy_per")
        assert isinstance(doy_t, PercentileThreshold)

        # Per grid-cell threshold
        grided_t = build_threshold(
            operator=">=", value="path/to/tasmax_thresholds.nc", unit="K"
        )
        assert isinstance(grided_t, BasicThreshold)

        # Daily percentile threshold, from a file
        tasmax = xarray.open_dataset("path/to/tasmax_thresholds.nc").tasmax
        doys = xclim.core.calendar.percentile_doy(tasmax)
        doy_file_t = build_threshold(operator=">=", value=doys)
        assert isinstance(doy_file_t, PercentileThreshold)

        # Bounded threshold
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
        **kwargs,
    )
    if _must_build_per_threshold(input_thresh):
        return _build_per_threshold(input_thresh)
    elif _must_build_basic_threshold(input_thresh):
        return _build_basic_threshold(input_thresh)
    elif _must_build_bounded_threshold(input_thresh):
        return _build_bounded_threshold(input_thresh)
    else:
        raise NotImplementedError(f"Threshold cannot be built from a {type(value)}")


class Threshold(metaclass=abc.ABCMeta):
    """
    - scalar thresh:                               "> 25 ºC"
    - per grid cell thresh:                        "> data.nc"
    - doy percentile threshold:                    "> 98th doy_per"
    - period percentile threshold:                 "> 75th period_per"
    - period percentile threshold with min value:  "> 98th period_per",
                                                   threshold_min_value= "1mm"
    - sequence thresholds (or):                    "> 10 ºC, > 25 ºC"
                                                     thresholds are a new dimension
    """

    operator: Operator | str
    value: ThresholdValueType
    unit: str | None = None
    initial_query: str | None
    threshold_min_value: pint.Quantity | None = None
    threshold_var_name: str | None

    @abc.abstractmethod
    def format_metadata(
        self, *, jinja_scope: dict[str, Any], jinja_env: jinja2.Environment, **kwargs
    ) -> ThresholdMetadata:
        """Get a dictionary of standardized threshold metadata."""
        ...

    @abc.abstractmethod
    def __eq__(self, other: Threshold) -> bool:
        ...

    def __and__(self, other: Threshold) -> BoundedThreshold:
        return BoundedThreshold(
            self, other, LogicalLinkRegistry.LOGICAL_AND, initial_query=None
        )

    def __or__(self, other: Threshold) -> BoundedThreshold:
        return BoundedThreshold(
            self, other, LogicalLinkRegistry.LOGICAL_OR, initial_query=None
        )

    @abc.abstractmethod
    def compute(
        self,
        comparison_data: xr.DataArray,
        override_op: Callable[[DataArray, DataArray], DataArray] | None = None,
        **kwargs,
    ) -> DataArray:
        """Compute the exceedance of comparison_data over/below self threshold
        depending on `self` operator.
        The operator can be overridden by `override_op`. This is needed when
        self.operator is REACH.

        Parameters
        ----------
        comparison_data: xr.DataArray
            Data that must be compared to self threshold
        override_op: Callable[[DataArray, DataArray], DataArray] | None
            Operator to override self.operator compute function.
            Optional.
        kwargs:
            Keyword arguments passed to the concrete compute implementations
            This makes the `compute` interface contract not always reliable.
            So we assume to not really respected LSP here.
        """
        ...


class BoundedThreshold(Threshold):
    """
    Threshold binding class to compute two thresholds for a single variable.
    The logical link can be either "OR" or "AND".
    """

    left_threshold: Threshold
    right_threshold: Threshold
    logical_link: LogicalLink

    def __init__(
        self,
        left_threshold: Threshold,
        right_threshold: Threshold,
        logical_link: LogicalLink,
        initial_query: str | None,
    ):
        self.left_threshold = left_threshold
        self.right_threshold = right_threshold
        self.logical_link = logical_link
        self.initial_query = initial_query

    def compute(
        self,
        comparison_data: xr.DataArray,
        override_op: Callable[[DataArray, DataArray], DataArray] | None = None,
        **kwargs,
    ) -> DataArray:
        left_res = self.left_threshold.compute(
            comparison_data, override_op=override_op, **kwargs
        )
        right_res = self.right_threshold.compute(
            comparison_data, override_op=override_op, **kwargs
        )
        return self.logical_link.compute([left_res, right_res])

    def format_metadata(
        self, *, jinja_scope: dict[str, Any], jinja_env: jinja2.Environment, **kwargs
    ) -> ThresholdMetadata:
        templates = self._get_metadata_templates()
        conf = {
            "left_threshold": self.left_threshold.format_metadata(
                jinja_scope=jinja_scope, jinja_env=jinja_env, **kwargs
            ),
            "logical_link": self.logical_link,
            "right_threshold": self.right_threshold.format_metadata(
                jinja_scope=jinja_scope, jinja_env=jinja_env, **kwargs
            ),
        }
        conf.update(jinja_scope)
        return {
            k: jinja_env.from_string(v, globals=conf).render()
            for k, v in templates.items()
        }

    def __eq__(self, other: BoundedThreshold):
        return (
            isinstance(other, BoundedThreshold)
            and self.initial_query == other.initial_query
            and self.left_threshold == other.left_threshold
            and self.right_threshold == other.right_threshold
            and self.logical_link == other.logical_link
        )

    def _get_metadata_templates(self) -> ThresholdMetadata:
        return EN_THRESHOLD_TEMPLATE["bounded_threshold"]

    class BoundedThresholdInput(TypedDict):
        left_threshold: Threshold
        right_threshold: Threshold
        logical_link: LogicalLink
        initial_query: str | None


class PercentileThreshold(Threshold):
    reference_period: Sequence[str]
    doy_window_width: int
    only_leap_years: bool
    interpolation: QuantileInterpolation

    is_doy_per_threshold: bool
    _prepared_value: PercentileDataArray
    _initial_unit: str | None
    _initial_value: list[float] | None

    @property
    def unit(self) -> str | None:
        if self.is_ready:
            return self._prepared_value.attrs[UNITS_KEY]
        return self._initial_unit

    @unit.setter
    def unit(self, unit):
        if self.is_ready:
            if self.value.attrs.get(UNITS_KEY, None) is not None and unit is not None:
                self._prepared_value = convert_units_to(self._prepared_value, unit)
            self.value.attrs[UNITS_KEY] = unit

    @property
    def value(self) -> PercentileDataArray:
        if self.is_ready:
            return self._prepared_value
        else:
            raise RuntimeError(
                "Property `value` is not ready. For PercentileDataArray,"
                " you must call `.prepare` first and fill `studied_data`"
                " parameter in order to prepare `value`."
            )

    def __init__(
        self,
        operator: str | Operator,
        value: str | int | float | DataArray,
        unit: str | None,
        doy_window_width: int,
        only_leap_years: bool,
        interpolation: QuantileInterpolation,
        reference_period: Sequence[datetime | str] | None,
        threshold_min_value: pint.Quantity | None,
        initial_query: str | None,
        is_doy_per_threshold: bool,
        threshold_var_name: str | None,
    ):
        if isinstance(value, DataArray):
            self.prepare = None
            self._prepared_value = PercentileDataArray.from_da(value)
            self.is_ready = True
            self._initial_unit = None
            self._initial_value = None
            self.unit = self._prepared_value.attrs[UNITS_KEY]
        else:
            self.is_ready = False
            self._initial_unit = unit
            if not isinstance(value, list):
                value = [value]
            self._initial_value = [float(x) for x in value]
            self.unit = unit
        self.operator = operator
        self.threshold_var_name = threshold_var_name
        self.initial_query = initial_query
        self.threshold_min_value = threshold_min_value
        self.reference_period = reference_period
        self.doy_window_width = doy_window_width
        self.only_leap_years = only_leap_years
        self.interpolation = interpolation
        self.unit = unit
        self.is_doy_per_threshold = is_doy_per_threshold

    def prepare(self, studied_data: DataArray) -> None:
        if self._initial_unit == DOY_PERCENTILE_UNIT:
            prepared_data = _build_doy_per(
                studied_data=studied_data,
                per_val=self._initial_value,
                reference_period=self.reference_period,
                interpolation=self.interpolation,
                only_leap_years=self.only_leap_years,
                doy_window_width=self.doy_window_width,
                percentile_min_value=self.threshold_min_value,
            )
        elif self._initial_unit == PERIOD_PERCENTILE_UNIT:
            prepared_data = _build_period_per(
                studied_data=studied_data,
                per_val=self._initial_value,
                reference_period=self.reference_period,
                interpolation=self.interpolation,
                only_leap_years=self.only_leap_years,
                percentile_min_value=self.threshold_min_value,
            )
        else:
            raise NotImplementedError(
                f"Unknown percentile unit" f" '{self._initial_unit}'."
            )
        self._prepared_value = prepared_data.chunk("auto")
        self.is_ready = True

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, PercentileThreshold)
            and self.initial_query == other.initial_query
            and self.doy_window_width == other.doy_window_width
            and self.only_leap_years == other.only_leap_years
            and self.interpolation == other.interpolation
            and self.reference_period == other.reference_period
            and self.unit == other.unit
            and self.threshold_min_value == other.threshold_min_value
        )

    # noinspection PyMethodOverriding
    # (reason: with * and **kwargs we can have a different signature while still
    # being liskov proof)
    def format_metadata(
        self,
        *,
        jinja_scope: dict[str, Any],
        jinja_env: jinja2.Environment,
        src_freq: Frequency,
        must_run_bootstrap: bool = False,
        **kwargs,
    ) -> ThresholdMetadata:
        per_coord = self.value.coords["percentiles"]
        templates = self._get_metadata_templates(per_coord)
        climatology_bounds: list[str] = self.value.attrs.get("climatology_bounds")
        conf: PercentileTemplateConfig = {
            "climatology_bounds": climatology_bounds,
            "doy_window_width": self.doy_window_width,
            "src_freq": src_freq,
            "operator": self.operator,
            "unit": self.unit,
            "per_coord": per_coord.values,
            "threshold_min_value": self.threshold_min_value,
            "must_run_bootstrap": must_run_bootstrap,
        }
        conf.update(jinja_scope)
        return {
            k: jinja_env.from_string(v, globals=conf).render()
            for k, v in templates.items()
        }

    def _get_metadata_templates(self, per_coord: DataArray) -> ThresholdMetadata:
        if self.is_doy_per_threshold:
            if per_coord.size == 1:
                return EN_THRESHOLD_TEMPLATE["single_doy_percentile"]
            else:
                return EN_THRESHOLD_TEMPLATE["multiple_doy_percentiles"]
        else:
            if per_coord.size == 1:
                return EN_THRESHOLD_TEMPLATE["single_period_percentile"]
            else:
                return EN_THRESHOLD_TEMPLATE["multiple_period_percentiles"]

    def compute(
        self,
        comparison_data: xr.DataArray,
        override_op: Callable[[DataArray, DataArray], DataArray] | None = None,
        **kwargs,
    ) -> DataArray:
        if override_op is not None:
            op = override_op
        else:
            op = self.operator
        if self.is_ready:
            return self._per_compute(
                comparison_data,
                self.value,
                op,
                self.is_doy_per_threshold,
                kwargs.get("freq", None),
                kwargs.get("bootstrap", False),
            )
        else:
            raise RuntimeError(
                "This PercentileThreshold is not ready. You must first call `.prepare`"
                " with a `studied_data` parameter in order to prepare the threshold"
                " for computation."
            )

    @percentile_bootstrap
    def _per_compute(
        self,
        comparison_data: xr.DataArray,
        per: xr.DataArray,
        op: Callable[[DataArray, DataArray], DataArray],
        is_doy_per_threshold: bool,
        freq: str,  # noqa used by @percentile_bootstrap
        bootstrap: bool,  # noqa used by @percentile_bootstrap
    ) -> DataArray:
        if is_doy_per_threshold:
            threshold_value = resample_doy(per, comparison_data)
        else:
            threshold_value = per
        return op(comparison_data, threshold_value)

    class PercentileThresholdInput(TypedDict):
        operator: Operator
        value: int | float | DataArray
        unit: str | None
        threshold_var_name: str | None
        initial_query: str | None
        threshold_min_value: pint.Quantity

        doy_window_width: int
        only_leap_years: bool
        interpolation: str | QuantileInterpolation
        reference_period: Sequence[datetime | str]


class BasicThreshold(Threshold):
    @property
    def unit(self) -> str | None:
        return self.value.attrs[UNITS_KEY]

    @unit.setter
    def unit(self, unit):
        if self.value.attrs.get(UNITS_KEY, None) is not None and unit is not None:
            self.value = convert_units_to(self.value, unit)
        self.value.attrs[UNITS_KEY] = unit

    def __init__(
        self,
        operator: Operator | str,
        value: ThresholdValueType,
        unit: str | None = None,
        initial_query: str | None = None,
        threshold_min_value: pint.Quantity | None = None,
        threshold_var_name: str | None = None,
    ):
        self.operator = operator
        self.value = value
        self.unit = unit
        self.is_ready = True
        self.threshold_var_name = threshold_var_name
        self.initial_query = initial_query
        if (
            unit is not None
            and threshold_min_value is not None
            and threshold_min_value.dimensionless
        ):
            self.threshold_min_value = float(threshold_min_value.m) * str2pint(unit)
        else:
            self.threshold_min_value = threshold_min_value
        self.prepare = None

    def __eq__(self, other):
        return (
            isinstance(other, BasicThreshold)
            and self.operator == other.operator
            and self.value == other.value
            and self.unit == other.unit
            and self.initial_query == other.initial_query
            and self.threshold_min_value == other.threshold_min_value
        )

    def _get_metadata_templates(self) -> ThresholdMetadata:
        if self.value.size == 1:
            return EN_THRESHOLD_TEMPLATE["single_value"]
        else:
            return EN_THRESHOLD_TEMPLATE["multiple_values"]

    def format_metadata(
        self,
        jinja_scope: dict[str, Any],
        jinja_env: jinja2.Environment,
        **kwargs,
    ) -> ThresholdMetadata:
        templates = self._get_metadata_templates()
        conf = {
            "operator": self.operator,
            "unit": self.unit,
            "threshold_min_value": self.threshold_min_value,
            "must_run_bootstrap": True,
            "value": self.value,
        }
        if self.value.size > 1:
            conf["min_value"] = np.format_float_positional(
                self.value.min().values[()], 3
            )
            conf["max_value"] = np.format_float_positional(
                self.value.max().values[()], 3
            )
        conf.update(jinja_scope)
        return {
            k: jinja_env.from_string(v, globals=conf).render()
            for k, v in templates.items()
        }

    def compute(
        self,
        comparison_data: xr.DataArray,
        override_op: Callable[[DataArray, DataArray], DataArray] | None = None,
        **kwargs,
    ) -> DataArray:
        if override_op is not None:
            return override_op(comparison_data, self.value)
        return self.operator.compute(comparison_data, self.value)


def _build_period_per(
    studied_data: DataArray,
    per_val: Sequence[float],
    reference_period: Sequence[str],
    interpolation: QuantileInterpolation,
    only_leap_years: bool,
    percentile_min_value: pint.Quantity | None,
) -> PercentileDataArray:
    reference = build_reference_da(
        studied_data,
        reference_period,
        only_leap_years,
        percentile_min_value=percentile_min_value,
    )
    computed_per = xr.apply_ufunc(
        calc_perc,
        reference,
        input_core_dims=[["time"]],
        output_core_dims=[["percentiles"]],
        keep_attrs=True,
        kwargs=dict(
            percentiles=per_val,
            alpha=interpolation.alpha,
            beta=interpolation.beta,
            copy=True,
        ),
        dask="parallelized",
        output_dtypes=[reference.dtype],
        dask_gufunc_kwargs=dict(output_sizes={"percentiles": 1}, allow_rechunk=True),
    )
    computed_per = computed_per.assign_coords(
        percentiles=xr.DataArray(per_val, dims=("percentiles",))
    )
    res = PercentileDataArray.from_da(
        source=computed_per,
        climatology_bounds=build_climatology_bounds(reference),
    )
    return res


def _build_doy_per(
    studied_data: DataArray,
    per_val: Sequence[float],
    reference_period: Sequence[str],
    interpolation: QuantileInterpolation,
    only_leap_years: bool,
    doy_window_width: int,
    percentile_min_value: pint.Quantity | None,
) -> PercentileDataArray:
    reference = build_reference_da(
        studied_data,
        reference_period,
        only_leap_years,
        percentile_min_value,
    )
    res = percentile_doy(
        arr=reference,
        window=doy_window_width,
        per=per_val,
        alpha=interpolation.alpha,
        beta=interpolation.beta,
    ).compute()  # "optimization" (diminish dask scheduler workload)
    return res


def _read_string_threshold(query: str) -> tuple[str, str, float]:
    value = re.findall(r"-?\d+\.?\d*", query)
    if len(value) == 0:
        raise InvalidIcclimArgumentError(f"Cannot build threshold from '{query}'")
    value = value[0]
    value_index = query.find(value)
    operator = query[0:value_index].strip()
    if operator == "":
        operator = None
    if query.endswith(value):
        unit = None
    else:
        unit = query[value_index + len(value) :].strip()
    return operator, unit, float(value)


def _build_min_value(
    threshold_min_value: None | str | float | pint.Quantity,
    default_unit: str | None,
) -> pint.Quantity | None:
    if threshold_min_value is None:
        return None
    elif isinstance(threshold_min_value, xc_units.Quantity):
        return threshold_min_value
    elif isinstance(threshold_min_value, (float, int)):
        if (
            default_unit == PERIOD_PERCENTILE_UNIT
            or default_unit == DOY_PERCENTILE_UNIT
        ):
            unit = None
        else:
            unit = default_unit
        return xc_units.Quantity(value=threshold_min_value, units=unit)
    elif isinstance(threshold_min_value, str):
        operator, unit, value = _read_string_threshold(threshold_min_value)
        if operator is not None and operator != "" and operator != ">=":
            raise InvalidIcclimArgumentError(
                f"cannot compute threshold_min_value with"
                f" {operator}. You don't need to fill an"
                f" operator for this parameter."
            )
        return xc_units.Quantity(value=value, units=unit)
    else:
        raise NotImplementedError(
            f"Unknown type '{type(threshold_min_value)}' for `threshold_min_value`."
        )


def _read_input(
    query: str | None = None,
    operator: Operator | str = None,
    value: ThresholdValueType = None,
    unit: str | None = None,
    threshold_min_value: str | float | None = None,
    thresholds: tuple[Threshold, Threshold] | None = None,
    logical_link: str | LogicalLink | None = None,
    **kwargs,
) -> ThresholdBuilderInput:
    if _must_read_query(query, operator, value, unit):
        if _is_bounded_threshold_query(query):
            return _read_bounded_threshold_query(query)
        else:
            return _read_threshold_from_query(query, threshold_min_value, kwargs)
    elif _must_read_bounded(operator, value, unit, thresholds, logical_link):
        return _read_bounded_threshold(thresholds, logical_link)
    elif _must_read_from_args(operator, value):
        if (operator := OperatorRegistry.lookup(operator, no_error=True)) is None:
            operator = OperatorRegistry.REACH
        return {
            "operator": operator,
            "unit": unit,
            "value": value,
            "threshold_min_value": _build_min_value(threshold_min_value, unit),
            **kwargs,
        }
    else:
        raise NotImplementedError("Could not read threshold")


def _read_bounded_threshold(
    thresholds: tuple[Threshold, Threshold], logical_link: LogicalLink | str
) -> ThresholdBuilderInput:
    acc = []
    for t in thresholds:
        if isinstance(t, str):
            acc.append(_read_input(t))
        elif isinstance(t, Threshold):
            acc.append(t)
        else:
            raise NotImplementedError(f"Unknown type '{type(t)}'")
    if len(acc) > 2:
        raise NotImplementedError(
            "Can't build BoundedThreshold on more than 2 thresholds."
        )
    if isinstance(logical_link, str):
        logical_link = LogicalLinkRegistry.lookup(logical_link)
    return {  # noqa
        "initial_query": None,
        "thresholds": tuple(acc),
        "logical_link": logical_link,
    }


def _read_threshold_from_query(
    query: str,
    threshold_min_value: None | str | float | xc_units.Quantity,
    kwargs: dict,
) -> ThresholdBuilderInput:
    operator, unit, value = _read_string_threshold(query)
    if (operator := OperatorRegistry.lookup(operator, no_error=True)) is None:
        operator = OperatorRegistry.REACH
    return {
        "operator": operator,
        "unit": unit,
        "value": value,
        "threshold_min_value": _build_min_value(threshold_min_value, unit),
        "initial_query": query,
        **kwargs,
    }


def _must_read_query(
    query: str | None,
    operator: Operator | str,
    value: ThresholdValueType,
    unit: str | None,
) -> bool:
    return (
        isinstance(query, str) and operator is None and value is None and unit is None
    )


def _must_read_bounded(
    operator: Operator | str,
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


def _must_read_from_args(operator: Operator | str, value: ThresholdValueType) -> bool:
    return operator is not None and value is not None


def _is_bounded_threshold_query(query: str) -> bool:
    return any(
        [l_l.name.upper() in query.upper() for l_l in LogicalLinkRegistry.values()]
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
        raise InvalidIcclimArgumentError(f"No logical link found in {query}")
    threshs = query.split(split_word)
    if len(threshs) != 2:
        raise InvalidIcclimArgumentError(
            "BoundedThreshold can only be built on 2"
            f" thresholds. We found {len(threshs)} here."
        )
    return {
        "initial_query": query,
        "thresholds": (_read_input(threshs[0]), _read_input(threshs[1])),
        "logical_link": link,
    }


def _must_build_per_threshold(input: ThresholdBuilderInput) -> bool:
    value = input.get("value")
    unit = input.get("unit", None)
    var_name = input.get("threshold_var_name", None)
    return _has_per_unit(unit, value) or _is_per_dataset(var_name, value)


def _is_per_dataset(threshold_var_name: str, value: str | Dataset | DataArray) -> bool:
    if is_dataset_path(value) or isinstance(value, Dataset):
        thresh_da = _get_dataarray_from_dataset(threshold_var_name, value)
    else:
        thresh_da = value
    return PercentileDataArray.is_compatible(thresh_da)


def _has_per_unit(unit: str | None | Sequence[float], value: float) -> bool:
    return isinstance(value, (float, Sequence)) and (
        unit == DOY_PERCENTILE_UNIT or unit == PERIOD_PERCENTILE_UNIT
    )


def _must_build_basic_threshold(input: ThresholdBuilderInput) -> bool:
    value = input.get("value")
    threshold_var_name = input.get("threshold_var_name", None)
    if is_dataset_path(value) or isinstance(value, Dataset):
        thresh_da = _get_dataarray_from_dataset(threshold_var_name, value)
        return not PercentileDataArray.is_compatible(thresh_da)
    return (
        is_number_sequence(value)
        or isinstance(value, (float, int))
        or isinstance(value, DataArray)
    )


def _must_build_bounded_threshold(input: ThresholdBuilderInput) -> bool:
    logical_link = input.get("logical_link")
    return logical_link is not None


def _get_bounded_threshold_conf(
    conf: ThresholdBuilderInput,
) -> BoundedThreshold.BoundedThresholdInput:
    thresholds = conf.get("thresholds")
    logical_link: LogicalLink = conf.get("logical_link")
    initial_query = conf.get("initial_query")
    if isinstance(thresholds[0], Threshold):
        t_left = thresholds[0]
    else:
        t_left = build_threshold(**thresholds[0])
    if isinstance(thresholds[1], Threshold):
        t_right = thresholds[1]
    else:
        t_right = build_threshold(**thresholds[1])
    return {  # noqa
        "left_threshold": t_left,
        "right_threshold": t_right,
        "logical_link": logical_link,
        "initial_query": initial_query,
    }


def _get_percentile_threshold_conf(
    conf: ThresholdBuilderInput,
) -> PercentileThreshold.PercentileThresholdInput:
    value: DataArray | float | int | Sequence[float] = conf.get("value")
    unit = conf.get("unit", None)
    threshold_var_name = conf.get("threshold_var_name", None)
    reference_period = conf.get("reference_period", None)
    interpolation = conf.get(
        "interpolation", QuantileInterpolationRegistry.MEDIAN_UNBIASED
    )
    interpolation = QuantileInterpolationRegistry.lookup(interpolation)
    if is_dataset_path(value) or isinstance(value, Dataset):
        value, is_doy_per_threshold = _build_per_thresh_from_dataset(
            value=value,
            unit=unit,
            threshold_var_name=threshold_var_name,
            reference_period=reference_period,
        )
    else:
        is_doy_per_threshold = unit == DOY_PERCENTILE_UNIT
    return dict(  # noqa (wtf typing)
        value=value,
        operator=conf.get("operator"),
        unit=conf.get("unit", None),
        doy_window_width=conf.get("doy_window_width", DEFAULT_DOY_WINDOW),
        only_leap_years=conf.get("only_leap_years", False),
        interpolation=interpolation,
        reference_period=reference_period,
        threshold_min_value=conf.get("threshold_min_value", None),
        initial_query=conf.get("initial_query", None),
        threshold_var_name=threshold_var_name,
        is_doy_per_threshold=is_doy_per_threshold,
    )


def _get_basic_threshold_conf(input: ThresholdBuilderInput) -> ThresholdBuilderInput:
    value = input.get("value")
    unit = input.get("unit", None)
    threshold_var_name = input.get("threshold_var_name", None)
    initial_query = input.get("initial_query", None)
    operator: Operator = input.get("operator")
    threshold_min_value = input.get("threshold_min_value", None)
    if (
        is_number_sequence(value) or isinstance(value, (float, int))
    ) and threshold_min_value is not None:
        raise InvalidIcclimArgumentError("Cannot use threshold_min_value with scalars")
    if is_dataset_path(value) or isinstance(value, Dataset):
        # e.g. build_threshold(">", "thresh*.nc" , "degC")
        thresh_da = _get_dataarray_from_dataset(threshold_var_name, value)
        built_value = _apply_min_value(thresh_da, threshold_min_value)
        if unit is None:
            unit = built_value.attrs.get(UNITS_KEY, None)
    elif isinstance(value, DataArray):
        built_value = _apply_min_value(value, threshold_min_value)
        if unit is None:
            unit = built_value.attrs.get(UNITS_KEY, None)
    elif is_number_sequence(value):
        built_value = DataArray(
            name="threshold",
            data=value,
            attrs={UNITS_KEY: unit},
            dims="threshold",
            coords={"threshold": value},
        )
    elif isinstance(value, (float, int)):
        # e.g. build_threshold(">", [2,3,4], "degC")
        built_value = DataArray(name="threshold", data=value, attrs={UNITS_KEY: unit})
    else:
        raise NotImplementedError(f"Cannot build threshold from a {type(value)}.")
    if unit is not None:
        built_value = convert_units_to(built_value, unit)
    return dict(  # noqa
        operator=operator,
        value=built_value,
        unit=unit,
        initial_query=initial_query,
        threshold_var_name=threshold_var_name,
        threshold_min_value=threshold_min_value,
    )


def _apply_min_value(thresh_da: DataArray, min_value: pint.Quantity | None):
    if min_value is not None:
        if min_value.dimensionless:
            min_value = convert_units_to(min_value.m, thresh_da)
        else:
            min_value = convert_units_to(str(min_value), thresh_da)
        built_value = thresh_da.where(thresh_da > min_value, np.nan)
        return built_value
    else:
        return thresh_da


def _get_dataarray_from_dataset(
    threshold_var_name: str | None, value: Dataset | str
) -> DataArray:
    if isinstance(value, Dataset):
        ds = value
    else:
        ds = read_dataset(value, standard_var=None)
    if threshold_var_name is None:
        if len(ds.data_vars) == 1:
            threshold_var_name = get_name_of_first_var(ds)
        else:
            names = find_standard_vars(ds)
            if len(names) == 1:
                threshold_var_name = names[0]
            else:
                raise InvalidIcclimArgumentError(
                    f"Could not guess the variable to use as a threshold in {ds}."
                    f" Use `threshold_var_name` to specify which variable should be"
                    f" used."
                )
    thresh_da = ds[threshold_var_name]
    return thresh_da


def _build_per_thresh_from_dataset(
    value: ThresholdValueType,
    unit: str | None,
    threshold_var_name: str,
    reference_period: Sequence[datetime | str],
) -> tuple[DataArray, bool]:
    thresh_da = _get_dataarray_from_dataset(threshold_var_name, value)
    built_value = PercentileDataArray.from_da(
        standardize_percentile_dim_name(thresh_da),
        read_clim_bounds(reference_period, thresh_da),
    )
    if unit is not None:
        if built_value.attrs.get(UNITS_KEY, None) is not None:
            built_value = convert_units_to(built_value, unit)
        built_value.attrs[UNITS_KEY] = unit
    return built_value, DOY_COORDINATE in built_value.coords


def _build_basic_threshold(input_thresh: ThresholdBuilderInput):
    config = _get_basic_threshold_conf(input_thresh)
    return BasicThreshold(**config)


def _build_per_threshold(conf: ThresholdBuilderInput) -> PercentileThreshold:
    config = _get_percentile_threshold_conf(conf)
    return PercentileThreshold(**config)


def _build_bounded_threshold(conf: ThresholdBuilderInput) -> BoundedThreshold:
    config = _get_bounded_threshold_conf(conf)
    return BoundedThreshold(**config)
