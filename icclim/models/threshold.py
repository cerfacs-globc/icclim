from __future__ import annotations

import abc
import re
from datetime import datetime
from typing import Any, Sequence, TypedDict, Union

import jinja2
import numpy as np
import pint
import xarray as xr
from pint import Quantity
from xarray import DataArray, Dataset
from xclim.core.calendar import build_climatology_bounds, percentile_doy
from xclim.core.units import convert_units_to
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
    operator: Operator
    value: int | float | DataArray
    unit: str | None
    threshold_var_name: str | None
    initial_query: str | None
    threshold_min_value: Quantity

    doy_window_width: int | None
    only_leap_years: bool | None
    interpolation: str | QuantileInterpolation | None
    reference_period: Sequence[datetime | str] | None


class PercentileThresholdInput(TypedDict):
    operator: Operator
    value: int | float | DataArray
    unit: str | None
    threshold_var_name: str | None
    initial_query: str | None
    threshold_min_value: Quantity

    doy_window_width: int
    only_leap_years: bool
    interpolation: str | QuantileInterpolation
    reference_period: Sequence[datetime | str]


def build_threshold(
    query: str | None = None,
    *,
    operator: Operator | str = None,
    value: ThresholdValueType = None,
    unit: str | None = None,
    threshold_min_value: str | float | None | pint.Quantity = None,
    **kwargs,
):
    """Factory for thresholds.

    Parameters
    ----------

    query: str | None = None
        todo: [bounded threshold] update query definition
        string query describing a threshold.
        It must describe an operator followed by a threshold value and optionally a unit
        such as "> 10 degC".
        It acts as a shorthand for ``operator``, ``value`` and ``unit`` parameters for
        simple threshold.
        Don't use ``query`` when value is a DataArray, a Dataset or a path to a
        netcdf/zarr storage, instead use ``operator``, ``value`` and ``unit``.
        query supersede `operator`, `value` and `unit` parameters.
    operator: Operator | str = None
        keyword argument only.
        The operator either as an instance of Operator or as a compatible string.
        See :class:`icclim.models.operator.OperatorRegistry` for the list of all
        operators.
        When query is None and operator is None, the default ``Operator.REACH`` is used.
    value: str | float | int | Dataset | DataArray | Sequence[float | int | str] | None
        todo: [bounded threshold] update definition  (for the sequence of scalars,
        todo: (suite)             if LogicalLink is None, keep the same behavior)
        keyword argument only.
        The threshold value(s), default to None.
        It can be:
        * a simple scalar threshold
        * in combinaison with ``unit``, a percentile that will be computed per-grid cell
        * per-grid cell thresholds defined by a DataArray, a Dataset or a string path to
        a netcdf/zarr.
        * a sequence of scalars, the indicator will then be computed for each value and
        a specific dimension will be created
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
    kwargs: dict
        todo: [bounded threshold] update definition
        Additional arguments to build a PercentileThreshold.
        See :class:`PercentileThreshold` constructor for the complete list
        of possible arguments.

    Examples
    --------
    .. code-block:: python

        t1 = build_threshold(">= 30 degC")
        assert isinstance(t1, BasicThreshold)
        t2 = build_threshold(">= 30 doy_per")
        assert isinstance(t2, PercentileThreshold)



    """
    input_thresh = _read_input(
        query, operator, value, unit, threshold_min_value, **kwargs
    )
    if _must_build_per_threshold(input_thresh):
        return _build_per_threshold(input_thresh)
    elif must_build_basic_threshold(input_thresh):
        return _build_basic_threshold(input_thresh)
    else:
        raise NotImplementedError(f"Threshold cannot be built from a {type(value)}")


def _build_basic_threshold(input_thresh: ThresholdBuilderInput):
    config = _get_basic_threshold_conf(input_thresh)
    return BasicThreshold(**config)


def _build_per_threshold(conf: ThresholdBuilderInput) -> PercentileThreshold:
    config = _get_percentile_threshold_conf(conf)
    return PercentileThreshold(**config)


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
    threshold_min_value: Quantity | None
    threshold_var_name: str | None

    @abc.abstractmethod
    def format_metadata(
        self, *, jinja_scope: dict[str, Any], jinja_env: jinja2.Environment, **kwargs
    ) -> ThresholdMetadata:
        """Get a dictionary of standardized threshold metadata."""
        ...

    @abc.abstractmethod
    def __eq__(self, other):
        ...


