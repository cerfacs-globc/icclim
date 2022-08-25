from __future__ import annotations

from datetime import datetime
from functools import partial
from typing import Any, Callable, Sequence, Union

import numpy as np
import xarray as xr
from xarray import DataArray, Dataset
from xclim.core.calendar import build_climatology_bounds, percentile_doy
from xclim.core.units import convert_units_to
from xclim.core.utils import PercentileDataArray, calc_perc

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.constants import (
    DOY_COORDINATE,
    DOY_PERCENTILE_UNIT,
    PERIOD_PERCENTILE_UNIT,
    UNITS_ATTRIBUTE_KEY,
)
from icclim.models.frequency import Frequency
from icclim.models.operator import Operator, OperatorRegistry
from icclim.models.quantile_interpolation import (
    QuantileInterpolation,
    QuantileInterpolationRegistry,
)
from icclim.pre_processing.input_parsing import (
    build_reference_da,
    is_dataset_path,
    read_dataset,
    read_string_threshold,
    read_threshold_DataArray,
)
from icclim.utils import is_number_sequence

ThresholdValueType = Union[
    str, float, int, Dataset, DataArray, Sequence[Union[float, int, str]], None
]


class Threshold:
    """
    - scalar thresh:                               "> 25 ºC"
    - per grid cell thresh:                        "> data.nc"
    - doy percentile threshold:                    "> 98th doy_per"
    - period percentile threshold:                 "> 75th period_per"
    - period percentile threshold with min value:  "> 98th period_per", min_value= "1mm"
    - sequence thresholds (or):                    "> 10 ºC, > 25 ºC"
                                                     thresholds are a new dimension
    """

    operator: Operator
    value: DataArray | Callable[[Frequency, DataArray], PercentileDataArray]
    threshold_var_name: str | None  # may be guessed if missing

    # -- Percentile specific properties:
    reference_period: Sequence[str]
    doy_window_width: int
    only_leap_years: bool
    interpolation: QuantileInterpolation
    threshold_min_value: Threshold

    @property
    def unit(self) -> str | None:
        if isinstance(self.value, Callable):
            return None
        return self.value.attrs[UNITS_ATTRIBUTE_KEY]

    @unit.setter
    def unit(self, unit):
        if not isinstance(self.value, Callable):
            if self.value.attrs.get(UNITS_ATTRIBUTE_KEY, None) is not None:
                self.value = convert_units_to(self.value, unit)
            self.value.attrs[UNITS_ATTRIBUTE_KEY] = unit
            if self.threshold_min_value:
                self.threshold_min_value.unit = unit

    def __init__(
        self,
        query: str | None | Operator = None,
        value: ThresholdValueType = None,
        unit: str | None = None,
        threshold_var_name: str | None = None,
        doy_window_width: int = 5,
        only_leap_years: bool = False,
        interpolation=QuantileInterpolationRegistry.MEDIAN_UNBIASED,
        reference_period: Sequence[datetime | str] | None = None,
        threshold_min_value: str | float | None = None,
    ):
        is_doy_per_threshold = False
        if isinstance(query, str) and value is None and unit is None:
            operator, unit, value = read_string_threshold(query)
            self.initial_query = query
        else:
            operator = query
            self.initial_query = None
        if is_dataset_path(value) or isinstance(value, Dataset):
            # e.g. Threshold(">", "thresh*.nc" , "degC")
            ds = (
                value
                if isinstance(value, Dataset)
                else read_dataset(value, standard_index=None)
            )
            _check_threshold_var_name(threshold_var_name)
            value = read_threshold_DataArray(
                ds[threshold_var_name],
                threshold_min_value=threshold_min_value,
                climatology_bounds=reference_period,
                unit=unit,
            )
            if DOY_COORDINATE in value.coords:
                is_doy_per_threshold = True
        elif is_number_sequence(value):
            # e.g. Threshold(">", [2,3,4], "degC")
            value = DataArray(data=value)
        elif unit == DOY_PERCENTILE_UNIT:
            value = partial(
                build_doy_per,
                per_val=float(value),
                reference_period=reference_period,
                interpolation=interpolation,
                only_leap_years=only_leap_years,
                doy_window_width=doy_window_width,
                percentile_min_value=threshold_min_value,
            )
            is_doy_per_threshold = True
        elif unit == PERIOD_PERCENTILE_UNIT:
            value = partial(
                build_period_per,
                per_val=float(value),
                reference_period=reference_period,
                interpolation=interpolation,
                only_leap_years=only_leap_years,
                percentile_min_value=threshold_min_value,
            )
        elif isinstance(value, (float, int)):
            value = DataArray(data=value)
        elif isinstance(value, DataArray):
            #  nothing to do
            ...
        else:
            raise NotImplementedError(
                f"Threshold could not be built from the {type(value)}"
            )
        self.is_doy_per_threshold = is_doy_per_threshold
        self.operator = (
            OperatorRegistry.lookup(operator, no_error=True) or OperatorRegistry.REACH
        )
        self.value = value
        self.threshold_min_value = (
            Threshold(threshold_min_value) if threshold_min_value else None
        )
        self.unit = unit
        self.threshold_var_name = threshold_var_name
        self.doy_window_width = doy_window_width
        self.only_leap_years = only_leap_years
        self.interpolation = interpolation
        self.reference_period = reference_period

    def __eq__(self, other):
        return (
            isinstance(other, Threshold)
            and self.initial_query == other.initial_query
            and self.doy_window_width == other.doy_window_width
            and self.only_leap_years == other.only_leap_years
            and self.interpolation == other.interpolation
            and self.reference_period == other.reference_period
            and self.unit == other.unit
            and self.threshold_min_value == other.threshold_min_value
        )

    def get_metadata(
        self,
        src_freq: Frequency,
        must_run_bootstrap: bool = False,
        indicator_name: str | None = None,
    ) -> dict[str, Any]:
        # TODO: [xclim backport] localize/translate these with templates
        additional_metadata = []
        if self.value.size == 1:
            res = {
                "standard_name": f"{self.operator.standard_name}"
                f"_threshold",  # not cf
                "long_name": f"{self.operator.long_name}"
                f" {self.value.values[()]}"
                f" {self.unit}",
                "short_name": f"{self.operator.short_name}_threshold",
            }
        elif isinstance(self.value, PercentileDataArray):
            percentiles = self.value.coords[indicator_name + "_percentiles"].values
            bds = self.value.attrs.get("climatology_bounds")
            if self.is_doy_per_threshold:
                if percentiles.size == 1:
                    display_perc = f"{percentiles[0]}th day of year percentile"
                    standard_name = "doy_percentile_threshold"
                    short_name = "doy_per_threshold"
                else:
                    display_perc = str(list(map(lambda x: f"{x}th", percentiles)))
                    standard_name = "_doy_percentile_thresholds"
                    short_name = "_doy_per_thresholds"
                window = self.value.attrs.get("window", "")
                additional_metadata.append(
                    f"day of year percentiles were computed per grid cell, on the {bds}"
                    f" period, with a {window} {src_freq.units} centred window to"
                    f" aggregate values around each day of year"
                )
                if must_run_bootstrap:
                    additional_metadata.append(
                        "the bootstrap algorithm has been applied to compute doy"
                        " percentiles for the period overlapping both the reference"
                        " period and the studied period"
                    )
            else:
                if percentiles.size == 1:
                    display_perc = f"{percentiles[0]}th period percentile"
                    standard_name = "period_percentile_threshold"
                    short_name = "period_per_threshold"
                else:
                    display_perc = (
                        str(list(map(lambda x: f"{x}th", percentiles)))
                        + " period percentiles"
                    )
                    standard_name = "_period_percentile_thresholds"
                    short_name = "period_per_thresholds"
                additional_metadata.append(
                    f"period percentiles were computed per grid cell, on the {bds}"
                    " period"
                )
            res = {
                "standard_name": f"{self.operator.standard_name}_{standard_name}",
                "long_name": f"{self.operator.long_name} {display_perc}",
                "short_name": short_name,
            }
        elif isinstance(self.value, DataArray):
            if self.value.size < 10:
                display_value = f"{self.value.values} {self.unit}"
            else:
                display_value = (
                    f"per grid cell values between"
                    f" {np.format_float_positional(self.value.min().values[()], 3)}"
                    f" {self.unit}"
                    f" and {np.format_float_positional(self.value.max().values[()], 3)}"
                    f" {self.unit}"
                )
            res = {
                "standard_name": f"{self.operator.standard_name}_thresholds",
                "long_name": f"{self.operator.long_name} {display_value}",
                "short_name": f"{self.operator.short_name}_thresholds",
            }
        else:
            raise NotImplementedError(
                f"Threshold::value must be a DataArray. It was a {type(self.value)}."
            )
        if self.threshold_min_value:
            min_t = self.threshold_min_value.get_metadata(src_freq, False)
            additional_metadata.append(
                f"only values {min_t['long_name']} were considered"
            )
        if len(additional_metadata) > 0:
            added_meta = map(lambda s: s.capitalize(), additional_metadata)
            added_meta = "(" + (". ".join(added_meta)) + ")"
            res.update({"additional_metadata": added_meta})
        return res


def _check_threshold_var_name(threshold_var_name: str | None) -> None:
    if threshold_var_name is None:
        raise InvalidIcclimArgumentError(
            "When threshold is a Dataset, "
            "threshold_var_name must be given to "
            "find the data_variable in the "
            "dataset."
        )


def build_period_per(
    per_val: float,
    reference_period: Sequence[str],
    interpolation: QuantileInterpolation,
    only_leap_years: bool,
    studied_data: DataArray,
    percentile_min_value: float | None,
    indicator_name: str,
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
    res = res.rename({"percentiles": indicator_name + "_percentiles"})
    return res


def build_doy_per(
    per_val: float,
    reference_period: Sequence[str],
    interpolation: QuantileInterpolation,
    only_leap_years: bool,
    doy_window_width: int,
    studied_data: DataArray,
    percentile_min_value: float | None,
    indicator_name: str,
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
    res = res.rename({"percentiles": indicator_name + "_percentiles"})
    return res
