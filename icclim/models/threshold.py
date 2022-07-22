from __future__ import annotations

import re
from datetime import datetime
from functools import reduce
from typing import Any, Callable, Sequence, Union

import numpy as np
import xarray as xr
from models.logical_link import LOGICAL_AND, LOGICAL_LINK_REGISTRY, LogicalLink
from models.operator import (
    GREATER,
    GREATER_OR_EQUAL,
    LOWER,
    LOWER_OR_EQUAL,
    OPERATOR_REGISTRY,
)
from utils import get_date_to_iso_format
from xarray import DataArray, Dataset
from xclim.core.calendar import build_climatology_bounds, percentile_doy
from xclim.core.units import convert_units_to
from xclim.core.utils import PercentileDataArray, calc_perc

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.constants import VALID_PERCENTILE_DIMENSION
from icclim.models.frequency import Frequency
from icclim.models.operator import Operator
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.pre_processing.input_parsing import (
    _get_threshold_var_name,
    _read_clim_bounds,
    _standardize_percentile_dim_name,
    check_time_range_post_validity,
    check_time_range_pre_validity,
    is_glob_path,
    is_netcdf_path,
    is_zarr_path,
    read_dataset,
)

PERIOD_PERCENTILE_UNIT = "period_per"
DOY_PERCENTILE_UNIT = "doy_per"


class BoundedThresholds:
    # TODO Won't work with bootstrap !
    thresholds: Sequence[Threshold]
    operator: Operator
    link: LogicalLink

    def __init__(
        self,
        thresholds: Sequence[Threshold | str],
        link: str,
        operator: str | None = None,
    ) -> None:
        thresholds = list(
            map(lambda x: x if isinstance(x, Threshold) else Threshold(x), thresholds)
        )
        if operator is None:
            operator = thresholds[0].operator
        operator = OPERATOR_REGISTRY.lookup(operator)
        all_same_op = all(
            map(lambda t: t.operator is None or t.operator == operator, thresholds)
        )
        if not all_same_op:
            raise InvalidIcclimArgumentError(
                "Cannot combine multiple thresholds with " "different operators."
            )
        self.link = LOGICAL_LINK_REGISTRY.lookup(link)
        self.thresholds = thresholds
        self.operator = operator

    def to_threshold(
        self, sampling_frequency: Frequency, study_da: DataArray, unit: str
    ) -> Threshold:
        if self.link is LOGICAL_AND:
            if self.operator is GREATER_OR_EQUAL or self.operator is GREATER:
                combine_op = np.maximum
            elif self.operator is LOWER_OR_EQUAL or self.operator is LOWER:
                combine_op = np.minimum
            else:
                combine_op = lambda x, y: x == y
        else:
            raise NotImplementedError(
                "For now thresholds can only be linked by and keyword"
            )
        converted_thresholds = []
        for t in self.thresholds:
            if isinstance(t.value, Callable):
                thresh = t.value(sampling_frequency, study_da)
                thresh.attrs["units"] = unit
            else:
                thresh = convert_units_to(t.value, unit)
            converted_thresholds.append(thresh)
        return Threshold(
            query=self.operator,
            value=reduce(combine_op, converted_thresholds),
            unit=unit,
        )


def is_dataset_path(query: Sequence | str) -> bool:
    # todo move to input_parsing
    if isinstance(query, (tuple, list)):
        return all(map(lambda q: is_netcdf_path(q), query))
    return is_zarr_path(query) or is_glob_path(query) or is_netcdf_path(query)


def check_threshold_var_name(threshold_var_name) -> None:
    if threshold_var_name is None:
        raise InvalidIcclimArgumentError(
            "When threshold is a Dataset, "
            "threshold_var_name must be given to "
            "find the data_variable in the "
            "dataset."
        )


def is_number_sequence(values) -> bool:
    return isinstance(values, (tuple, list)) and all(
        map(lambda x: isinstance(x, (float, int)), values)
    )


ThresholdValueType = Union[
    str, float, int, Dataset, DataArray, Sequence[Union[float, int, str]], None
]


