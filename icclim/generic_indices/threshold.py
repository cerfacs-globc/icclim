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
from xclim.core.utils import calc_perc

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
    PercentileDataArray,
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
    thresholds: Sequence[Threshold | str, Threshold | str] | None = None,
    logical_link: str | LogicalLink | None = None,
    **kwargs,
) -> BoundedThreshold | PercentileThreshold | BasicThreshold:
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

        # -- Scalar threshold
        scalar_t = build_threshold(">= 30 degC")
        assert isinstance(scalar_t, BasicThreshold)

        # -- Daily percentile threshold
        doy_t = build_threshold(">= 30 doy_per")
        assert isinstance(doy_t, PercentileThreshold)

        # -- Per grid-cell threshold
        grided_t = build_threshold(
            operator=">=", value="path/to/tasmax_thresholds.nc", unit="K"
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
        **kwargs,
    )
    if _must_build_per_threshold(input_thresh):
        return PercentileThreshold(**input_thresh)
    elif _must_build_basic_threshold(input_thresh):
        return BasicThreshold(**input_thresh)
    elif _must_build_bounded_threshold(input_thresh):
        return BoundedThreshold(**input_thresh)
    else:
        raise NotImplementedError(f"Threshold cannot be built from a {type(value)}")


class Threshold(metaclass=abc.ABCMeta):
    """
    Abstract super class for all thresholds.
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
        """
        Shorthand to build a BoundedThreshold from two existing Threshold with a
        "AND" LogicalLink.
        """
        return BoundedThreshold(
            thresholds=[self, other],
            logical_link=LogicalLinkRegistry.LOGICAL_AND,
            initial_query=None,
        )

    def __or__(self, other: Threshold) -> BoundedThreshold:
        """
        Shorthand to build a BoundedThreshold from two existing Threshold with a
        "OR" LogicalLink.
        """
        return BoundedThreshold(
            thresholds=[self, other],
            logical_link=LogicalLinkRegistry.LOGICAL_OR,
            initial_query=None,
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
    Threshold that binds two other thresholds (e.g. "> 95 doy_per AND >= 30 deg_C").

    The logical link must be either "and" or "or".
    """

    left_threshold: Threshold
    right_threshold: Threshold
    logical_link: LogicalLink

    @property
    def unit(self) -> str | None:
        if self.left_threshold.unit == self.right_threshold.unit:
            return self.left_threshold.unit
        else:
            return None

    @unit.setter
    def unit(self, unit):
        self.left_threshold.unit = unit
        self.right_threshold.unit = unit

    def __init__(
        self,
        thresholds: Sequence[Threshold | str | ThresholdBuilderInput],
        logical_link: LogicalLink,
        initial_query: str | None,
        **kwargs,  # noqa
    ):
        if len(thresholds) != 2:
            raise InvalidIcclimArgumentError(
                f"BoundedThreshold can only be built on 2 thresholds, {len(thresholds)}"
                f" were found."
            )
        self.left_threshold = self._build_thresh(thresholds[0])
        self.right_threshold = self._build_thresh(thresholds[1])
        if self.left_threshold == self.right_threshold:
            raise InvalidIcclimArgumentError(
                f"BoundedThreshold must be built on 2 **different** thresholds, here"
                f" both were {self.left_threshold.initial_query}"
            )
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

    def __eq__(self, other: BoundedThreshold) -> bool:
        """
        BoundedThreshold equality is based on the reflexive property of logical links (
        and/or). Thus, the left_threshold of `self` can be either equal to the
        left_threshold or the right_threshold of `other`.
        Same goes for right_threshold of self.

        Parameters
        ----------
        other : BoundedThreshold
            The comparison threshold.

        Returns
        -------
            True if the the comparison threshold `other` is equivalent to `self`.
        """
        return (
            isinstance(other, BoundedThreshold)
            and self.initial_query == other.initial_query
            and (
                self.left_threshold == other.left_threshold
                or self.left_threshold == other.right_threshold
            )
            and (
                self.right_threshold == other.left_threshold
                or self.right_threshold == other.right_threshold
            )
            and self.logical_link == other.logical_link
        )

    def _build_thresh(
        self, thresh_input: Threshold | str | ThresholdBuilderInput
    ) -> Threshold:
        if isinstance(thresh_input, Threshold):
            return thresh_input
        elif isinstance(thresh_input, str):
            return build_threshold(thresh_input)
        else:
            return build_threshold(**thresh_input)

    def _get_metadata_templates(self) -> ThresholdMetadata:
        return EN_THRESHOLD_TEMPLATE["bounded_threshold"]


