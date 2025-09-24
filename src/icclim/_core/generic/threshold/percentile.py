"""Percentile based threshold module."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import xarray as xr
from xarray import DataArray, Dataset
from xclim.core.bootstrapping import percentile_bootstrap
from xclim.core.calendar import build_climatology_bounds, percentile_doy, resample_doy
from xclim.core.units import convert_units_to
from xclim.core.utils import calc_perc

from icclim._core.constants import (
    DEFAULT_DOY_WINDOW,
    DOY_COORDINATE,
    DOY_PERCENTILE_UNIT,
    PERIOD_PERCENTILE_UNIT,
    UNITS_KEY,
)
from icclim._core.generic.threshold.threshold_templates import (
    EN_THRESHOLD_TEMPLATE,
    PercentileTemplateConfig,
    ThresholdMetadata,
)
from icclim._core.input_parsing import (
    PercentileDataArray,
    build_reference_da,
    get_dataarray_from_dataset,
    is_dataset_path,
    read_clim_bounds,
    standardize_percentile_dim_name,
)
from icclim._core.model.quantile_interpolation import (
    QuantileInterpolation,
    QuantileInterpolationRegistry,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    import jinja2
    import pint

    from icclim._core.model.operator import Operator
    from icclim.frequency import Frequency

from typing import TYPE_CHECKING

from icclim._core.model.threshold import Threshold, ThresholdValueType


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
    initial_value: list[float] | None
    is_doy_per_threshold: bool

    _prepared_value: PercentileDataArray
    _initial_unit: str | None

    @property
    def unit(self) -> str | None:
        """The unit of the threshold."""
        if self.is_ready:
            return self._prepared_value.attrs[UNITS_KEY]
        return self._initial_unit

    @unit.setter
    def unit(self, unit: str | xr.DataArray | pint.Quantity | pint.Unit) -> None:
        if self.is_ready:
            if self.value.attrs.get(UNITS_KEY, None) is not None and unit is not None:
                self._prepared_value = convert_units_to(
                    self._prepared_value,
                    unit,
                    context="hydro",
                )
            self.value.attrs[UNITS_KEY] = unit

    @property
    def value(self) -> PercentileDataArray:
        """
        The computed percentile threshold.

        Raises
        ------
        RuntimeError
            If the threshold is not ready (prepare has not been called).
        """
        if self.is_ready:
            return self._prepared_value
        msg = (
            "Property `value` is not ready. For PercentileDataArray,"
            " you must call `.prepare` first and fill `studied_data`"
            " parameter in order to prepare `value`."
        )
        raise RuntimeError(msg)

    def __init__(
        self,
        operator: str | Operator,
        value: DataArray | float | Sequence[float],
        unit: str | None = None,
        doy_window_width: int = DEFAULT_DOY_WINDOW,
        only_leap_years: bool = False,
        interpolation: QuantileInterpolation
        | str = QuantileInterpolationRegistry.MEDIAN_UNBIASED,
        reference_period: Sequence[datetime | str] | None = None,
        threshold_min_value: pint.Quantity | None = None,
        initial_query: str | None = None,
        threshold_var_name: str | None = None,
        **kwargs,  # noqa: ARG002
    ) -> None:
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
            self.initial_value = None
            self.unit = self._prepared_value.attrs[UNITS_KEY]
        else:
            self.is_ready = False
            self._initial_unit = unit
            if not isinstance(value, list):
                value = [value]
            self.initial_value = [float(x) for x in value]
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
        """
        Prepare the data for calculating percentiles.

        Parameters
        ----------
        studied_data : DataArray
            The input data to be prepared.

        Raises
        ------
        NotImplementedError
            If the percentile unit is unknown.

        Returns
        -------
        None
        """
        if self._initial_unit == DOY_PERCENTILE_UNIT:
            prepared_data = _build_doy_per(
                studied_data=studied_data,
                per_val=self.initial_value,
                reference_period=self.reference_period,
                interpolation=self.interpolation,
                only_leap_years=self.only_leap_years,
                doy_window_width=self.doy_window_width,
                percentile_min_value=self.threshold_min_value,
            )
        elif self._initial_unit == PERIOD_PERCENTILE_UNIT:
            prepared_data = _build_period_per(
                studied_data=studied_data,
                per_val=self.initial_value,
                reference_period=self.reference_period,
                interpolation=self.interpolation,
                only_leap_years=self.only_leap_years,
                percentile_min_value=self.threshold_min_value,
            )
        else:
            msg = f"Unknown percentile unit '{self._initial_unit}'."
            raise NotImplementedError(msg)
        self._prepared_value = prepared_data.chunk("auto")
        self.is_ready = True

    def __eq__(self, other: object) -> bool:
        """
        Compare two PercentileThreshold objects for equality.

        Parameters
        ----------
        other : object
            The object to compare with.

        Returns
        -------
        bool
            True if the objects are equal, False otherwise.
        """
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
        **kwargs,  # noqa: ARG002
    ) -> ThresholdMetadata:
        """
        Generate the metadata for the threshold.

        These metadata are used to fill the generic template.

        Parameters
        ----------
        jinja_scope : dict
            The jinja scope, it contains the variables to be used in the jinja template.
        jinja_env : jinja2.Environment
            The jinja environment, it contains the jinja rendering engine.
        src_freq : Frequency
            The frequency of the source data.
        must_run_bootstrap : bool, optional
            Whether to run bootstrap, by default False.

        Returns
        -------
        ThresholdMetadata
            The metadata for the threshold.
        """
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
        """
        Compute the percentile threshold.

        Parameters
        ----------
        comparison_data : xr.DataArray
            The data array to compare with the threshold.
        override_op : Callable[[DataArray, DataArray], DataArray] | None, optional
            An optional override operator to use instead of the default operator.
        **kwargs
            Additional keyword arguments.
            The `freq` parameter is used to specify the frequency of the data.
            The `bootstrap` parameter is used to specify whether to run bootstrap.

        Returns
        -------
        DataArray
            The computed percentile threshold.

        Raises
        ------
        RuntimeError
            If the PercentileThreshold is not ready. You must first call `.prepare`
            with a `studied_data` parameter in order to prepare the threshold
            for computation.
        """
        op = override_op if override_op is not None else self.operator
        if self.is_ready:
            return self._per_compute(
                comparison_data,
                self.value,
                op,
                self.is_doy_per_threshold,
                kwargs.get("freq", None),
                kwargs.get("bootstrap", False),
            )
        msg = (
            "This PercentileThreshold is not ready. You must first call `.prepare`"
            " with a `studied_data` parameter in order to prepare the threshold"
            " for computation."
        )
        raise RuntimeError(msg)

    def _get_metadata_templates(self, per_coord: DataArray) -> ThresholdMetadata:
        if self.is_doy_per_threshold:
            if per_coord.size == 1:
                return EN_THRESHOLD_TEMPLATE["single_doy_percentile"]
            return EN_THRESHOLD_TEMPLATE["multiple_doy_percentiles"]
        if per_coord.size == 1:
            return EN_THRESHOLD_TEMPLATE["single_period_percentile"]
        return EN_THRESHOLD_TEMPLATE["multiple_period_percentiles"]

    @percentile_bootstrap
    def _per_compute(
        self,
        comparison_data: xr.DataArray,
        per: xr.DataArray,
        op: Callable[[DataArray, DataArray], DataArray],
        is_doy_per_threshold: bool,
        freq: str,  # noqa: ARG002 used by @percentile_bootstrap
        bootstrap: bool,  # noqa: ARG002 used by @percentile_bootstrap
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


def _compute_per(
    per_val: float, alpha: float, beta: float, study: DataArray
) -> PercentileDataArray:
    computed_per = xr.apply_ufunc(
        calc_perc,
        study,
        input_core_dims=[["time"]],
        output_core_dims=[["percentiles"]],
        keep_attrs=True,
        kwargs={
            "percentiles": per_val,
            "alpha": alpha,
            "beta": beta,
            "copy": True,
        },
        dask="parallelized",
        output_dtypes=[study.dtype],
        dask_gufunc_kwargs={"output_sizes": {"percentiles": 1}, "allow_rechunk": True},
    )
    computed_per = computed_per.assign_coords(
        percentiles=xr.DataArray(per_val, dims=("percentiles",)),
    )
    return PercentileDataArray.from_da(
        source=computed_per,
        climatology_bounds=build_climatology_bounds(study),
    )


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
    return _compute_per(per_val, interpolation.alpha, interpolation.beta, reference)


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
    return percentile_doy(
        arr=reference,
        window=doy_window_width,
        per=per_val,
        alpha=interpolation.alpha,
        beta=interpolation.beta,
    ).compute()  # "optimization" (diminish dask scheduler workload)


def _build_per_thresh_from_dataset(
    value: ThresholdValueType,
    unit: str | None,
    threshold_var_name: str,
    reference_period: Sequence[datetime | str],
) -> tuple[DataArray, bool]:
    thresh_da = get_dataarray_from_dataset(threshold_var_name, value)
    built_value = PercentileDataArray.from_da(
        standardize_percentile_dim_name(thresh_da),
        read_clim_bounds(reference_period, thresh_da),
    )
    if unit is not None:
        if built_value.attrs.get(UNITS_KEY, None) is not None:
            built_value = convert_units_to(built_value, unit, context="hydro")
        built_value.attrs[UNITS_KEY] = unit
    return built_value, DOY_COORDINATE in built_value.coords