class Threshold:
    operator: Operator
    value: DataArray | Callable[[Frequency, DataArray], PercentileDataArray]
    threshold_var_name: str | None  # may be guessed if missing
    additional_metadata: list[str]
    # -- Percentile specific properties:
    climatology_bounds: Sequence[str, str] | None  # may be guessed if missing
    reference_period: Sequence[str]
    window: int
    only_leap_years: bool
    interpolation: QuantileInterpolation

    @property
    def unit(self) -> str:
        return self.value.attrs["units"]

    @unit.setter
    def unit(self, unit):
        if self.value.attrs.get("units", None) is not None:
            self.value = convert_units_to(self.value, unit)
        self.value.attrs["units"] = unit

    def __init__(
        self,
        query: str | None | Operator = None,
        value: ThresholdValueType = None,
        unit: str | None = None,
        threshold_var_name: str | None = None,
        climatology_bounds: Sequence[str, str] | None = None,
        window: int = 5,
        only_leap_years: bool = False,
        interpolation: QuantileInterpolation = QuantileInterpolation.MEDIAN_UNBIASED,
        base_period_time_range: Sequence[datetime | str] | None = None,
    ):
        if isinstance(query, str) and value is None and unit is None:
            operator, unit, value = self.read_string_query(query)
        else:
            operator = query
        if is_dataset_path(value) or isinstance(value, Dataset):
            # e.g. Threshold(">", "thresh*.nc" , "degC")
            ds = value if isinstance(value, Dataset) else read_dataset(value)
            check_threshold_var_name(threshold_var_name)
            value = self._read_threshold_DataArray(ds[threshold_var_name])
            value.attrs["units"] = unit
        elif is_number_sequence(value):
            # e.g. Threshold(">", [2,3,4], "degC")
            value = DataArray(
                data=value,
                coords={"threshold": value},
            )
            value.attrs["units"] = unit
        elif unit == DOY_PERCENTILE_UNIT:
            per_value = float(value)
            value = lambda f, da: build_doy_per(
                sampling_frequency=f,
                study_da=da,
                per_val=per_value,
                base_period_time_range=base_period_time_range,
                interpolation=interpolation,
                only_leap_years=only_leap_years,
                window=window,
            )
        elif unit == PERIOD_PERCENTILE_UNIT:
            per_value = float(value)
            value = lambda f, da: build_period_per(
                sampling_frequency=f,
                study_da=da,
                per_val=per_value,
                base_period_time_range=base_period_time_range,
                interpolation=interpolation,
                only_leap_years=only_leap_years,
            )
        elif np.isscalar(value):
            value = DataArray(data=value, coords={"threshold": value})
            value.attrs["units"] = unit
        elif isinstance(value, DataArray):
            value.attrs["units"] = unit
        self.operator = OPERATOR_REGISTRY.lookup(operator)
        self.value = value
        # self.unit = unit
        self.additional_metadata = []
        self.threshold_var_name = threshold_var_name
        self.climatology_bounds = climatology_bounds
        self.window = window
        self.only_leap_years = only_leap_years
        self.interpolation = interpolation
        self.base_period_time_range = base_period_time_range

    def read_string_query(self, query: str):
        value = re.findall(r"-?\d+\.?\d*", query)[0]
        value_index = query.find(value)
        operator = query[0:value_index].strip()
        if value_index < len(query) - 1:
            unit = query[value_index + len(value) :].strip()
        else:
            unit = None
        return operator, unit, float(value)

    def _read_threshold_DataArray(self, thresh_da: DataArray):
        if PercentileDataArray.is_compatible(self.value):
            built_value = PercentileDataArray.from_da(
                _standardize_percentile_dim_name(thresh_da),
                _read_clim_bounds(self.climatology_bounds, thresh_da),
            )
            built_value.attrs["unit"] = self.unit
        else:
            built_value = self.value
            built_value.attrs["unit"] = self.unit
        return built_value

    def get_metadata(self, src_freq: Frequency) -> dict[str, Any]:
        # TODO: [xclim backport] localize/translate these
        if self.value.size == 1:
            res = {
                "standard_name": f"{self.operator.standard_name}_"
                                 f"{self.value.values[()]}"
                                 f"_{self.unit}",
                "long_name": f"{self.operator.long_name} "
                             f"{self.value.values[()]} "
                             f"{self.unit}",
            }
        elif isinstance(self.value, PercentileDataArray):
            percentiles = self.value.coords["percentiles"].values
            if percentiles.size == 1:
                display_pers = (
                    f"{self.operator.long_name} {percentiles[0]}th percentile"
                )
                standard_name = (
                    f"{self.operator.standard_name}_{percentiles[0]}th_percentile"
                )
            else:
                display_pers = self.operator.long_name + str(
                    list(map(lambda x: f"{x}th", percentiles))
                )
                standard_name = f"{self.operator.standard_name}_percentiles"
            window = self.value.attrs.get("window", None)
            # TODO: make specific metadata for doy and period percentiles
            #       (lazy way to detect is `if window!=None then it's doy`)
            bds = self.value.attrs.get("climatology_bounds")
            self.additional_metadata.append(
                f"percentiles were computed over {bds}"
                f" on a {window} {src_freq.units} window"
            )
            res = {
                "standard_name": f"{self.operator.standard_name}_{standard_name}",
                "long_name": f"{self.operator.long_name} {display_pers}",
            }
        elif isinstance(self.value, DataArray):
            if self.value.size < 10:
                display_value = f"{self.value.values}{self.unit}"
            else:
                display_value = (
                    f"values between {self.value.min().values[()]}{self.unit}"
                    f" and {self.value.max().values[()]}{self.unit}"
                )
            res = {
                "standard_name": f"{self.operator.standard_name}_thresholds",
                "long_name": f"{self.operator.long_name} {display_value}",
            }
        else:
            raise NotImplementedError(
                f"Threshold::value must be a DataArray."
                f" It was a {type(self.value)}."
            )
        if len(self.additional_metadata) > 0:
            added_meta = "(" + (", ".join(self.additional_metadata) + ").")
            res.update({"additional_metadata": added_meta})
        res.update({"operator": self.operator})
        return res

    def _is_pint_compatible(self, thresh: str) -> bool:
        return "per" not in thresh