class PercentileThreshold(Threshold):
    reference_period: Sequence[str]
    doy_window_width: int
    only_leap_years: bool
    interpolation: QuantileInterpolation

    is_doy_per_threshold: bool
    _prepared_value: PercentileDataArray
    _initial_unit: str | None
    _initial_value: float | None

    @property
    def unit(self) -> str | None:
        if self.is_ready:
            return self._prepared_value.attrs[UNITS_KEY]
        return self._initial_unit

    @unit.setter
    def unit(self, unit):
        if self.is_ready:
            if self.value.attrs.get(UNITS_KEY, None) is not None:
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
        threshold_min_value: Quantity | None,
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
        else:
            self.is_ready = False
            self._initial_unit = unit
            self._initial_value = float(value)
        self.operator = operator
        self.unit = unit
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
        templates = self.get_metadata_templates(per_coord)
        climatology_bounds: list[str] = self.value.attrs.get("climatology_bounds")
        conf: PercentileTemplateConfig = {
            "climatology_bounds": climatology_bounds,
            "doy_window_width": self.doy_window_width,
            "src_freq": src_freq,
            "operator": self.operator,
            "unit": self.unit,
            "per_coord": per_coord,
            "threshold_min_value": self.threshold_min_value,
            "must_run_bootstrap": must_run_bootstrap,
        }
        conf.update(jinja_scope)
        return {k: jinja_env.from_string(v, globals=conf) for k, v in templates.items()}

    def get_metadata_templates(self, per_coord: DataArray) -> ThresholdMetadata:
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


class BasicThreshold(Threshold):
    @property
    def unit(self) -> str | None:
        return self.value.attrs[UNITS_KEY]

    @unit.setter
    def unit(self, unit):
        if self.value.attrs.get(UNITS_KEY, None) is not None:
            self.value = convert_units_to(self.value, unit)
        self.value.attrs[UNITS_KEY] = unit

    def __init__(
        self,
        operator: Operator | str,
        value: ThresholdValueType,
        unit: str | None = None,
        initial_query: str | None = None,
        threshold_min_value: Quantity | None = None,
        threshold_var_name: str | None = None,
    ):
        self.operator = operator
        self.value = value
        self.unit = unit
        self.is_ready = True
        self.threshold_var_name = threshold_var_name
        self.initial_query = initial_query
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

    def get_metadata_templates(self) -> ThresholdMetadata:
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
        templates = self.get_metadata_templates()
        conf = {
            "operator": self.operator,
            "unit": self.unit,
            "threshold_min_value": self.threshold_min_value,
            "must_run_bootstrap": True,
        }
        if self.value.size > 1:
            conf["min_value"] = np.format_float_positional(
                self.value.min().values[()], 3
            )
            conf["max_value"] = np.format_float_positional(
                self.value.max().values[()], 3
            )
        conf.update(jinja_scope)
        return {k: jinja_env.from_string(v, globals=conf) for k, v in templates.items()}


def _build_period_per(
    studied_data: DataArray,
    per_val: float,
    reference_period: Sequence[str],
    interpolation: QuantileInterpolation,
    only_leap_years: bool,
    percentile_min_value: Quantity | None,
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
            percentiles=[per_val],
            alpha=interpolation.alpha,
            beta=interpolation.beta,
            copy=True,
        ),
        dask="parallelized",
        output_dtypes=[reference.dtype],
        dask_gufunc_kwargs=dict(output_sizes={"percentiles": 1}, allow_rechunk=True),
    )
    computed_per = computed_per.assign_coords(
        percentiles=xr.DataArray([per_val], dims=("percentiles",))
    )
    res = PercentileDataArray.from_da(
        source=computed_per,
        climatology_bounds=build_climatology_bounds(reference),
    )
    return res


