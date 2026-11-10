"""Percentile based threshold module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import xarray as xr
from xarray import DataArray, Dataset

from icclim._core.constants import (
    DEFAULT_DOY_WINDOW,
    DOY_COORDINATE,
    DOY_PERCENTILE_UNIT,
    MAX_LEAP_YEAR_DAYS,
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
from icclim._core.model.threshold import Threshold, ThresholdValueType

if TYPE_CHECKING:
    # Standard library
    from collections.abc import Callable, Sequence
    from datetime import datetime

    # Third-party
    import jinja2
    import pint

    # Local
    from icclim._core.model.operator import Operator


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
    * "period percentiles" (unit: "period_per"). They are usually used for liquid
      precipitation indices such as the ECAD :ref:`r75p <ecad_functions_api>`
      or even :ref:`r75ptot <ecad_functions_api>`.
      These percentiles are computed per grid cell over the period defined by
      ``reference_period``.
      The resulting ``value`` is a DataArray with per grid cell values and no time axis.

    ``is_ready`` becomes True when `prepare` method has been called, the actual
    percentiles are then computed and accessible in ``value`` property.
    Once ``is_ready`` is True, ``unit`` property can be set and will attempt a pint unit
    conversion similar to what is done on ``BasicThreshold``.
    Before that, setting unit has no effect.
    """

    reference_period: Sequence[datetime | str] | None
    doy_window_width: int
    only_leap_years: bool
    interpolation: QuantileInterpolation
    initial_value: list[float] | None
    is_doy_per_threshold: bool

    _prepared_value: PercentileDataArray
    _initial_unit: str | None
    _prepare_output_unit: str | None
    _prepare_source_data: DataArray | None

    @property  # type: ignore[override]
    def unit(self) -> str | None:
        """The unit of the threshold."""
        res = None
        if self.is_ready:
            res = self._prepared_value.attrs.get(UNITS_KEY, None)
        else:
            res = self._prepare_output_unit or self._initial_unit
        return res.replace("°C", "degC") if res else None

    @unit.setter
    def unit(self, unit: str | xr.DataArray | pint.Quantity | pint.Unit | None) -> None:
        if self.is_ready:
            if (
                self._prepared_value.attrs.get(UNITS_KEY, None) is not None
                and unit is not None
            ):
                from xclim.core.units import convert_units_to  # noqa: PLC0415

                self._prepared_value = convert_units_to(
                    self._prepared_value,
                    unit,
                    context="hydro",
                )
            self._prepared_value.attrs[UNITS_KEY] = unit
        else:
            self._initial_unit = unit  # type: ignore[assignment]

    @property  # type: ignore[override]
    def value(self) -> PercentileDataArray:  # type: ignore[override]
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
        if is_dataset_path(cast("Any", value)) or isinstance(value, Dataset):
            value, is_doy_per_threshold = _build_per_thresh_from_dataset(
                value=value,
                unit=unit,
                threshold_var_name=cast("str", threshold_var_name),
                reference_period=cast("Sequence[datetime | str]", reference_period),
            )
        else:
            is_doy_per_threshold = unit == DOY_PERCENTILE_UNIT
        if isinstance(value, DataArray):
            self.prepare = cast("Any", None)  # type: ignore[method-assign]
            self._prepared_value = PercentileDataArray.from_da(value)
            self.is_ready = True
            self._initial_unit = None
            self.initial_value = None
            self.unit = self._prepared_value.attrs[UNITS_KEY]
        else:
            self.is_ready = False
            self._initial_unit = unit
            if isinstance(value, (float, int)):
                self.initial_value = [float(value)]
            elif isinstance(value, (list, tuple)):
                self.initial_value = [float(x) for x in value]
            else:
                self.initial_value = None
            self.unit = unit
        self.operator = operator
        self.threshold_var_name = threshold_var_name
        self.initial_query = initial_query
        self.threshold_min_value = threshold_min_value
        self.reference_period = reference_period
        self.doy_window_width = doy_window_width
        self.only_leap_years = only_leap_years
        self.interpolation = QuantileInterpolationRegistry.lookup(interpolation)
        self._prepare_output_unit = None
        self._prepare_source_data = None
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
                per_val=cast("Sequence[float]", self.initial_value),
                reference_period=cast("Sequence[str]", self.reference_period),
                interpolation=self.interpolation,
                only_leap_years=self.only_leap_years,
                doy_window_width=self.doy_window_width,
                percentile_min_value=self.threshold_min_value,
            )
        elif self._initial_unit == PERIOD_PERCENTILE_UNIT:
            prepared_data = _build_period_per(
                studied_data=studied_data,
                per_val=cast("Sequence[float]", self.initial_value),
                reference_period=cast("Sequence[str]", self.reference_period),
                interpolation=self.interpolation,
                only_leap_years=self.only_leap_years,
                percentile_min_value=self.threshold_min_value,
            )
        else:
            msg = f"Unknown percentile unit '{self._initial_unit}'."
            raise NotImplementedError(msg)
        # This rechunk is a graph-stabilization boundary for percentile_doy.
        # Preserving its generated chunks causes missing-dependency failures in
        # supported xarray/Dask combinations, even though source chunks are safe
        # to preserve during ordinary input preparation.
        self._prepared_value = prepared_data.chunk("auto")
        self.is_ready = True
        if self._prepare_output_unit is not None:
            self.unit = self._prepare_output_unit

    def set_prepare_context(
        self,
        studied_data: DataArray,
        conversion_unit: str | None,
    ) -> None:
        self._prepare_source_data = studied_data
        self._prepare_output_unit = conversion_unit

    def ensure_ready(self, comparison_data: DataArray | None = None) -> None:
        if self.is_ready:
            return
        source = (
            self._prepare_source_data
            if self._prepare_source_data is not None
            else comparison_data
        )
        if source is None:
            msg = "PercentileThreshold cannot be prepared without source data."
            raise RuntimeError(msg)
        self.prepare(source)

    def climatology_bounds(self, comparison_data: DataArray | None = None) -> list[str]:
        if self.is_ready:
            return self.value.attrs["climatology_bounds"]
        source = (
            self._prepare_source_data
            if self._prepare_source_data is not None
            else comparison_data
        )
        if source is None:
            msg = "PercentileThreshold cannot infer climatology bounds without source data."
            raise RuntimeError(msg)
        reference = build_reference_da(
            source,
            cast("Sequence[str]", self.reference_period),
            self.only_leap_years,
            self.threshold_min_value,
        )
        from xclim.core.calendar import build_climatology_bounds  # noqa: PLC0415

        return build_climatology_bounds(reference)

    def percentile_coord(self) -> DataArray:
        if self.is_ready:
            return self.value.coords["percentiles"]
        if self.initial_value is None:
            msg = "PercentileThreshold must have a percentile value."
            raise RuntimeError(msg)
        return xr.DataArray(
            self.initial_value,
            dims=["percentiles"],
            coords={"percentiles": self.initial_value},
        )

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

    def __hash__(self) -> int:
        """Return the hash of the threshold."""
        return hash(
            (
                self.operator,
                self.initial_query,
                self.doy_window_width,
                self.only_leap_years,
                self.interpolation,
                tuple(self.reference_period) if self.reference_period else None,
                self.unit,
                self.threshold_min_value,
            )
        )

    # noinspection PyMethodOverriding
    # (reason: with * and **kwargs we can have a different signature while still
    # being liskov proof)
    def format_metadata(
        self,
        *,
        jinja_scope: dict[str, Any],
        jinja_env: jinja2.Environment,
        **kwargs,
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
        **kwargs
            Additional keyword arguments, ignored for compatibility with other
            `format_metadata` methods.
            src_freq : Frequency
                The frequency of the source data.
            must_run_bootstrap : bool, optional
                Whether to run bootstrap, by default False.

        Returns
        -------
        ThresholdMetadata
            The metadata for the threshold.
        """
        src_freq = kwargs.get("src_freq")
        must_run_bootstrap = kwargs.get("must_run_bootstrap", False)
        per_coord = self.percentile_coord()
        templates = self._get_metadata_templates(per_coord)
        climatology_bounds = self.climatology_bounds()
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
        conf.update(jinja_scope)  # type: ignore[typeddict-item]
        return cast(
            "ThresholdMetadata",
            {
                k: cast(
                    "str",
                    jinja_env.from_string(
                        cast("str", v), globals=cast("dict[str, Any]", conf)
                    ).render(),
                )
                for k, v in templates.items()
            },
        )

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
        op_func = (
            override_op
            if override_op is not None
            else cast("Operator", self.operator).compute
        )
        if self.is_ready:
            return self._per_compute(
                comparison_data,
                self.value,
                op_func,
                self.is_doy_per_threshold,
                cast("str", kwargs.get("freq", "")),
                bootstrap=kwargs.get("bootstrap", False),
            )
        self.ensure_ready(comparison_data)
        return self._per_compute(
            comparison_data,
            self.value,
            op_func,
            self.is_doy_per_threshold,
            cast("str", kwargs.get("freq", "")),
            bootstrap=kwargs.get("bootstrap", False),
        )

    def _get_metadata_templates(self, per_coord: DataArray) -> ThresholdMetadata:
        if self.is_doy_per_threshold:
            if per_coord.size == 1:
                return EN_THRESHOLD_TEMPLATE["single_doy_percentile"]
            return EN_THRESHOLD_TEMPLATE["multiple_doy_percentiles"]
        if per_coord.size == 1:
            return EN_THRESHOLD_TEMPLATE["single_period_percentile"]
        return EN_THRESHOLD_TEMPLATE["multiple_period_percentiles"]

    def _per_compute(
        self,
        comparison_data: xr.DataArray,
        per: xr.DataArray,
        op: Callable[[DataArray, DataArray], DataArray],
        is_doy_per_threshold: bool,
        freq: str,
        bootstrap: bool,
    ) -> DataArray:
        from xclim.core.bootstrapping import percentile_bootstrap  # noqa: PLC0415

        @percentile_bootstrap
        def __per_compute(
            da: xr.DataArray,
            per: xr.DataArray,
            op: Callable[[DataArray, DataArray], DataArray],
            is_doy_per_threshold: bool,
            freq: str,  # noqa: ARG001
            bootstrap: bool,  # noqa: ARG001
        ) -> DataArray:
            comparison_floor = None
            if self.threshold_min_value is not None:
                thresh = self.threshold_min_value
                from xclim.core.units import convert_units_to  # noqa: PLC0415

                comparison_floor = convert_units_to(thresh, da, context="hydro")
                thresh = convert_units_to(thresh, per, context="hydro")
                per = per.where(per > thresh, thresh)
            if is_doy_per_threshold:
                threshold_value = _resample_doy_exact(per, da)
            else:
                threshold_value = per
            result = op(da, threshold_value)
            if comparison_floor is not None:
                result = result.where(da >= comparison_floor, False)
            if "units" not in result.attrs and "units" in da.attrs:
                result.attrs["units"] = da.attrs["units"]
            return result

        return __per_compute(
            comparison_data,
            per,
            op,
            is_doy_per_threshold,
            freq,
            bootstrap,
        )


def _compute_per(
    per_val: float | Sequence[float], alpha: float, beta: float, study: DataArray
) -> PercentileDataArray:
    from collections.abc import Sequence  # noqa: PLC0415

    from xclim.core.calendar import build_climatology_bounds  # noqa: PLC0415
    from xclim.core.utils import calc_perc  # noqa: PLC0415

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
        dask_gufunc_kwargs={
            "output_sizes": {
                "percentiles": len(per_val) if isinstance(per_val, Sequence) else 1
            },
            "allow_rechunk": True,
        },
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
    return _circular_percentile_doy(
        arr=reference,
        window=doy_window_width,
        per=per_val,
        alpha=interpolation.alpha,
        beta=interpolation.beta,
    )


def _circular_percentile_doy(
    arr: DataArray,
    window: int,
    per: Sequence[float],
    alpha: float,
    beta: float,
) -> DataArray:
    """Compute calendar-day percentiles with a window wrapping year boundaries."""
    import numpy as np  # noqa: PLC0415
    import pandas as pd  # noqa: PLC0415
    from xclim.core.calendar import build_climatology_bounds  # noqa: PLC0415
    from xclim.core.formatting import update_history  # noqa: PLC0415
    from xclim.core.utils import calc_perc  # noqa: PLC0415

    left = window // 2
    right = window - left - 1
    parts = []
    if left:
        parts.append(arr.isel(time=slice(-left, None)))
    parts.append(arr)
    if right:
        parts.append(arr.isel(time=slice(0, right)))
    padded = xr.concat(parts, dim="time")
    rolling = padded.rolling(min_periods=1, center=True, time=window).construct(
        "window"
    )
    rolling = rolling.isel(time=slice(left, left + arr.sizes["time"]))

    coordinates = xr.Coordinates.from_pandas_multiindex(
        pd.MultiIndex.from_arrays(
            (rolling.time.dt.year.values, rolling.time.dt.dayofyear.values),
            names=("year", "dayofyear"),
        ),
        "time",
    )
    rolling = rolling.drop_vars("time").assign_coords(coordinates)
    stacked = rolling.unstack("time").stack(stack_dim=("year", "window"))
    if (
        stacked.chunks is not None
        and len(stacked.chunks[stacked.get_axis_num("stack_dim")]) > 1
    ):
        time_chunk_count = len(arr.chunks[arr.get_axis_num("time")])
        doy_chunk_size = np.ceil(len(stacked.dayofyear) / (window * time_chunk_count))
        stacked = stacked.chunk({"stack_dim": -1, "dayofyear": doy_chunk_size})

    result = xr.apply_ufunc(
        calc_perc,
        stacked,
        input_core_dims=[["stack_dim"]],
        output_core_dims=[["percentiles"]],
        keep_attrs=True,
        kwargs={"percentiles": per, "alpha": alpha, "beta": beta, "copy": True},
        dask="parallelized",
        output_dtypes=[stacked.dtype],
        dask_gufunc_kwargs={"output_sizes": {"percentiles": len(per)}},
    ).assign_coords(percentiles=xr.DataArray(per, dims=("percentiles",)))
    if result.dayofyear.max() == MAX_LEAP_YEAR_DAYS:
        result = _adjust_doy_calendar_exact(
            result.sel(dayofyear=(result.dayofyear < MAX_LEAP_YEAR_DAYS)), arr
        )
    result.attrs.update(arr.attrs.copy())
    result.attrs["climatology_bounds"] = build_climatology_bounds(arr)
    result.attrs["window"] = window
    result.attrs["alpha"] = alpha
    result.attrs["beta"] = beta
    result.attrs["history"] = update_history(
        "percentile_doy with a circular calendar-day window",
        arr,
        new_name="per",
    )
    return result.rename("per")


def _adjust_doy_calendar_exact(source: DataArray, target: DataArray) -> DataArray:
    """
    Interpolate calendar-day percentiles to the day-of-year range of `target`.

    Same result as `xclim.core.calendar.adjust_doy_calendar`, but the linear
    interpolation uses the numerically stable form `a + (b - a) * gamma` (also used
    by the compiled bootstrap kernels). `DataArray.interp` goes through SciPy, whose
    arithmetic is not exact between equal neighbours depending on its version:
    10.0 can become 10.000000000000002, which turns observations tying with the
    threshold into spurious exceedances.
    """
    import numpy as np  # noqa: PLC0415
    from xclim.core.calendar import get_calendar, max_doy  # noqa: PLC0415

    max_target_doy = int(target.time.dt.dayofyear.max())
    min_target_doy = int(target.time.dt.dayofyear.min())
    if source.dayofyear.max() == max_doy[get_calendar(target)]:
        return source
    if max_target_doy == min_target_doy:
        return source
    da = source.chunk({"dayofyear": -1}) if source.chunks is not None else source
    filled = da.interpolate_na(dim="dayofyear")
    size = filled.sizes["dayofyear"]
    new_doys = np.arange(min_target_doy, max_target_doy + 1)
    position = (
        (new_doys - min_target_doy) * (size - 1.0) / (max_target_doy - min_target_doy)
    )
    lower = np.minimum(np.floor(position).astype(int), max(size - 2, 0))
    gamma = position - lower
    upper = np.minimum(lower + 1, size - 1)

    left = filled.isel(dayofyear=lower).assign_coords(dayofyear=new_doys)
    right = filled.isel(dayofyear=upper).assign_coords(dayofyear=new_doys)
    weight = xr.DataArray(gamma, dims="dayofyear", coords={"dayofyear": new_doys})
    diff = right - left
    result = xr.where(
        weight >= 0.5,  # noqa: PLR2004
        right - diff * (1.0 - weight),
        left + diff * weight,
        keep_attrs=True,
    )
    result = result.transpose(*source.dims)
    result.attrs = dict(source.attrs)
    return result


def _resample_doy_exact(doy: DataArray, arr: DataArray) -> DataArray:
    """
    Give each day of `arr` the value of the calendar-day thresholds `doy`.

    Same result as `xclim.core.calendar.resample_doy`, but the calendar adjustment is
    `_adjust_doy_calendar_exact`: xclim goes through `DataArray.interp`, whose SciPy
    arithmetic is not exact between equal neighbours (SciPy 1.18.1), so a threshold of
    10.0 could become 10.000000000000002 and change the exceedance counts.
    """
    if "dayofyear" not in doy.coords:
        msg = "Source should have `dayofyear` coordinates."
        raise AttributeError(msg)
    adjusted = _adjust_doy_calendar_exact(doy, arr)
    out = adjusted.rename(dayofyear="time").reindex(time=arr.time.dt.dayofyear)
    out["time"] = arr.time
    return out


def _build_per_thresh_from_dataset(
    value: ThresholdValueType,
    unit: str | None,
    threshold_var_name: str,
    reference_period: Sequence[datetime | str],
) -> tuple[DataArray, bool]:
    if (isinstance(value, (str, Dataset)) and is_dataset_path(value)) or isinstance(
        value, Dataset
    ):
        v = cast("Dataset | str", value)
        thresh_da = get_dataarray_from_dataset(threshold_var_name, v)
    elif isinstance(value, DataArray):
        thresh_da = value
    else:
        msg = f"Cannot build threshold from a {type(value)}."
        raise NotImplementedError(msg)
    built_value = PercentileDataArray.from_da(
        standardize_percentile_dim_name(thresh_da),
        read_clim_bounds(reference_period, thresh_da),
    )
    if unit is not None:
        if built_value.attrs.get(UNITS_KEY, None) is not None:
            from xclim.core.units import convert_units_to  # noqa: PLC0415

            built_value = convert_units_to(built_value, unit, context="hydro")
        built_value.attrs[UNITS_KEY] = unit
    return built_value, DOY_COORDINATE in built_value.coords