def read_in_file(
    value, climate_var_name, climatology_bounds, conversion_unit, threshold_var_name
) -> DataArray:
    thresh_ds = read_dataset(value, index=None)
    if threshold_var_name is None:
        threshold_var_name = _get_threshold_var_name(thresh_ds, climate_var_name)
    thresh_da = thresh_ds[threshold_var_name]
    if _is_percentile_data(thresh_da):
        res = PercentileDataArray.from_da(
            _standardize_percentile_dim_name(thresh_da),
            _read_clim_bounds(climatology_bounds, thresh_da),
        )
    else:
        if (u := thresh_da.attrs.get("unit", None)) is None:
            thresh_da.attrs["units"] = conversion_unit
            res = thresh_da
        else:
            res = convert_units_to(thresh_da, u)
    return res


def build_period_per(
    per_val: float,
    base_period_time_range,
    interpolation,
    only_leap_years,
    sampling_frequency,
    study_da,
) -> PercentileDataArray:
    reference = _build_reference_da(
        study_da,
        base_period_time_range,
        only_leap_years,
        sampling_frequency,
    )
    #  todo overkill to use apply_ufunc here ?
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


def build_doy_per(
    per_val: float,
    base_period_time_range: Sequence[str],
    interpolation: QuantileInterpolation,
    only_leap_years: bool,
    window: int,
    sampling_frequency: Frequency,
    study_da: DataArray,
) -> PercentileDataArray:
    if base_period_time_range is not None:
        reference = _build_reference_da(
            study_da,
            base_period_time_range,
            only_leap_years,
            sampling_frequency,
        )
    else:
        reference = study_da
    res = percentile_doy(
        arr=reference,
        window=window,
        per=per_val,
        alpha=interpolation.alpha,
        beta=interpolation.beta,
    ).compute()  # "optimization" (diminish dask scheduler workload)
    return res


def _build_reference_da(
    original_da: DataArray,
    base_period_time_range: Sequence[datetime | str] | None,
    only_leap_years: bool,
    sampling_frequency: Frequency,
) -> DataArray:
    da = original_da
    if base_period_time_range:
        check_time_range_pre_validity("base_period_time_range", base_period_time_range)
        base_period_time_range = [
            get_date_to_iso_format(x) for x in base_period_time_range
        ]
        da = original_da.sel(
            time=slice(base_period_time_range[0], base_period_time_range[1])
        )
        check_time_range_post_validity(
            da, original_da, "base_period_time_range", base_period_time_range
        )
    if sampling_frequency.time_clipping is not None:
        da = sampling_frequency.time_clipping(da)
    if only_leap_years:
        da = _reduce_only_leap_years(original_da)
    return da


def _reduce_only_leap_years(da: DataArray) -> DataArray:
    reduced_list = []
    for _, val in da.groupby(da.time.dt.year):
        if val.time.dt.dayofyear.max() == 366:
            reduced_list.append(val)
    if not reduced_list:
        raise InvalidIcclimArgumentError(
            "No leap year in current dataset. Do not use `only_leap_years` parameter."
        )
    return xr.concat(reduced_list, "time")


def _is_percentile_data(da) -> bool:
    return reduce(lambda x, y: x or (y in da.dims), VALID_PERCENTILE_DIMENSION, False)