class PercentileThreshold(Threshold):
    """
    Percentile based threshold (e.g. "<= 10 doy_per").

    The percentiles to be computed are expected to be either:

    * "doy percentiles" (unit: "doy_per"). They are usually used for temperatures
      indices such as the ECAD :ref:`tx90p <ecad_functions_api>`.
      These percentiles are computed per day of year (doy) and by aggregating
      values on the time axis ranged by ``reference_period``, using the
      ``doy_window_width`` parameter to control the time axis window of aggregation.
      The resulting `value` is a DataArray with a "dayofyear" dimension ranging from
      0 to 365 with one value per day of the year.
    * "period percentiles" (unit: "period_per"). They are usually used for liquide
      precipitation indices such as the ECAD :ref:`r75p <ecad_functions_api>`
      or even :ref:`r75ptot <ecad_functions_api>`.
      These percentiles are computed per grid cell on the period ranged by
      ``reference_period``.
      The resulting ``value`` is a DataArray with per grid cell values and no time axis.

    ``is_ready`` becomes True when `prepare` method has been called, the actual
    percentiles are then computed and accessible in ``value`` property.
    Once ``is_ready`` is True, ``unit`` property can be set and will attempt a pint unit
    conversion similar to what is done on ``BasicThreshold``.
    Before that, setting unit has no effect.
    """

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
    def unit(self, unit: str | xr.DataArray | pint.Quantity | pint.Unit):
        if self.is_ready:
            if self.value.attrs.get(UNITS_KEY, None) is not None and unit is not None:
                self._prepared_value = convert_units_to(
                    self._prepared_value, unit, context="hydro"
                )
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
        value: DataArray | float | int | Sequence[float],
        unit: str | None = None,
        doy_window_width: int = DEFAULT_DOY_WINDOW,
        only_leap_years: bool = False,
        interpolation: QuantileInterpolation
        | str = QuantileInterpolationRegistry.MEDIAN_UNBIASED,
        reference_period: Sequence[datetime | str] | None = None,
        threshold_min_value: pint.Quantity | None = None,
        initial_query: str | None = None,
        threshold_var_name: str | None = None,
        **kwargs,  # noqa
    ):
        if is_dataset_path(value) or isinstance(value, Dataset):
            value, is_doy_per_threshold = _build_per_thresh_from_dataset(
                value=value,
                unit=unit,
                threshold_var_name=threshold_var_name,
                reference_period=reference_period,
            )
        else:
            is_doy_per_threshold = unit == DOY_PERCENTILE_UNIT
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
        self.interpolation = QuantileInterpolationRegistry.lookup(interpolation)
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
        if self.threshold_min_value is not None:
            # there is only a threshold_min_value when we are computing > or >=
            thresh = self.threshold_min_value
            thresh = convert_units_to(thresh, per, context="hydro")
            per = per.where(per > thresh, thresh)
        if is_doy_per_threshold:
            threshold_value = resample_doy(per, comparison_data)
        else:
            threshold_value = per
        return op(comparison_data, threshold_value)


class BasicThreshold(Threshold):
    """
    Pint ready simple threshold (e.g. "> 300 K").

    When built, ``value`` is always turned into a ``xarray.DataArray``.
    The ``unit`` property as a setter that will attempt a unit conversion using
    units found in xclim's pint registry.

    The actual unit can be overridden by modify ``value.attrs["units"]`` directly.
    """

    @property
    def unit(self) -> str | None:
        return self.value.attrs[UNITS_KEY]

    @unit.setter
    def unit(self, unit):
        if self.value.attrs.get(UNITS_KEY, None) is not None and unit is not None:
            self.value = convert_units_to(self.value, unit, context="hydro")
        self.value.attrs[UNITS_KEY] = unit

    def __init__(
        self,
        operator: Operator | str,
        value: ThresholdValueType,
        unit: str | None = None,
        initial_query: str | None = None,
        threshold_min_value: pint.Quantity | None = None,
        threshold_var_name: str | None = None,
        **kwargs,  # noqa
    ):
        if (
            is_number_sequence(value) or isinstance(value, (float, int))
        ) and threshold_min_value is not None:
            raise InvalidIcclimArgumentError(
                "Cannot use threshold_min_value with scalars"
            )
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
            built_value = DataArray(
                name="threshold", data=value, attrs={UNITS_KEY: unit}
            )
        else:
            raise NotImplementedError(f"Cannot build threshold from a {type(value)}.")
        if unit is not None:
            built_value = convert_units_to(built_value, unit, context="hydro")
        self.operator = operator
        self.value = built_value
        self.unit = unit
        self.is_ready = True
        self.threshold_var_name = threshold_var_name
        self.initial_query = initial_query
        if unit is not None and (
            threshold_min_value is not None and threshold_min_value.dimensionless
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


def _apply_min_value(thresh_da: DataArray, min_value: pint.Quantity | None):
    if min_value is not None:
        if min_value.dimensionless:
            # We assume min_value use the same unit as thresh_da if it's dimensionless
            min_value = min_value.m
        else:
            min_value = convert_units_to(str(min_value), thresh_da, context="hydro")
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
            built_value = convert_units_to(built_value, unit, context="hydro")
        built_value.attrs[UNITS_KEY] = unit
    return built_value, DOY_COORDINATE in built_value.coords