def _build_doy_per(
    studied_data: DataArray,
    per_val: float,
    reference_period: Sequence[str],
    interpolation: QuantileInterpolation,
    only_leap_years: bool,
    doy_window_width: int,
    percentile_min_value: Quantity | None,
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
    value = re.findall(r"-?\d+\.?\d*", query)[0]
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
    threshold_min_value: None | str | float | Quantity, default_unit: str | None
) -> Quantity | None:
    if threshold_min_value is None:
        return None
    elif isinstance(threshold_min_value, Quantity):
        return threshold_min_value
    elif isinstance(threshold_min_value, float):
        return Quantity(value=threshold_min_value, units=default_unit)
    elif isinstance(threshold_min_value, str):
        operator, unit, value = _read_string_threshold(threshold_min_value)
        if operator is not None and operator != "" and operator != ">=":
            raise InvalidIcclimArgumentError(
                f"cannot compute threshold_min_value with"
                f" {operator}. You don't need to fill an"
                f" operator for this parameter."
            )
        return Quantity(value=value, units=unit)
    else:
        raise NotImplementedError(
            f"Unknown type '{type(threshold_min_value)}' for" f" `threshold_min_value`."
        )


def _read_input(
    query: str | None = None,
    operator: Operator | str = None,
    value: ThresholdValueType = None,
    unit: str | None = None,
    threshold_min_value: str | float | None = None,
    **kwargs,
) -> ThresholdBuilderInput:
    res = {}
    if isinstance(query, str) and operator is None and value is None and unit is None:
        operator, unit, value = _read_string_threshold(query)
        res.update(dict(initial_query=query))
    min_value = _build_min_value(threshold_min_value, unit)
    if (operator := OperatorRegistry.lookup(operator, no_error=True)) is None:
        operator = OperatorRegistry.REACH
    res.update(
        {
            "operator": operator,
            "unit": unit,
            "value": value,
            "threshold_min_value": min_value,
            **kwargs,
        }
    )
    return res


def _must_build_per_threshold(input: ThresholdBuilderInput) -> bool:
    value = input.get("value")
    unit = input.get("unit", None)
    threshold_var_name = input.get("threshold_var_name", None)
    if isinstance(value, float) and (
        unit == DOY_PERCENTILE_UNIT or unit == PERIOD_PERCENTILE_UNIT
    ):
        return True
    if is_dataset_path(value) or isinstance(value, Dataset):
        thresh_da = _get_dataarray_from_dataset(threshold_var_name, value)
        return PercentileDataArray.is_compatible(thresh_da)
    return False


def must_build_basic_threshold(input: ThresholdBuilderInput) -> bool:
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


def _get_percentile_threshold_conf(
    conf: ThresholdBuilderInput,
) -> PercentileThresholdInput:
    value: DataArray | float | int = conf.get("value")
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
    if is_dataset_path(value) or isinstance(value, Dataset):
        # e.g. build_threshold(">", "thresh*.nc" , "degC")
        thresh_da = _get_dataarray_from_dataset(threshold_var_name, value)
        built_value = _apply_min_value(thresh_da, threshold_min_value)
    elif isinstance(value, DataArray):
        built_value = _apply_min_value(value, threshold_min_value)
    elif is_number_sequence(value) or isinstance(value, (float, int)):
        # e.g. build_threshold(">", [2,3,4], "degC")
        if threshold_min_value is not None:
            raise InvalidIcclimArgumentError(
                "Cannot use threshold_min_value with scalars"
            )
        built_value = DataArray(data=value, attrs={UNITS_KEY: unit})
    else:
        raise NotImplementedError(f"Cannot build threshold from a {type(value)}.")
    if unit is not None:
        built_value = convert_units_to(built_value, unit)
    else:
        built_value = built_value
    return dict(  # noqa
        operator=operator,
        value=built_value,
        unit=unit,
        initial_query=initial_query,
        threshold_var_name=threshold_var_name,
        threshold_min_value=threshold_min_value,
    )


def _apply_min_value(thresh_da: DataArray, min_value: Quantity | None):
    if min_value is not None:
        if min_value.unit is not None:
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
    unit: str,
    threshold_var_name: str,
    reference_period: Sequence[datetime | str],
) -> tuple[DataArray, bool]:
    thresh_da = _get_dataarray_from_dataset(threshold_var_name, value)
    built_value = PercentileDataArray.from_da(
        standardize_percentile_dim_name(thresh_da),
        read_clim_bounds(reference_period, thresh_da),
    )
    if built_value.attrs.get(UNITS_KEY, None) is None:
        built_value.attrs[UNITS_KEY] = unit
    else:
        built_value = convert_units_to(built_value, unit)
    return built_value, DOY_COORDINATE in value.coords
